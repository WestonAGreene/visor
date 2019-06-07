"""
Will pull the last hour of modified records from a given CDO
and push the count of records to pushgateway

Not active. 000-10-03_14.52

Created 000-10-03 11:06

In Prometheus:
There is one main exported_job that triggers all CDOs and waits for them.
Each individual CDO will run in a subprocess and will have to have a separate exported_job 
    and therefore a separate prometheus_registry.
"""

from datetime import datetime
from datetime import timedelta
import os
import re
import sys
from json import load
from multiprocessing import Process
import pytz
from pyeloqua import Bulk
from function_defintions_visor import format_text_for_vars, prometheus_registry_prep, export_json_to_csv
from visor_main import script_wrapper

try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except KeyError:
    PRINT_OUTPUT = False
# PRINT_OUTPUT = True  # devonly
if PRINT_OUTPUT:
    from pprint import pprint
    from json import dump

CAMPAIGN_ID_REGEX_18 = re.compile(r'000[a-zA-Z0-9]{15}$')
CAMPAIGN_ID_REGEX_15 = re.compile(r'000[a-zA-Z0-9]{12}$')

FILE_PREFIX = 'visor_eloqua_cdo_'

OPTIONAL_FIELDS = [
    'status_field',
    'offer_field',
    'tactic_field',
    'email_field',
    'cdo_fields',
    'custom_fields',
    'frequency',
    'date_to',
]

CDOS_TO_MONITOR = load(open('visor_eloqua_cdo.json', 'r'))

TIMEZONE = pytz.timezone("America/New_York")
NOW_RALEIGH = datetime.now(TIMEZONE)


def visor_eloqua_cdo(adhoc=None):
    """
    Combines all functions

    If parameter "adhoc" is True, some decision are different, such as analysis on all data rather than a subset (such as only the last 24 hours). 
    I also included it envisioning some command line argument passing.

    However, to run this script adhoc, it is designed to accept the file of a custom CDO JSON.
    See 'visor_eloqua_cdo_exampleAdHoc.json' for an example.
    This could be run by 
        $export PRINT_OUTPUT="True"; python3 visor_eloqua_cdo.py visor_eloqua_cdo_exampleAdHoc.json
    """
    # prep CDO criteria
    sys.path.insert(0, './%scustomProcessing' % FILE_PREFIX)
    for key, item in CDOS_TO_MONITOR.items():

        item['var_name'] = format_text_for_vars(item['name'])

        for ROW in OPTIONAL_FIELDS:
            if ROW not in item:
                item[ROW] = None

        custom_function = '%s%s' % (FILE_PREFIX, item['var_name'])
        if PRINT_OUTPUT:
            print("Looking for ", custom_function)
        try:
            item['function'] = getattr(__import__(custom_function, fromlist=[custom_function]),
                                       custom_function,
                                       )
            if PRINT_OUTPUT:
                print("found ", custom_function)
        except:
            item['function'] = None
            if PRINT_OUTPUT:
                print("didn't find ", custom_function)

    if PRINT_OUTPUT:
        print("\nThis script will pull the Custom Data Objects (CDOs) of a CDO table ",
              "and trigger custom processing, if any.",
              "\nNow:", datetime.now(),
              )

    global NOW_RALEIGH
    NOW_RALEIGH = datetime.now(TIMEZONE)  # need to reinstantiate NOW_RALEIGH because the date grows stale otherwise since it's declared outside of this function. This is where using class variables and these scripts as subclass would be handy

    for key, item in CDOS_TO_MONITOR.items():
        file_name = "%s%s" % (FILE_PREFIX, item['name'])
        try:  # This try prevents an exception in the case that a frequency isn't specified for the CDO.
            sub_process = Process(target=script_wrapper, args=(file_name,
                                                               process_cdo,
                                                               [key, adhoc],
                                                               (item['frequency'] * 60 * 60),
                                                               )
                                  )
        except:
            sub_process = Process(target=script_wrapper, args=(file_name,
                                                               process_cdo,
                                                               [key, adhoc],
                                                               )
                                  )
        if PRINT_OUTPUT:
            print("Triggering sub_process for ", item['name'])
        try:  # try so that if the sub_process fails the main loop script (visor_main.py) continues.
            sub_process.start()
        except:
            if PRINT_OUTPUT:
                print("sub_process failed for ", item['name'])
                pprint(sys.exc_info())

    sub_process.join()  # TODO doesn't wait for the sub_processes to finish for some reason; low priority

    # return prometheus_registry
    # return nothing  # this function isn't to return anything becuase it spins off script_wrappers for every CDO and those sub processes do the returning


