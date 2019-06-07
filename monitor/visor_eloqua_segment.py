"""
Pulls the current count from a segment.

US000
changeReport.ContactUploadProcess.ReduceTheInefficientTimeSpentByVeritcurl.Wgreene.000-01-08
https://docs.google.com/spreadsheets/d/1EbgqNk-vJIU9BaU5XXNyxgi2u6LrJsFtOiyfaFVWUf0
Created 000-01-26 20:57
Modified 000-02-20 16:32
"""

import os
import datetime
import time
import sys
import pytz
import requests
from pyeloqua import Eloqua
from function_defintions_visor import prometheus_registry_prep
from pprint import pprint

SEG_RECAL_WAIT_TIME = 15  # minutes

try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except (KeyError):
    PRINT_OUTPUT = False
# PRINT_OUTPUT = True  # devonly


TIMEZONE = pytz.timezone('America/New_York')
TIME_IN_RALEIGH = datetime.datetime.now(TIMEZONE)
TIME_IN_RALEIGH_PRINTABLE = datetime.datetime.strftime(TIME_IN_RALEIGH, '%Y-%m-%d %H:%M:%S')

SEGMENTS_TO_COUNT = [
    {'segment_id': 000, 'segment_name': "Cntcts actv 3m | pndng - y | wrmd - y | wrmd lst wk - n"},
    {'segment_id': 000, 'segment_name': "Cntcts w inq. rec. wthn 1m | pndng - y | wrmble - y"},
    {'segment_id': 000, 'segment_name': "Cntcts pndng - y | email snds wthn 1m > 2"},
    {'segment_id': 000, 'segment_name': "Cntcts Mdfd Last 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Crtd Last 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Crtd frm C.Uploads.Members Last 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Mdfd by DWM Last 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts in Elq"}, # , 'monitor': "false"}, I have chosen to monitor total contacts as I hope that my monitoring will be capable of handling a continuously growing metric and maybe the monitoring will catch when contacts are deleted.
    {'segment_id': 000, 'segment_name': "Cntcts Mdfd by DWM CV Last 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Ext Lead Fnnl Last 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Ext MLSM Last 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Entrd CLS Last 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Most Active"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Active"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Inactive"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Internal"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Invalid"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Lapsed", 'monitor': "false"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Lapsing", 'monitor': "false"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Pending"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Unconventional"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Blank"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Most Active 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Inactive 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Internal 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Invalid 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Lapsed 24 Hrs", 'monitor': "false"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Lapsing 24 Hrs", 'monitor': "false"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta One-time Reset 24 Hrs"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta Pending 24 Hrs"},
    {'segment_id': 000, 'segment_name': "INC000.gdprRisk.de.000-07-19"},
    {'segment_id': 000, 'segment_name': "INC000.gdprRisk.euAndNotDe.000-07-19"},
    {'segment_id': 000, 'segment_name': "Cntcts Eng Sta One-time Reset"},
    {'segment_id': 000, 'segment_name': "Cntcts w CLS Suspend Marketing"},
    {'segment_id': 000, 'segment_name': "Cntcts w CLS CCEE"},
    {'segment_id': 000, 'segment_name': "Manual Send Warmup Email - KPI"},
    # {'segment_id': 000, 'segment_name': "Cntcts GDPR Never Warmed"},
    # {'segment_id': 000, 'segment_name': "Master Exclude Replica"},
    # {'segment_id': 000, 'segment_name': "Cntcts Eng Sta One-time Reset_OLD"}, Quit refreshing for some reason. 000-08-17
]


def visor_eloqua_segment():
    """Combines all functions"""

    if PRINT_OUTPUT:
        print(TIME_IN_RALEIGH_PRINTABLE,
              "Starting script visor_eloqua_segment\n",
              "This script will:",
              "for a list of Eloqua segments, refresh them and record their new counts.",
              "\n\n\n",
              )

    # log in
    username = os.environ['ELOQUA_USER']
    password = os.environ['ELOQUA_PASSWORD']
    company = os.environ['ELOQUA_COMPANY']
    elq = Eloqua(company=company, username=username, password=password)

    for row in SEGMENTS_TO_COUNT:
        if 'monitor' not in row:
            row['monitor'] = "true"

    # Trigger refresh
    for row in SEGMENTS_TO_COUNT:
        row['time_previous_calc'] = segment_refresh(segment_id=row['segment_id'], elq_auth=elq)
        time.sleep(10)  # small wait to prevent overloading Eloqua

    # Pull counts
    for row in SEGMENTS_TO_COUNT:
        row['count'] = segment_get_count(segment_id=row['segment_id'], time_previous_calc=row['time_previous_calc'], elq_auth=elq)

    # Push to prometheus
    metric_desc = "Count returned by an Eloqua Segment."
    metric_list = []
    for row in SEGMENTS_TO_COUNT:
        metric_list.append({
            'metric_name': row['segment_name'],
            'metric_desc': metric_desc,
            'metric_value': row['count'],
            'monitor': row['monitor']
            })
    # prometheus_registry = prometheus_registry_prep(metric_list=metric_list, job_name=os.path.basename(__file__))
    # return prometheus_registry
    return metric_list


def segment_refresh(
        segment_id,
        elq_auth,
        elq_api_endpoint="https://REDACTED.eloqua.com/api/rest/2.0/assets/contact/segment/",
):
    """
    Trigger a refresh of the segment
    """

    # Get segment current state
    segment_url = '%s%s' % (elq_api_endpoint, segment_id)
    get_response = requests.get('%s/count' % segment_url, auth=elq_auth.auth)
    time_previous_calc = get_response.json()['lastCalculatedAt']

    # Tell segment to refresh
    requests.post('%squeue/%s' % (elq_api_endpoint, segment_id), auth=elq_auth.auth)

    if PRINT_OUTPUT:
        print("Triggered refresh for segment_id ", segment_id)

    return time_previous_calc


def segment_get_count(
        segment_id,
        time_previous_calc,
        elq_auth,
        elq_api_endpoint="https://REDACTED.eloqua.com/api/rest/2.0/assets/contact/segment/",
):
    """
    Pull the segments count when the refresh finishes
    """

    # Get segment's new state
    segment_url = '%s%s' % (elq_api_endpoint, segment_id)
    get_response = requests.get('%s/count' % segment_url, auth=elq_auth.auth)
    seg_last_calculated = get_response.json()['lastCalculatedAt']
    if PRINT_OUTPUT:
        print('\ntime_previous_calc', time_previous_calc,
              '\nseg_last_calculated', seg_last_calculated,
              "\nsegment_url = ", segment_url
              )

    error_message = None
    while_count = 0
    if PRINT_OUTPUT:
        print('\nWaiting for segment to recalculate.')
    while while_count < (SEG_RECAL_WAIT_TIME * 60 / 10):
        get_response = requests.get('%s/count' % segment_url, auth=elq_auth.auth)
        seg_last_calculated = get_response.json()['lastCalculatedAt']
        while_count += 1
        if seg_last_calculated != time_previous_calc:
            break
        if PRINT_OUTPUT:
            print('Waiting an additional 10 seconds.')
        time.sleep(10)
    else:
        error_message = ('Segment {segment_id} exceeded {SEG_RECAL_WAIT_TIME} minutes to recalculate'.format(segment_id=segment_id, SEG_RECAL_WAIT_TIME=SEG_RECAL_WAIT_TIME))
        print(TIME_IN_RALEIGH_PRINTABLE, error_message)

    if error_message:
        segment_count = -1
    else:
        segment_count = get_response.json()['count']

    return segment_count


if __name__ == '__main__':
    visor_eloqua_segment()


# # testing:
# from pyeloqua import Eloqua
# import requests
# import os
# username = os.environ['ELOQUA_USER']
# password = os.environ['ELOQUA_PASSWORD']
# company = os.environ['ELOQUA_COMPANY']
# elq = Eloqua(company=company, username=username, password=password)
# requests.post("https://REDACTED.eloqua.com/api/rest/2.0/assets/contact/segment/queue/000", auth=elq_auth.auth)
