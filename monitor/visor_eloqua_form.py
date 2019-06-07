"""
monitoring on Eloqua forms.
You can probably tell that I started using a python linter (pylint for Atom).
Created 000-08-10_10.45
"""

import datetime
import os
import sys
from json import dump, load, JSONDecodeError

import pytz
import requests
from pyeloqua import Form, Eloqua
from pprint import pprint

from function_defintions_visor import printObject, export_json_to_csv, format_text_for_vars

# os.environ['PRINT_OUTPUT'] = "True"  # devonly
try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except KeyError:
    PRINT_OUTPUT = False
# PRINT_OUTPUT = True

METRIC_LIST = []

FORMS_CUSTOM_ANALYSIS = {
    "000": {
        "form_name": "Integration Form: Automated Campaigns",
        "fields_planned": [
            "submittedAt",
            "id",
            "F_FormData_Source",
            "F_FormData_IsLeadActivity",
            "C_EmailAddress",
            "A_TacticID_External"
        ]
    },
    "000": {
        "form_name": "Integration Form: Automated Campaigns",
        "function": "dyfo_monitoring"
    }
}

# because a PVC is mounted at folder "monitor-pvc", all the files created there from the Build are wiped, meaning I can only reply on files in "monitor-pvc" that have been created by my scripts post-build
FORMS_FILENAME = "monitor-pvc/visor_eloqua_form.json"
try:  # after the first run of script, this try will no longer fail
    FORMS = load(open(FORMS_FILENAME, 'r'))
except FileNotFoundError:
    FORMS = load(open("visor_eloqua_form.json", 'r'))

FORM_DEFINITION_PATH = "monitor-pvc/visor_eloqua_form_definitions/"
if not os.path.exists(FORM_DEFINITION_PATH):  # also should only need to run once.
    os.mkdir(FORM_DEFINITION_PATH)

TIMEZONE = pytz.timezone("America/New_York")
NOW_RALEIGH = datetime.datetime.now(TIMEZONE)


def visor_eloqua_form():
    """
    The defintion to be run when this file is run
    or the main definition when used in visor_main.py
    """

    global FORMS  # so that I edit the global variable: https://www.geeksforgeeks.org/global-local-variables-python/

    global NOW_RALEIGH
    NOW_RALEIGH = datetime.datetime.now(TIMEZONE)  # need to reinstantiate NOW_RALEIGH because the date grows stale otherwise since it's declared outside of this function. This is where using class variables and these scripts as subclass would be handy

    if low_traffic_hour():
        try:
            forms_from_api = form_name_search()
            forms_from_api.update(FORMS)  # FORMS updates forms_from_api because I want the values() from FORMS to be last in and therefore remain
            FORMS = forms_from_api
            with open(FORMS_FILENAME, 'w') as fopen:
                dump(FORMS, fopen)
        except:
            print("Failed to refresh", FORMS_FILENAME)
            pprint(sys.exc_info())

    for key, value in FORMS.items():
        try:
            visor_eloqua_form_proc(form_id=key)
        except:
            pprint(sys.exc_info())

    # prometheus_registry = prometheus_registry_prep(metric_list=METRIC_LIST, job_name=os.path.basename(__file__))
    # return prometheus_registry
    return METRIC_LIST