def process_cdo(args):
    """
    Pulls records of a CDO, does generic processing, then triggers custom processing, if any.
    args = a list[] of two variables: cdo_id, adhoc.
    """
    cdo_id = args[0]
    adhoc = args[1]

    if PRINT_OUTPUT:
        print("\nThe chosen CDO table:", cdo_id, CDOS_TO_MONITOR[cdo_id]['name'])

    if CDOS_TO_MONITOR[cdo_id]['frequency'] is not None:
        whole_number = (int(NOW_RALEIGH.strftime('%H')) /
                        CDOS_TO_MONITOR[cdo_id]['frequency']
                        )
        if not float(whole_number).is_integer():
            if PRINT_OUTPUT:
                print("\n This CDO's frequency is set only to run every", CDOS_TO_MONITOR[cdo_id]['frequency'],
                      "hours. It is not time yet.")
            return

    bulk_definition = Bulk(company=os.environ['ELOQUA_COMPANY'],
                           username=os.environ['ELOQUA_USER'],
                           password=os.environ['ELOQUA_PASSWORD'],
                           )
    # if PRINT_OUTPUT:
    #     print("\nRunning as", os.environ['ELOQUA_USER'])

    bulk_definition.exports('customobjects', cdo_id)

    fields = [
        "DataCardIDExt",
        "CreatedAt",
        "UpdatedAt"
    ]
    if CDOS_TO_MONITOR[cdo_id]['tactic_field'] is not None:
        fields.append(CDOS_TO_MONITOR[cdo_id]['tactic_field'])
    if CDOS_TO_MONITOR[cdo_id]['offer_field'] is not None:
        fields.append(CDOS_TO_MONITOR[cdo_id]['offer_field'])
    if CDOS_TO_MONITOR[cdo_id]['status_field'] is not None:
        fields.append(CDOS_TO_MONITOR[cdo_id]['status_field'])
    if CDOS_TO_MONITOR[cdo_id]['email_field'] is not None:
        fields.append(CDOS_TO_MONITOR[cdo_id]['email_field'])
    if CDOS_TO_MONITOR[cdo_id]['cdo_fields'] is not None:
        for row in CDOS_TO_MONITOR[cdo_id]['cdo_fields']:
            fields.append(row)
    # if PRINT_OUTPUT:
    #     print("\n CDO fields to be pulled:")
    #     pprint(fields)
    bulk_definition.add_fields(fields)
    if CDOS_TO_MONITOR[cdo_id]['custom_fields'] is not None:
        field_dic = []
        for row in CDOS_TO_MONITOR[cdo_id]['custom_fields']:
            field_dic.append({'statement': '{{CustomObject[%s].%s}}' % (cdo_id, row['statement']),
                              'name': row['name']
                              })
        # if PRINT_OUTPUT:
        #     print("\n Linked contact fields to be pulled:")
        #     for row in CDOS_TO_MONITOR[cdo_id]['custom_fields']:
        #         print(row['name'])
        bulk_definition.job['fields'].extend(field_dic)

    # if PRINT_OUTPUT:
    #     print("\n bulk_definition:")
    #     pprint(bulk_definition.__dict__) 

    try:  # this is to allow for a custom json of CDOs to be able to restrict the timie
        date_to = datetime.strptime(
            CDOS_TO_MONITOR[cdo_id]['date_to'],
            "%Y-%m-%d %H:%M"
        )
    except TypeError:
        date_to = NOW_RALEIGH
    date_from = date_to + timedelta(-CDOS_TO_MONITOR[cdo_id]['days_pulled'])
    bulk_definition.filter_date(field=CDOS_TO_MONITOR[cdo_id]['date_field'],
                                start=date_from,
                                end=date_to,
                                )
    # if PRINT_OUTPUT:
    #     print("\nRecords will be pulled with created dates greater than",
    #           date_from, "and less than or equal to", date_to,
    #           )
    try:
        if PRINT_OUTPUT:  # pull from a local file if testing (that is, PRINT_OUTPUT = True) otherwise raise an error so it goes to the exception and pulls from eloqua.
            if not os.path.exists("monitor-pvc/testing"):  # should only need to run once.
                os.mkdir("monitor-pvc/testing")
            response = load(open("monitor-pvc/testing/testingCdo_%s.json" % str(cdo_id), 'r'))
            print("Managed to pull sample records from local; no need to GET from Eloqua")
        else:
            fail = 1 / 0
    except (ZeroDivisionError, FileNotFoundError):
        bulk_definition.create_def(name=CDOS_TO_MONITOR[cdo_id]['name'])

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
                with open("monitor-pvc/testing/testingCdo_%s.json" % str(cdo_id), 'w') as fopen:
                    dump(response, fopen)
                print("Exported file locally to skip the GET to Eloqua next time.")

    # Modify response with key performance indicators

    print("Slow down?")
    now_raleigh_no_tz = NOW_RALEIGH.replace(tzinfo=None)
    for row in response:
        created_at = datetime.strptime(row['CreatedAt'], "%Y-%m-%d %H:%M:%S.%f")  # TODO: make faster
        # created_at = TIMEZONE.localize(parse(row['CreatedAt']))  # Takes too long. 000-05-28
        row['age'] = (now_raleigh_no_tz - created_at).seconds
    print("end slow down")

    analyze_campaigns = {}
    if CDOS_TO_MONITOR[cdo_id]['offer_field'] is not None:
        analyze_campaigns['offer'] = CDOS_TO_MONITOR[cdo_id]['offer_field']
    if CDOS_TO_MONITOR[cdo_id]['tactic_field'] is not None:
        analyze_campaigns['tactic'] = CDOS_TO_MONITOR[cdo_id]['tactic_field']
    if analyze_campaigns:
        for key, item in analyze_campaigns.items():
            for row in response:
                row['%s_blank' % key] = 0
                row['%s_valid' % key] = 0
                row['%s_format_bad' % key] = 0
                if row[item] == '':
                    row['%s_blank' % key] = 1

                if (row['%s_blank' % key] == 0 and
                        (CAMPAIGN_ID_REGEX_18.match(row[item]) or
                         CAMPAIGN_ID_REGEX_15.match(row[item])
                        )
                ):
                    row['%s_valid' % key] = 1

                if (row['%s_blank' % key] == 0 and
                        row['%s_valid' % key] == 0
                ):
                    row['%s_format_bad' % key] = 1

        if len(analyze_campaigns) > 1:  # That is, includes both offer and tactic
            for row in response:
                row['offerless_tactic'] = 0
                row['tacticless_offer'] = 0
                if (row['tactic_blank'] == 0 and
                        row['offer_blank'] == 1
                ):
                    row['offerless_tactic'] = 1
                if (row['offer_blank'] == 0 and
                        row['tactic_blank'] == 1
                ):
                    row['tacticless_offer'] = 1

    if CDOS_TO_MONITOR[cdo_id]['status_field'] is not None:
        data_status_normal = ['NEW',
                              'PROCESSED',
                              'PROCESSED as NEW',
                              'PROCESSED as MOD',
                              'PROCESSING...',
                              'PROCESSING',
                              'READY to PROCESS',
                              ]
        for row in response:
            row['data_status_abnormal'] = 0
            if row[CDOS_TO_MONITOR[cdo_id]['status_field']] not in data_status_normal:
                row['data_status_abnormal'] = 1

    if CDOS_TO_MONITOR[cdo_id]['email_field'] is not None:
        email_normal_characters = [
            '@',
            '.'
        ]
        for row in response:
            row['email_abnormal'] = 0
            if any(email_normal_char not in row[CDOS_TO_MONITOR[cdo_id]['email_field']] for email_normal_char in
                   email_normal_characters):
                row['email_abnormal'] = 1
            row['email_blank'] = 0
            if row[CDOS_TO_MONITOR[cdo_id]['email_field']] == '':
                row['email_blank'] = 1

    # START Generic CDO monitoring #

    metric_list = generic_analysis(
        response=response,
        date_field=CDOS_TO_MONITOR[cdo_id]['date_field'],
        status_field=CDOS_TO_MONITOR[cdo_id]['status_field'],
        email_field=CDOS_TO_MONITOR[cdo_id]['email_field'],
        analyze_campaigns=analyze_campaigns,
        adhoc=adhoc,
        print_output=PRINT_OUTPUT
    )

    # END Generic CDO monitoring #

    # START Custom CDO analysis #

    if CDOS_TO_MONITOR[cdo_id]['function'] is not None:
        if PRINT_OUTPUT:
            print("Triggering custom CDO processing for ", CDOS_TO_MONITOR[cdo_id]['var_name'])
        response, metric_list = CDOS_TO_MONITOR[cdo_id]['function'](
            records=response,
            metric_list=metric_list,
            adhoc=adhoc
        )
        if PRINT_OUTPUT:
            print("Custom CDO processing complete for ", CDOS_TO_MONITOR[cdo_id]['var_name'])

    # END Custom CDO analysis #

    if adhoc or PRINT_OUTPUT:
        export_json_to_csv(json=response, unique_name="visor_eloqua_cdo.%s." % cdo_id)

    if PRINT_OUTPUT:
        # print("Metrics to push to prometheus:")
        # pprint(metric_list)
        print("Pushing metrics for", CDOS_TO_MONITOR[cdo_id]['name'], "to Prometheus")
    job_name = "%s%s" % (FILE_PREFIX, CDOS_TO_MONITOR[cdo_id]['var_name'])
    prometheus_registry = prometheus_registry_prep(metric_list=metric_list, job_name=job_name)
    # return [prometheus_registry, job_name]
    return metric_list


