"""
Cleanup script for Eloqua Custom Data Object (CDO) tables.
The main function, 'visor_eloqua_cdo_cleanup', uses file 'visor_eloqua_cdo_cleanup.json' 
    which contains the CDOs to be cleaned and parameters for each CDO.
Flow:
    Pull from the specified JSON file what criteria to filter the records by.
    Starting from the earliest timeframe specified in the criteria, 
            pull records in week increments until the end of the specified time 
            or no records are returned.
        For each pull of CDO records, process the records:
            - Filter out the records that do not meet the criteria.
            - Change the data status of the remaining records to "markedForDeletion".
            - Return those changes to Eloqua.
    End. The new data status will then be used by a Program Canvas in Eloqua to delete the CDO records.
        (https://REDACTED.eloqua.com/Main.aspx#programs&id=40)

This script will only run on production and on Sunday mornings between 00:00 and 01:00.
The program canvas (40) is configured to wait a week before deleting the records.

Story US000
Change report: https://docs.google.com/spreadsheets/d/1GOs3ZzJ_6FVq1eubK4hHYkA_0Ccsa3yOHJFnb3QcaGA
Created 000-08-17 19:07
Revised 000-06-14 07:05
"""
from datetime import datetime
from datetime import timedelta
import os
from pprint import pprint
import time
from json import load
from dateutil.relativedelta import relativedelta
import pytz
from pyeloqua import Bulk
from function_defintions_visor import format_text_for_vars, prometheus_registry_prep


try:
    OPENSHIFT_BUILD_REFERENCE = os.environ['OPENSHIFT_BUILD_REFERENCE']
except (KeyError):
    OPENSHIFT_BUILD_REFERENCE = "missing"

try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except (KeyError):
    PRINT_OUTPUT = False
# PRINT_OUTPUT = True #devonly

CDOS_TO_CLEANUP = load(open('visor_eloqua_cdo_cleanup.json', 'r'))
for KEY, ITEM in CDOS_TO_CLEANUP.items():
    ITEM['var_name'] = format_text_for_vars(ITEM['name'])

TIMEZONE = pytz.timezone("America/New_York")

NEW_DATA_STATUS = "markedForDeletion"


def visor_eloqua_cdo_cleanup():
    """
    Steps through the criteria
    """

    # only run on prod and on Sunday mornings between 00:00 and 01:00
    now_raleigh = datetime.now(TIMEZONE)
    # if os.environ['PROJECT_NAME'] != "visor":
    #     if PRINT_OUTPUT:
    #         print("Not on production server.")
    #     return
    if PRINT_OUTPUT:
        print('int(now_raleigh.weekday())', int(now_raleigh.weekday()))
        print("int(now_raleigh.strftime('%H'))", int(now_raleigh.strftime('%H')))
    if (int(now_raleigh.weekday()) != 6
        or int(now_raleigh.strftime('%H')) > 1
        ):
        if PRINT_OUTPUT:
            print("Not Sunday (day 6) morning between 00:00 and 01:00.")
        return


    metric_list = []

    # Split by each CDO
    for key, item in CDOS_TO_CLEANUP.items():
        if PRINT_OUTPUT:
            print("Processing", key)
        cdos_marked_for_deletion = set()
        
        # Split by each criteria
        for key2, item2 in item["criteria_to_delete"].items():
            if PRINT_OUTPUT:
                print("Processing criteria", key2)
            
            # pull data
            now_raleigh = datetime.now(TIMEZONE)
            days_to_chunk = 7
            pull_date_newest_final = now_raleigh + timedelta(-item2['day_range']['days_ago_oldest'])
            pull_date_newest_next = now_raleigh + timedelta(-item2['day_range']['days_ago_newest'])
            pull_date_oldest_next = pull_date_newest_next + timedelta(-days_to_chunk)
            more_days = True
            while more_days:
                cdo_fields = item['fields']
                cdo_fields.append(item['data_status_field'])
                data = request_cdo_records(
                    cdo_id=key, 
                    cdo_name_as_var=item['var_name'], 
                    cdo_fields=cdo_fields, 
                    date_oldest=pull_date_oldest_next, 
                    date_newest=pull_date_newest_next
                    )
                if data:
                    # analyze data, if there is criteria beyond date range
                    try:
                        data_to_delete = mark_local_for_deletion(
                            all_cdo_records=data, 
                            filter_criteria=item2['other_criteria']
                            )
                    except:
                        data_to_delete = data

                    # Mark for deletion 
                    record_ids = [row["DataCardIDExt"] for row in data_to_delete if row[item['data_status_field']] != NEW_DATA_STATUS]
                    if OPENSHIFT_BUILD_REFERENCE == "develop":
                        if PRINT_OUTPUT:
                            print("Don't run if created from develop branch.")
                    else:
                        mark_eloqua_for_deletion(
                            record_ids=record_ids, 
                            data_status_field=item["data_status_field"], 
                            cdo_id=key, 
                            cdo_name_as_var=item['var_name']
                            )

                    #record count marked for reporting
                    for row in record_ids:
                        cdos_marked_for_deletion.add(row)

                else:
                    days_to_chunk = days_to_chunk * 2  # this will speed up the process at the end of the CDO but not yet the days_ago_oldest
                pull_date_newest_next = pull_date_oldest_next
                pull_date_oldest_next = pull_date_newest_next + timedelta(-days_to_chunk)
                if pull_date_newest_next < pull_date_newest_final:
                    more_days = False

        cdos_marked_for_deletion_cnt = len(cdos_marked_for_deletion)
        metric_desc = "Count of CDO records that have been marked for deletion."
        metric_name = item['var_name']
        metric_value = cdos_marked_for_deletion_cnt
        metric_list.append({'metric_name': metric_name, 'metric_desc': metric_desc, 'metric_value': metric_value})

    # prometheus_registry = prometheus_registry_prep(metric_list=metric_list, job_name=os.path.basename(__file__))
    # return prometheus_registry
    return metric_list