def visor_eloqua_form_proc(form_id,
                           time_range=1,
                           ):
    """The function for processing visor_eloqua_form"""

    if PRINT_OUTPUT:
        print("\n\n\nForm name:", FORMS[form_id], "(", form_id, ")")

    form_name = format_text_for_vars(FORMS[form_id])

    if low_traffic_hour():
        form_definition_refresh(form_id=form_id, form_name=form_name)
        
    try:
        form_definition = Form(username=os.environ['ELOQUA_USER'],
                               password=os.environ['ELOQUA_PASSWORD'],
                               company=os.environ['ELOQUA_COMPANY'],
                               form_path=form_definition_path(form_name)
                               )
    except:
        form_definition = Form(username=os.environ['ELOQUA_USER'],
                               password=os.environ['ELOQUA_PASSWORD'],
                               company=os.environ['ELOQUA_COMPANY'],
                               form_id=form_id
                               )
        form_definition.write_form(form_definition_path(form_name))

    # request date range
    request_range_start = NOW_RALEIGH + datetime.timedelta(-time_range)
    request_range_start_int = int(request_range_start.timestamp())
    request_range_end = NOW_RALEIGH + datetime.timedelta(-0)
    request_range_end_int = int(request_range_end.timestamp())
    request_range = request_range_end - request_range_start
    if PRINT_OUTPUT:
        print('\nDate range to be returned: '
              , request_range_start_int, ' to '
              , request_range_end_int, '; '
              , request_range.days, 'day(s)'
              )
        print('\nPulling request (please wait)')

    if form_id in FORMS_CUSTOM_ANALYSIS:  # spilt between pulling all submission data--for custom analysis--and just the count of submission--generic analysis
        if PRINT_OUTPUT:
            test_file_name = "monitor-pvc/testing/testing.form{form_id}.json".format(form_id=form_id)
            try:
                response = load(open(test_file_name, 'r'))
                print(len(response), "records pulled from file.")
            except:
                response = form_definition.get_data(
                    start=request_range_start_int
                    , end=request_range_end_int
                )
        else:
            response = form_definition.get_data(
                start=request_range_start_int
                , end=request_range_end_int
            )

        if PRINT_OUTPUT:
            with open(test_file_name, 'w') as fopen:
                dump(response, fopen)

        response_cnt = len(response)

        if response_cnt == 0:
            return response_cnt

        if PRINT_OUTPUT:
            print('\nTotal records pulled:', response_cnt
                  , '\nFirst row of data: '
                  )
            printObject(response)

    else:
        response = form_definition.get_count(
            start=request_range_start_int
            , end=request_range_end_int
        )
        response_cnt = response
        if PRINT_OUTPUT:
            print('\nTotal records pulled:', response_cnt
                  , '\nNo field analysis requested. End.'
                  )

    if response_cnt != 0 and form_id in FORMS_CUSTOM_ANALYSIS:
        if "fields_planned" in FORMS_CUSTOM_ANALYSIS[form_id]:
            try:
                field_planned_ops(
                    response=response,
                    field_planned=FORMS_CUSTOM_ANALYSIS[form_id]["fields_planned"],
                    form_name=form_name
                )
            except:
                pprint(sys.exc_info())

        if "function" in FORMS_CUSTOM_ANALYSIS[form_id]:
            try:
                FORMS_CUSTOM_ANALYSIS[form_id]["function"] = getattr(
                    __import__("visor_eloqua_form",
                               fromlist=[FORMS_CUSTOM_ANALYSIS[form_id]["function"]]
                               ),
                    FORMS_CUSTOM_ANALYSIS[form_id]["function"]
                )
                FORMS_CUSTOM_ANALYSIS[form_id]["function"](
                    response=response,
                    form_name=form_name
                )
            except:
                pprint(sys.exc_info())

    # Always add the count to the general form metric
    metric_desc = "Count of submissions created."
    METRIC_LIST.append({"metric_name": form_name, "metric_desc": metric_desc, "metric_value": response_cnt})


