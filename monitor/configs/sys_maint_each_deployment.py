"""
Runs at the beginning of each deployment.
Performs the following:
 - Remove all pushgateway records; this allows any metric name changes made by
   a new deployment to replace the old metric names (000-09-27)
 - Removes the _last_success_unixtime metrics from Prometheus to avoid false alarms. 
   If they are not removed then Prometheus still believes the script should be running 
   and will throw errors.


000-05-08
Currently not in use as I'd have to add it to the jenkins build.

"""

import os
import sys
from pprint import pprint
import time
import urllib3
import requests
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone("America/New_York")

PRINT_OUTPUT = False
PRINT_OUTPUT = True  # devonly

EXPORTED_JOB_NAMES_REMOVED = []  # this is where I will add the names of jobs that have changed so that I don't get false alarms that they are no longer passing their "last_success_unixtime"

os.environ['REQUESTS_CA_BUNDLE'] = "/Users/westonagreene/Documents/RedHatWgreene/REDACTED.crt"
os.environ['SSL_CERT_FILE'] = "/Users/westonagreene/Documents/RedHatWgreene/REDACTED.crt"

def sys_maint_each_deployment(prometheus, pushgateway):
    """Compiler of all maintenance functions"""

    # time.sleep(60 * 5)  
        # wait 5 minutes as each build takes about 5 minutes; 
        # this is to avoid a race condition where this script may clear the old metric names
        # but the old scripts run again before the new scripts from the new build replace the old scripts.
        # 
        # Ultimately removed for fear that this process would continue too long and continue past the build.

    try:
        job_name = '{exported_job=~"visor_.*"}'  # backwards compatible to the old style of metrics
        if PRINT_OUTPUT:
            now_raleigh = datetime.now(TIMEZONE)
            print("\n", now_raleigh)
        clear_old_metric_names(job_name=job_name, prometheus=prometheus, pushgateway=pushgateway)
    except:
        pprint(sys.exc_info())

def clear_old_metric_names(job_name, prometheus, pushgateway):
    """
    pulls from prometheus all metrics related to job_name and removes them from Pushgateway
    """
    # Pull metrics from prometheus
    time_range = "10m"  # this is twice the scrape interval of prometheus from Pushgateway; this ensures prometheus has scraped from pushgateway within that timeframe
    get_url_var = ('%s/api/v1/query?query=%s[%s]&step=%s' % (prometheus, job_name, time_range, time_range))
    if PRINT_OUTPUT:
        print(get_url_var)
    get_response = requests.get(get_url_var).json()

    # if PRINT_OUTPUT:
    # #     pprint(get_response)
    # #     pprint(get_response['data'])
    #     pprint(get_response['data']['result'])

    # Format for removal
    metrics_to_remove = []
    for row in get_response['data']['result']:
        metrics_to_remove.append(
            [
                row["metric"]["__name__"],
                row["metric"]["exported_job"]
            ]
        )
    # if PRINT_OUTPUT:
    #     pprint(metrics_to_remove)
    metrics_to_remove_unique = set()
    for row in metrics_to_remove:
        metrics_to_remove_unique.add(row[1])
    if PRINT_OUTPUT:
        pprint(metrics_to_remove_unique)

    # delete from pushgateway
    for row in metrics_to_remove_unique:
        url_var = '{}/metrics/job/{}'.format(pushgateway, row)
        if PRINT_OUTPUT:
            print(url_var)
        delete_response = requests.delete(url_var)
        if PRINT_OUTPUT:
            print(delete_response)

    # # Prep to delete from Prometheus
    # metrics_to_remove = [
    #     "last_success_unixtime",
    #     "next_expected_unixtime"
    # ]
    # for row in get_response['data']['result']:
    #     if row["metric"]["__name__"] == "last_success_unixtime" \
    #     or row["metric"]["__name__"] == "next_expected_unixtime":
    #         metrics_to_remove.append(
    #             [
    #                 row["metric"]["__name__"],
    #                 row["metric"]["exported_job"]
    #             ]
    #         )
    # if PRINT_OUTPUT:
    #     print("metrics_to_remove from prom")
    #     pprint(metrics_to_remove)
    #
    # # delete from Prometheus
    # for row in metrics_to_remove:
    #     url_var = '{prometheus}/api/v1/admin/tsdb/delete_series?match[]={{__name__="{timeseries_name}"}}'.format(
    #         prometheus=prometheus,
    #         timeseries_name=row
    #         )
    #     if PRINT_OUTPUT:
    #         print(url_var)
    #     delete_response = requests.post(url_var)
    #     if PRINT_OUTPUT:
    #         print(delete_response)


if __name__ == '__main__':
    
    PROMETHEUS_TO_CLEAN = [
        {'prometheus': os.environ['PROMETHEUS_A'], 'pushgateway': os.environ['PUSHGATEWAY_A']},
        {'prometheus': os.environ['PROMETHEUS_B'], 'pushgateway': os.environ['PUSHGATEWAY_B']},
    ]

    for row in PROMETHEUS_TO_CLEAN:
        sys_maint_each_deployment(row['prometheus'], row['pushgateway'])
