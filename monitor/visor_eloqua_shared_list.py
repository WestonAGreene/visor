"""
Author: wgreene
Created: 000-04-25_17.16
How to get a Shared List's ID:
    open shared list >
    Settings ">>" >
    Field Summary >
    "&ContactInfoID=" URL parameter;
See visor_eloqua_shared_list.img0 and visor_eloqua_shared_list.img1 for examples

000-03-04
Half way updated to standard formatting.

"""

import os
import datetime
from pyeloqua import Eloqua
import pytz
import requests
from function_defintions_visor import prometheus_registry_prep


# os.environ['PRINT_OUTPUT'] = True  # devonly
try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except (KeyError):
    PRINT_OUTPUT = False
if PRINT_OUTPUT:
    from pprint import pprint


def visor_eloqua_shared_list():
    """function to be run by visor_main.py"""
    timezone = pytz.timezone("America/New_York")
    now_raleighTimezone = datetime.datetime.now(timezone)
    if PRINT_OUTPUT:
        print(datetime.datetime.strftime(now_raleighTimezone, '%Y-%m-%d %H:%M:%S'),
              "Starting script DATA_HOURLY_ELOQUA_SHAREDLIST",
              "This script will:",
              "check the count in several chosen shared lists.",
              "So that:",
              "we are notified when there are concerning counts in the shared lists, such as a count that indicates a program isn't removing records as it should or a count that indicates a program is adding more records than it should.",
              "\n",
              )


    sharedListsToMonitor = [
        {'sharedListName': 'CLS - Monitoring: 000 - CONTROLLER', 'sharedListId': '000'},
        {'sharedListName': 'CLS - Monitoring: 000 - Communities', 'sharedListId': '000'},
        {'sharedListName': 'CLS - Monitoring: 000 - RH Mktg Programs', 'sharedListId': '000'},
        {'sharedListName': 'CLS - Monitoring: 000 - Regions', 'sharedListId': '000'},
        {'sharedListName': 'CLS - Monitoring: 000 - Regions - APAC', 'sharedListId': '000'},
        {'sharedListName': 'CLS - Monitoring: 000 - Regions - EMEA', 'sharedListId': '000'},
        {'sharedListName': 'CLS - Monitoring: 000 - Regions - LATAM', 'sharedListId': '000'},
        {'sharedListName': 'CLS - Monitoring: 000 - Regions - NA', 'sharedListId': '000'},
        {'sharedListName': 'CLS - Suspend Marketing Master List', 'sharedListId': '000'},
        {'sharedListName': 'CLS: Suspend Marketing Tracking', 'sharedListId': '000'},
        {'sharedListName': 'Email Regulations Compliant - no | Pending - yes', 'sharedListId': '000'},
        {'sharedListName': 'Email Regulations Compliant - no | Pending - no', 'sharedListId': '000'},
        {'sharedListName': 'Manual Send Warmup Email - Master', 'sharedListId': '000'},
        # , {'sharedListName': 'DWM - Queue for Data Washing Machine' \
        #    , 'sharedListId': '000'
        #   }
    # ,{'sharedListName'          :'ALF - Update Lead - Tracking'
    #  ,'sharedListId'            :'000'
    #  }
    # ,{'sharedListName'          :'ALF - Create Lead - Tracking'
    #  ,'sharedListId'            :'000'
    #  }
    # ,{'sharedListName'          :'CLS: Programs - Partner-NA'
    #  ,'sharedListId'            :'000'
    #  }
    # ,{'sharedListName'          :'CLS: Programs - ABM-NA'
    #  ,'sharedListId'            :'000'
    #  }
    ]

    for sharedList in sharedListsToMonitor:
        sharedList['emailList'],sharedList['sharedListCount'] = sharedListGetContacts(sharedListId = sharedList['sharedListId'])
        if PRINT_OUTPUT:
            print('\n%s current count: %s' % (sharedList['sharedListName'], sharedList['sharedListCount']))

    metric_desc = 'All sharedlists being monitored'
    metric_list = []
    for row in sharedListsToMonitor:
        metric_list.append({"metric_name": row["sharedListName"], "metric_desc": metric_desc, "metric_value": row['sharedListCount']})
    # prometheus_registry = prometheus_registry_prep(metric_list=metric_list, job_name=os.path.basename(__file__))

    # return(prometheus_registry)
    return metric_list




    """
    From an email from Jeremy
    To add an "add to list" sync action to a bulk import:

    bulk = Bulk(username, password, etc...)

    bulk.imports('contacts')
    bulk.add_syncaction_list(action='add', list_id=000)

    then follow the rest of the examples to completion.
    To remove from shared list, swap out action='add' for action='remove'

    for context, here's what that code is doing (same idea, different in terms of actual api calls, because Eloqua docs don't have an exact example...):

    http://docs.oracle.com/cloud/latest/marketingcs_gs/OMCAC/op-api-bulk-2.0-contacts-syncActions-post.html
    """


def sharedListGetContacts(
    sharedListId,
    viewId=000, #https://REDACTED.eloqua.com/api/rest/1.0/assets/contact/views,
    eloquaApiBaseUrl="https://REDACTED.eloqua.com/api/rest/2.0",
    ):
    """Pulls the count from Eloqua for the shared list"""

    #log in
    username    = os.environ['ELOQUA_USER'      ]
    password    = os.environ['ELOQUA_PASSWORD'  ]
    company     = os.environ['ELOQUA_COMPANY'   ]
    elq         = Eloqua(company=company, username=username, password=password)

    sharedListUrl = '{baseUrl}/data/contact/view/{viewId}/contacts/list/{sharedListId}'.format(
        baseUrl=eloquaApiBaseUrl,
        viewId=viewId,
        sharedListId=sharedListId,
        )
    sharedListGet       = requests.get(sharedListUrl, auth=elq.auth).json()
    sharedListEmails    = []
    [sharedListEmails.append(row['C_EmailAddress']) for row in sharedListGet['elements']]
    sharedListCount     = sharedListGet['total']
    return(sharedListEmails, sharedListCount)


if __name__ == '__main__':
    visor_eloqua_shared_list()
