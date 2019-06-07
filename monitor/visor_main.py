"""
Runs continuously in the visorpythonmonitoring pod in OpenPaaS.
Triggers each monitoring python file.
Created: 000-08-10_10.43

Must be called "visor_main.py" because the python container on openshift automatically executes files called "visor_main.py"
"""
import datetime
import time
import os
import sys
from multiprocessing import Process
from function_defintions_visor import prometheus_registry_prep, prometheus_registry_push
from pprint import pprint

os.environ['PRINT_OUTPUT'] = "True"  # devonly
try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except (KeyError):
    PRINT_OUTPUT = False
# PRINT_OUTPUT = True

DEFAULT_FREQ = 1 * 60 * 60  # Second * minute * hour

# # to indicate which cronjob triggered the script
# try:
#     ARGUMENT_FREQUENCY = sys.argv[1]  # sys.argv[1] should be passed to visor_main.py by the cronjob, see the deployment config in the configs/deploy.yaml
# except (IndexError):
#     ARGUMENT_FREQUENCY = 60


def visor_main():
    """main function of visor_main.py"""

    for row in SCRIPTS_TO_RUN:
        subProcess = Process(target=script_wrapper, args=(row['file_name'], row['function'], None, row['frequency'], ))
        if PRINT_OUTPUT:
            print("Triggering subprocess for ", row['file_name'])
        try:  # try so that if the subprocess fails the main loop script (visor_main.py) continues.
            subProcess.start()
        except:
            pprint(sys.exc_info())
            pass
    time.sleep(000)  # for testing, sleep forever to allow time for subProcesses to complete

    # while True:
    #     for row in SCRIPTS_TO_RUN:
    #         now = datetime.datetime.now()
    #         seconds_since_midnight = int((now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())  # subtracts away the year, month, and day, leaving just the hour, minute, second, and microseconds
    #         if seconds_since_midnight % row['frequency'] == 0:  # if the current second of the day divided by the frequency of the script in seconds has no remainder, then it's time to trigger again.
    #             subProcess = Process(target=script_wrapper, args=(row['file_name'], row['function'], None, row['frequency'], ))
    #             if PRINT_OUTPUT:
    #                 print("Triggering subprocess for ", row['file_name'])
    #             try:  # try so that if the subprocess fails the main loop script (visor_main.py) continues.
    #                 subProcess.start()
    #             except:
    #                 pprint(sys.exc_info())
    #                 pass
    #
    #         # loopStart = datetime.datetime.now()
    #         # if row['last_run'] == ''\
    #         #         or loopStart - row['last_run'] > datetime.timedelta(seconds=row['frequency']):  # has enough time passed
    #         #     row['last_run'] = loopStart
    #         # # if str(ARGUMENT_FREQUENCY) == str(row['frequency']):
    #         #     subProcess = Process(target=script_wrapper, args=(row['file_name'], row['function'], None, row['frequency'], ))
    #         #     if PRINT_OUTPUT:
    #         #         print("Triggering subprocess for ", row['file_name'])
    #         #     try:  # try so that if the subprocess fails the main loop script (visor_main.py) continues.
    #         #         subProcess.start()
    #         #     except:
    #         #         pprint(sys.exc_info())
    #         #         pass
    #
    #         # else:
    #         #     if PRINT_OUTPUT:
    #         #         print(
    #         #             "Running files of frequency %s, but file %s has frequency %s" % (
    #         #                 ARGUMENT_FREQUENCY,
    #         #                 row['file_name'],
    #         #                 row['frequency']
    #         #             )
    #         #         )
    #     # This keeps the continuous loop, checking every second whether
    #     # enough time has lapsed to trigger the script again.
    #     time.sleep(1)  # TODO move to cronjobs