def field_planned_ops(
        response,
        field_planned,
        form_name
):
    """
    if field_planned is populated then assess if the correct fields are populated
    """
    # response = [  # to test that the function works
    #     {
    #         "C_EmailAddress": "junk1@me.com",
    #         "A_TacticID_External": "000f000RSioAAG",
    #         "F_FormData_Source": "GET READY_DRIP_PRIVATE CLOUD_STRATEGY_IT_TECH_CAMPAIGN",
    #         "id": "000",
    #         "submittedAt": "000"
    #     },
    #     {
    #         "C_EmailAddress": "junk2@me.com",
    #         "A_TacticID_External": "000f000CtoXAAS",
    #         "F_FormData_Source": "AGILE INTEGRATION_NURTURE_FSI_TECH_CAMPAIGN",
    #         "F_FormData_IsLeadActivity": "0",
    #         "id": "000",
    #         "submittedAt": "000",
    #         "bad_field": "bad value"
    #     }
    # ]

    if PRINT_OUTPUT:
        print("\nDetermining if there are fields that should be populated but aren't."
              , "These fields should be populated:"
              )
        pprint(field_planned)

    metric_name = "%s%s" % (form_name, "__fieldPlannedMissing")
    metric_desc = "Count of submissions with fields that should be populated but are not."
    if PRINT_OUTPUT:
        print("\nDetermining:", metric_desc)
    field_planned_missing = set()
    for submission in response:
        submission["fieldPlannedMissing"] = 0
        for field in field_planned:
            if field not in submission:
                submission["fieldPlannedMissing"] = 1
                field_planned_missing.add(field)
    submissions_missing_field_planned = sum(row['fieldPlannedMissing'] for row in response)
    METRIC_LIST.append({"metric_name": metric_name,
                        "metric_desc": metric_desc,
                        "metric_value": submissions_missing_field_planned}
                       )
    if PRINT_OUTPUT:
        if submissions_missing_field_planned == 0:
            print("No planned fields are missing from submissions.")
        else:
            print(submissions_missing_field_planned
                  , "submissions are missing a field that should be included."
                  , "They are:"
                  )
            pprint(field_planned_missing)

    metric_name = "%s%s" % (form_name, "__fieldUnplannedPopulated")
    metric_desc = "Count of submissions with fields that are populated but should not be."
    if PRINT_OUTPUT:
        print("\nDetermining:", metric_desc)
    field_actual_unplanned = set()
    for submission in response:
        submission["fieldUnplannedPopulated"] = 0
        for field in submission.keys():
            if field not in field_planned and \
                    field not in ['fieldPlannedMissing', 'fieldUnplannedPopulated']:
                submission["fieldUnplannedPopulated"] = 1
                field_actual_unplanned.add(field)
    submissions_field_unplanned = sum(row['fieldUnplannedPopulated'] for row in response)
    METRIC_LIST.append({"metric_name": metric_name,
                        "metric_desc": metric_desc,
                        "metric_value": submissions_field_unplanned}
                       )
    if PRINT_OUTPUT:
        if submissions_field_unplanned == 0:
            print("No unplanned fields are populated.")
        else:
            print(submissions_field_unplanned
                  , "fields are populated that shouldn't be populated."
                  , "They are:"
                  )
            pprint(field_actual_unplanned)
        # pivt_field_actual_unplanned = {}
        # for row_fld in field_actual_unplanned:
        #     count_within_loop = 0
        #     for row_response in response:
        #         try:
        #             if row_response[row_fld]:
        #                 count_within_loop += 1
        #         except:
        #             pass
        #     pivt_field_actual_unplanned[row_fld] = count_within_loop
        # if PRINT_OUTPUT:
        #     print('Pivot on field_actual_unplanned:')
        #     printObject(pivt_field_actual_unplanned)

    # metric_desc = "Count of records that have at least one unplanned field populated."
    # metric_name = "%s%s" % (form_name, "__createdWithUnplannedField")
    # if PRINT_OUTPUT:
    #     print("\nDetermining:", metric_desc)
    # if submissions_field_unplanned == 0:
    #     if PRINT_OUTPUT:
    #         print("No unplanned fields are populated.")
    #     response_w_fld_unplanned_cnt = 0
    # else:
    #     response_w_fld_unplanned = []
    #     for row in response:
    #         fields_in_row = [keys for keys, values in row.items()]
    #         count_within_loop = 0
    #         for field in fields_in_row:
    #             if field in field_actual_unplanned:
    #                 count_within_loop += 1
    #         if count_within_loop > 0:
    #             response_w_fld_unplanned.append(row)
    #     response_w_fld_unplanned_cnt = len(response_w_fld_unplanned)
    #     if PRINT_OUTPUT:
    #         print(response_w_fld_unplanned_cnt
    #               , "records have at least one unplanned field populated."
    #               , "\nFirst row of records with unplanned fields populated:"
    #               )
    #         printObject(response_w_fld_unplanned)
    # METRIC_LIST.append({"metric_name": metric_name,
    #                     "metric_desc": metric_desc,
    #                     "metric_value": response_w_fld_unplanned_cnt}
    #                    )
    #
    # metric_desc = "Count of records that have at least one planned field that is blank."
    # metric_name = "%s%s" % (form_name, "__createdWithBlankPlannedField")
    # if PRINT_OUTPUT:
    #     print("\nDetermining:", metric_desc)
    # response_w_field_planned_blnk = []
    # for row in response:
    #     fields_in_row = [keys for keys, values in row.items()]
    #     count_within_loop = 0
    #     for field in field_planned:
    #         if field not in fields_in_row or row[field] == "":
    #             count_within_loop += 1
    #     if count_within_loop > 0:
    #         response_w_field_planned_blnk.append(row)
    # response_w_field_planned_blnk_cnt = len(response_w_field_planned_blnk)
    # METRIC_LIST.append({"metric_name": metric_name,
    #                     "metric_desc": metric_desc,
    #                     "metric_value": response_w_field_planned_blnk_cnt
    #                     }
    #                    )
    if PRINT_OUTPUT:
        # if response_w_field_planned_blnk_cnt > 0:
        #     print(response_w_field_planned_blnk_cnt
        #           , "records have at least one planned field that is blank."
        #           , "\nFirst row of records with blank planned fields:"
        #           )
        #     printObject(response_w_field_planned_blnk)
        export_json_to_csv(json=response,
                           unique_name=form_name + "_monitoring"
                           )
        with open("testingUnplannedFields", 'w') as fopen:
            dump(response, fopen)