def criteria_if(filter_row, records):
    """Determines operator for filter"""
    if filter_row[0] == "between":
        records_matching = criteria_between(filter_row=filter_row[1], records=records)
    elif filter_row[0] == "and":
        records_matching = criteria_and(filter_row=filter_row[1], records=records)
    elif filter_row[0] == "or":
        records_matching = criteria_or(filter_row=filter_row[1], records=records)
    else:
        records_matching = []
        for record in records:
            if record[filter_row[0]] == filter_row[1]:
                records_matching.append(record)
    return records_matching


def criteria_between(filter_row, records):
    """Filters on records between the supplied dates"""
    records_matching = []
    for cdo_row in records:
        if cdo_row[filter_row[0][0]] > filter_row[0][1] \
        and cdo_row[filter_row[1][0]] < filter_row[1][1]:
            records_matching.append(cdo_row)
    return records_matching


def criteria_and(filter_row, records):
    """Filters records then passes the filtered records to the next filter"""
    records_matching = records
    for filter_row_row in filter_row:
        records_matching = criteria_if(filter_row=filter_row_row, records=records_matching)
    return records_matching


def criteria_or(filter_row, records):
    """Filters records and filters records then adds the two results upon each other"""
    records_matching = []
    for filter_row in filter_row:
        records_matching.extend(criteria_if(filter_row=filter_row, records=records))
    return records_matching


def request_cdo_records(cdo_id, cdo_name_as_var, cdo_fields, date_oldest, date_newest):
    """
    Pulls records of a CDO
    """
    bulk_definition = Bulk(company=os.environ['ELOQUA_COMPANY']
                           , username=os.environ['ELOQUA_USER']
                           , password=os.environ['ELOQUA_PASSWORD']
                          )
    if PRINT_OUTPUT:
        print("\nRunning as", os.environ['ELOQUA_USER'])

    bulk_definition.exports('customobjects', cdo_id)

    bulk_definition.add_fields(cdo_fields)
    if PRINT_OUTPUT:
        print("\nFields to be pulled:", cdo_fields)

    bulk_definition.filter_date(field="CreatedAt"
                                , start=date_oldest
                                , end=date_newest
                               )
    if PRINT_OUTPUT:
        print("\nRecords will be pulled with created dates greater than", \
              date_oldest, "and less than or equal to", date_newest \
             )

    bulk_definition.create_def(name=cdo_name_as_var)

    if PRINT_OUTPUT:
        print("\nPulling request (please wait)")
    status = bulk_definition.sync(timeout=000)
    if status in ['warning', 'error']:
        logs = bulk_definition.get_sync_logs()
        pprint(logs)

    response = bulk_definition.get_export_data()
    response_count = len(response)
    if PRINT_OUTPUT:
        print("\nCount of records returned:", response_count)
    if response_count != 0:
        if PRINT_OUTPUT:
            print("\nFirst row:")
            pprint(response[0])

    return response