def script_wrapper(file_name, function, args=None, frequency=DEFAULT_FREQ):  # frequency is placed after args because in script_wrapper is used elsewhere where frequency is not specified
    """
    Perform steps that should be performed for each monitoring script:
        Last Success timestamp
        Script duration
        next_expected_unixtime
    """
    subprocess_time_start = datetime.datetime.now()

    if PRINT_OUTPUT:
        print("Starting file ", file_name)
    if args:
        metric_list = function(args)
    else:
        metric_list = function()

    if not metric_list:
        if PRINT_OUTPUT:
            print("TypeError for NoneType, or in other words, nothing was returned by the function", file_name)
        return


    if frequency is None:
        frequency = DEFAULT_FREQ
    #
    # job_name = file_name
    # response_type = type(response)
    # if str(response_type) == '<class \'list\'>':  # This is specifically for CDO monitoring where the job_name is not necssarily the file_name
    #     metric_list = response[0]
    #     job_name = response[1]
    # else:
    #     metric_list = response

    for row in metric_list:
        row['freq'] = frequency

    # pprint(metric_list)

    prometheus_registry = prometheus_registry_prep(
        metric_list=metric_list, job_name=file_name
    )

    subprocess_time_end = datetime.datetime.now()
    script_time_duration = subprocess_time_end - subprocess_time_start
    last_success_unixtime = subprocess_time_end.timestamp()
    next_expected_unixtime = (subprocess_time_end + datetime.timedelta(seconds=frequency)).timestamp()

    # Prometheus logging
    metric_desc = "%s%s" % ("https://REDACTED.redhat.com/marketing-ops/visor/blob/master/visorPythonMonitoring/", file_name)
    metric_list = [
        {"metric_name": "last_success_unixtime", "metric_desc": metric_desc, "metric_value": last_success_unixtime, "monitor": "false"},  # This is monitored by next_expected_unixtime
        {"metric_name": "next_expected_unixtime", "metric_desc": metric_desc, "metric_value": next_expected_unixtime, "monitor": "true"},  # If the script misses it's run time, we need to know; but by not having the alert trigger at a strict `> 0` standard, we allow for bad script that is already known to have a problem to not continuously throw false alarms
        {"metric_name": "script_duration_seconds", "metric_desc": metric_desc, "metric_value": script_time_duration.seconds, "monitor": "true"},  # If the script takes an exhorbitant amount of time, then something is wrong
    ]

    prometheus_registry = prometheus_registry_prep(
        job_name=file_name,
        metric_list=metric_list,
        prometheus_registry=prometheus_registry,
        )

    # if pushgateway != "all":  # in some cases, a metric would be best suited to appear on all prometheus instances.
    #     prometheus_registry_push(
    #         job_name=job_name,
    #         prometheus_registry=prometheus_registry,
    #         pushgateway=pushgateway,
    #         )
    # else:
    pushgateways = [
        os.environ['PUSHGATEWAY_A'],
        os.environ['PUSHGATEWAY_B'],
    ]
    for row in pushgateways:
        prometheus_registry_push(
            job_name=file_name,
            prometheus_registry=prometheus_registry,
            pushgateway=row,
            )

    if PRINT_OUTPUT:
        print("Completed file ", file_name)


if __name__ == '__main__':
    
    SCRIPTS_TO_RUN = [
        # {'file_name': 'visor_url', 'frequency': 1 * 60},
        # {'file_name': 'visor_memory', 'frequency': DEFAULT_FREQ},
        {'file_name': 'visor_eloqua_cdo', 'frequency': DEFAULT_FREQ},
        # {'file_name': 'visor_eloqua_form', 'frequency': DEFAULT_FREQ},
        # {'file_name': 'visor_eloqua_segment', 'frequency': DEFAULT_FREQ},
        # {'file_name': 'visor_eloqua_shared_list', 'frequency': DEFAULT_FREQ},
        # {'file_name': 'visor_eloqua_cdo_cleanup', 'frequency': DEFAULT_FREQ},
    ]
    for SCRIPT in SCRIPTS_TO_RUN:
        SCRIPT['last_run'] = ''
        SCRIPT['function'] = getattr(__import__(SCRIPT['file_name'], fromlist=[SCRIPT['file_name']]),
                                    SCRIPT['file_name'],
                                    )

    # print(os.path.basename(__file__))
    visor_main()