def dyfo_monitoring(response, form_name):
    """
    000-05-18 13:49
    US000 DyFo A_UX_Status monitoring:
        SLI on DyFo A_UX_Status

        Field has 4 possible values:
        "New Offer Selected: *"
        "no_offer=true|Bad Offer: *"
        "Bad Offer: *"
        "OK"

        DOD:
        Trending line on all 4 values and an alert if bad offer is more than 1% of the average of 'OK'.
    """

    if PRINT_OUTPUT:
        a_ux_status_unique = set()
        for row in response:
            a_ux_status_unique.add(row['A_UX_Status'])
        pivot = {}
        for row in a_ux_status_unique:
            pivot[row] = len([rowAll for rowAll in response if rowAll['A_UX_Status'] == row])
        if PRINT_OUTPUT:
            pprint(pivot)

    expected_ux_statuses = {
        'Bad Offer': '',
        'New Offer Selected': '',
        'OK': '',
        'no_offer=true': '',
    }
    UX_Status_missing = 0

    for key, value in expected_ux_statuses.items():
        expected_ux_statuses[key] = {
            'count': 0,
            'len': len(key),
            'clean_name': format_text_for_vars(key)

        }

    for key, value in expected_ux_statuses.items():
        count = 0
        for row in response:
            try:
                if key in row['A_UX_Status'][:value['len']]:
                    count += 1
            except:
                UX_Status_missing += 1
                if PRINT_OUTPUT:
                    pprint(sys.exc_info())
                    pprint(row)
        value['count'] = count

    expected_ux_statuses['UX_Status_missing'] = {
        'count': UX_Status_missing,
        'clean_name': 'UX_Status_missing'
    }

    for key, value in expected_ux_statuses.items():
        prcnt_of_ttl = value['count'] / len(response)
        value['prcnt_of_ttl'] = prcnt_of_ttl

    metric_desc = "Count of DyFo records of each A_UX_Status value"
    for key, value in expected_ux_statuses.items():
        metric_name = '{name}.{status}.cnt'.format(name=form_name, status=value['clean_name'])
        metric_value = value['count']
        METRIC_LIST.append({"metric_name": metric_name,
                            "metric_desc": metric_desc,
                            "metric_value": metric_value
                            }
                           )

    metric_desc = "Percent of total DyFo records of each A_UX_Status value"
    for key, value in expected_ux_statuses.items():
        metric_name = '{name}.{status}.prcnt_of_ttl'.format(name=form_name, status=value['clean_name'])
        metric_value = value['prcnt_of_ttl']
        METRIC_LIST.append({"metric_name": metric_name,
                            "metric_desc": metric_desc,
                            "metric_value": metric_value
                            }
                           )


def form_name_search(search_term="Integration Form", search_contains=False):
    """
    Pull all forms and check if their names contain a term.
    The API has a search term, but doesn't allow contains or starts with:
    https://docs.oracle.com/cloud/latest/marketingcs_gs/OMCAC/op-api-rest-2.0-assets-forms-get.html
    """

    username = os.environ['ELOQUA_USER']
    password = os.environ['ELOQUA_PASSWORD']
    company = os.environ['ELOQUA_COMPANY']
    elq = Eloqua(company=company, username=username, password=password)

    try:
        if PRINT_OUTPUT:
            export_filename = "monitor-pvc/testing/testingFormsFromApi.json"
            forms = load(open(export_filename, 'r'))
            print("Managed to pull sample records from local; no need to GET from Eloqua")
        else:
            fail = 1 / 0
    except (ZeroDivisionError, FileNotFoundError):
            forms = []
            loop = 1
            while True:
                response = requests.get("https://REDACTED.eloqua.com/api/REST/2.0/assets/forms?page=%s" % loop, auth=elq.auth)
                if PRINT_OUTPUT:
                    print(response)
                try:
                    if response.json()['elements']:
                        forms.extend(response.json()['elements'])
                    else:
                        break
                    loop += 1
                except JSONDecodeError:
                    break

    if PRINT_OUTPUT:
        with open(export_filename, 'w') as fopen:
            dump(forms, fopen)

    forms_matching_search = {}
    for row in forms:
        if search_contains:
            if search_term in row['name']:  # contains
                forms_matching_search[row['id']] = row['name']
        else:
            if search_term == row['name'][:len(search_term)]:  # starts with
                forms_matching_search[row['id']] = row['name']

    # if PRINT_OUTPUT:
    #     with open("%s" % FORMS_FILENAME, 'w') as fopen:
    #         dump(forms_matching_search, fopen)
    #     pprint(forms_matching_search)
    #
    return forms_matching_search


def form_definition_refresh(form_id, form_name):
    """ Refresh the form_definitions """
    form_definition = Form(username=os.environ['ELOQUA_USER'],
                           password=os.environ['ELOQUA_PASSWORD'],
                           company=os.environ['ELOQUA_COMPANY'],
                           form_id=form_id
                           )
    form_definition.write_form(form_definition_path(form_name))


def form_definition_path(form_name):
    return "{base_path}form_defintion_{form_name}.json".format(
        base_path=FORM_DEFINITION_PATH,
        form_name=form_name
    )


def low_traffic_hour():
    """Sunday mornings between 00:00 and 01:00"""
    # return True
    if (int(NOW_RALEIGH.weekday()) == 6 and
            0 < int(NOW_RALEIGH.strftime('%H')) < 2
    ):
        return True
    else:
        return False


if __name__ == '__main__':
    visor_eloqua_form()
