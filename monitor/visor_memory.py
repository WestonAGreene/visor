"""
Run the `$ df` command to track the memory usage of ViSOR pods
"""
import subprocess
import os
import requests
from function_defintions_visor import prometheus_registry_prep
# from visor_main import script_wrapper
# from pprint import pprint

try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except (KeyError):
    PRINT_OUTPUT = False
# PRINT_OUTPUT = True  # devonly
if PRINT_OUTPUT:
    from pprint import pprint

PVC_TO_MONITOR = [
    'alert-a-pvc',
    'alert-b-pvc',
    'grafana-pvc',
    'monitor-pvc',
    'prom-a-pvc',
    'prom-b-pvc',
    'pushgate-a-pvc',
    'pushgate-b-pvc',
]

MOUNT_PATH = "/opt/app-root/src/"


def visor_memory():
    """
    Combines all functions
    """
    # prep for prometheus
    metric_desc = "Memory usage, according to `$ df`, from the pod."
    metric_list = []

    for pvc in PVC_TO_MONITOR:
        try:
            memory_percent = subprocess.check_output([
                "df",
                "-h",
                pvc
            ])
            if PRINT_OUTPUT:
                pprint(memory_percent)
            memory_percent = str(memory_percent)
            memory_percent = memory_percent.split('\\n')
            if PRINT_OUTPUT:
                pprint(memory_percent)
            # characters_to_keep = len(pvc)-2
            # text_to_search = " /%s" % pvc[:characters_to_keep]
            # if PRINT_OUTPUT:
            #     pprint(text_to_search)
            for row in memory_percent:
                if pvc in row:
                    memory_percent = row
            if PRINT_OUTPUT:
                pprint(memory_percent)
            characters_to_keep = 6 + len(pvc) + len(MOUNT_PATH)
            memory_percent = memory_percent[-characters_to_keep:]
            if PRINT_OUTPUT:
                pprint(memory_percent)
            memory_percent = ''.join(CHAR for CHAR in memory_percent if CHAR.isdigit())
            if PRINT_OUTPUT:
                pprint(memory_percent)
            memory_percent = int(memory_percent)
            if PRINT_OUTPUT:
                print("app_name:", pvc, "memory_percent:", memory_percent)
        except:
            memory_percent = -1

        metric_list.append({"metric_name": pvc, "metric_desc": metric_desc, "metric_value": memory_percent})

    # prometheus_registry = prometheus_registry_prep(metric_list=metric_list, job_name=os.path.basename(__file__))
    # return prometheus_registry
    return metric_list


if __name__ == '__main__':
    # script_wrapper('visor_memory', visor_memory)  # added to visor_main.py and therefore no longer treated separately
    visor_memory()