def mark_local_for_deletion(all_cdo_records, filter_criteria):
    """
    Returns only records that meet the criteria
    """
    if PRINT_OUTPUT:
        print("\nFiltering on row criteria")
        pprint(filter_criteria)
    filtered_records = criteria_if(filter_row=filter_criteria, records=all_cdo_records)
    if PRINT_OUTPUT:
        print("\nRecords filtered.")

    return filtered_records


def mark_eloqua_for_deletion(record_ids, data_status_field, cdo_id, cdo_name_as_var, chunk_count=000, sync_timeout=000):
    """
    Change the data status of the CDO records so that a
    feeder passes them to a Program Canvas which deletes them.
    """
    status = None
    
    if PRINT_OUTPUT:
        print("\nData Status to be used to mark for deletion:", NEW_DATA_STATUS)

    # chunk data_to_post into groups
    record_ids_count = len(record_ids) - 1
    if PRINT_OUTPUT:
        last_post_num = 0
        last_post_time = datetime.now()
        print("Definition created in server.", \
              "Starting to POST data.", record_ids_count, "records to post.", \
              datetime.strftime(last_post_time, '%Y-%m-%d %H:%M'), \
             )
    bulk_definition = Bulk(company=os.environ['ELOQUA_COMPANY']
                           , username=os.environ['ELOQUA_USER']
                           , password=os.environ['ELOQUA_PASSWORD']
                          )
    bulk_definition.imports(elq_object='customobjects', obj_id=cdo_id)
    cdo_fields = ["DataCardIDExt"
                  , data_status_field
                 ]
    bulk_definition.add_fields(cdo_fields)
    bulk_definition.add_options(identifierFieldName='DataCardIDExt')
    bulk_definition.create_def(name=cdo_name_as_var)
    data_to_post = []
    for row_num, row in enumerate(record_ids):
        data_to_post.append({
            "DataCardIDExt": row \
            , data_status_field: NEW_DATA_STATUS
        })
        is_first_row = row_num == 0
        is_last_row = row_num == record_ids_count
        is_chunk_row = row_num % chunk_count == 0
        if (is_chunk_row or is_last_row) and not is_first_row:
            if PRINT_OUTPUT:
                print("POSTing records", last_post_num, "to", row_num)
            attempts = 0            
            while True:
                try:
                    bulk_definition.post_data(data=data_to_post)
                    break
                except:
                    attempts += 1
                    wait_time = attempts * 5
                    print("POST data failed. Waiting", wait_time, "seconds before trying again.")
                    time.sleep(wait_time)
                if attempts > 10:
                    raise "POST data failed after" + attempts + "attempts."
            if PRINT_OUTPUT:
                try:
                    now = datetime.now()
                    time_processing = now - last_post_time
                    processing_rate = chunk_count / time_processing.seconds
                    remaining_records = (record_ids_count - row_num)
                    remaining_time = remaining_records / processing_rate
                    estimated_completion_time = \
                        now + relativedelta(seconds=+remaining_time)
                    print("Processed for", int(time_processing.seconds), \
                        "seconds; estimated completion in", \
                        round(remaining_time/60, 1), "minutes at", \
                        datetime.strftime(estimated_completion_time, '%Y-%m-%d %H:%M'), \
                        "; currently", datetime.strftime(now, '%Y-%m-%d %H:%M'), \
                        )
                except:
                    pass
            data_to_post = []
            last_post_num = row_num
            last_post_time = datetime.now()
        if is_last_row:
            if PRINT_OUTPUT:
                print("Now waiting for the sync (up to", sync_timeout/60, "minutes).")
            status = bulk_definition.sync(timeout=sync_timeout)
            if PRINT_OUTPUT:
                print("Sync status", status)
            if status in ['warning', 'error']:
                logs = bulk_definition.get_sync_logs()
                pprint(logs)


    if PRINT_OUTPUT:
        print("The filtered records have all had their data status changed to \"", \
              NEW_DATA_STATUS, "\".", \
             )

    return status


if __name__ == '__main__':

    visor_eloqua_cdo_cleanup()