def generic_analysis(
        response,
        date_field,
        status_field=None,
        email_field=None,
        analyze_campaigns=None,
        metric_list=None,
        metric_prefix='',
        adhoc=None,
        print_output=False
):
    """
    Analysis that should be applied on every data set from a CDO before passing to prometheus
    """

    if metric_list is None:
        metric_list = []

    if adhoc is None:  # Split from adhoc because the following analyses filter depending on timeframe
        date_pst24hr = NOW_RALEIGH + timedelta(-1)
        date_pst24hr = datetime.strftime(date_pst24hr, '%Y-%m-%d %H:%M:%S')
        response_crtd_pst24hr = [row for row in response if row['CreatedAt'] > date_pst24hr]

        # if date_field == 'CreatedAt':
        # else:
        #     response_gnric_analysis_crtd_cnt = len([row for row in response_gnric_analysis if row['CreatedAt'] > date_pst24hr])
        response_crtd_pst24hr_cnt = len(response_crtd_pst24hr)
        metric_desc = "Count of CDO records created"
        metric_name = "crtd"
        metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                            'metric_value': response_crtd_pst24hr_cnt})
        if print_output:
            print("\n response_crtd_pst24hr_cnt:", response_crtd_pst24hr_cnt)

        if date_field == 'UpdatedAt':
            response_mdfd_pst24hr_cnt = len([row for row in response if row['UpdatedAt'] > date_pst24hr])
            metric_desc = "Count of CDO records modified"
            metric_name = "mdfd"
            metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                                'metric_value': response_mdfd_pst24hr_cnt})
            if print_output:
                print("\n response_mdfd_pst24hr_cnt:", response_mdfd_pst24hr_cnt)

        if status_field is not None:
            response_status_new = [row for row in response if row[status_field] == 'NEW']
            response_status_new_cnt = len(response_status_new)
            if response_status_new_cnt > 0:
                response_status_new_avg_age_mins = sum(
                    row['age'] for row in response_status_new) / response_status_new_cnt / 60
            else:
                response_status_new_avg_age_mins = 0
            metric_desc = "Count of CDO records that still have a data status of NEW"
            metric_name = "new_avg_age_mins"
            metric_value = response_status_new_avg_age_mins
            metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                                'metric_value': metric_value})
            if print_output:
                print("\n response_status_new_avg_age_mins:", response_status_new_avg_age_mins)

        response = response_crtd_pst24hr

    # else:
    #     response_gnric_analysis = response

    if analyze_campaigns is not None:
        for key, item in analyze_campaigns.items():
            metric_value = sum(row['%s_format_bad' % key] for row in response)
            metric_desc = "Records that have a populated and incorrectly formatted %s." % key
            metric_name = "%s_format_bad" % key
            metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                                'metric_value': metric_value})
            metric_value = sum(row['%s_valid' % key] for row in response)
            metric_desc = "Records that have a populated and correctly formatted %s." % key
            metric_name = "%s_valid" % key
            metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                                'metric_value': metric_value})
            if len(analyze_campaigns) > 1:
                None  # this prevents redundant statistics; if the offerless_tactic stat is already included, I don't need to know that there is an equally sized offer_blank. 
            else:
                metric_value = sum(row['%s_blank' % key] for row in response)
                metric_desc = "Records that have a blank %s." % key
                metric_name = "%s_blank" % key
                metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                                    'metric_value': metric_value})

        if len(analyze_campaigns) > 1:
            metric_value = 0
            for row in response:
                if row['offer_blank'] == 1 and row['tactic_blank'] == 1:
                    metric_value += 1
            metric_desc = "Records that have a blank offer and tactic."
            metric_name = "campaigns_blank"
            metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                                'metric_value': metric_value})
            metric_value = sum(row['offerless_tactic'] for row in response)
            metric_desc = "Records that have a blank offer, but have a tactic."
            metric_name = "offerless_tactic"
            metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                                'metric_value': metric_value})
            metric_value = sum(row['tacticless_offer'] for row in response)
            metric_desc = "Records that have a blank tactic, but have an offer."
            metric_name = "tacticless_offer"
            metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                                'metric_value': metric_value})

    if status_field is not None:
        data_status_abnormal = sum([row['data_status_abnormal'] for row in response])
        metric_desc = "Count of CDO records that are not the typical Data Status of 'NEW', 'PROCESSED', or 'PROCESSING'."
        metric_name = "data_status_abnormal"
        metric_value = data_status_abnormal
        metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                            'metric_value': metric_value})
        if print_output:
            print("\n data_status_abnormal:", data_status_abnormal)
        if data_status_abnormal > 0:
            data_status_set = set()
            for row in response:
                data_status_set.add(row[status_field])
            data_status_count = {}
            for row in data_status_set:
                row_count = 0
                for response_row in response:
                    if response_row[status_field] == row:
                        row_count += 1
                data_status_count[row] = row_count
            if PRINT_OUTPUT:
                print('Abnormal data status found; count of each data status:')
                pprint(data_status_count)

    if email_field is not None:
        email_abnormal = sum([row['email_abnormal'] for row in response])
        metric_desc = "Count of CDO records that are not the typical Data Status of 'NEW', 'PROCESSED', or 'PROCESSING'."
        metric_name = "email_abnormal"
        metric_value = email_abnormal
        metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                            'metric_value': metric_value})
        if print_output:
            print("\n email_abnormal:", email_abnormal)
        email_blank = sum([row['email_blank'] for row in response])
        metric_desc = "Count of CDO records that are not the typical Data Status of 'NEW', 'PROCESSED', or 'PROCESSING'."
        metric_name = "email_blank"
        metric_value = email_blank
        metric_list.append({'metric_name': "%s%s" % (metric_prefix, metric_name), 'metric_desc': metric_desc,
                            'metric_value': metric_value})
        if print_output:
            print("\n email_blank:", email_blank)

    return metric_list


if __name__ == '__main__':

    ADHOC = None

    try:
        CDO_JSON_ARGUMENT = sys.argv[1]
        ADHOC = True
    except IndexError:
        CDO_JSON_ARGUMENT = 'visor_eloqua_cdo.json'

    CDOS_TO_MONITOR = load(open(CDO_JSON_ARGUMENT, 'r'))

    visor_eloqua_cdo(adhoc=ADHOC)
