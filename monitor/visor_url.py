import subprocess
import requests
import datetime
import os
import sys
import pytz
from function_defintions_visor import prometheus_registry_prep
import urllib3
from pprint import pprint

os.environ['PRINT_OUTPUT'] = "True"  # devonly
try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except (KeyError):
    PRINT_OUTPUT = False

TIMEZONE = pytz.timezone("America/New_York")

URLS_TO_PING = [
    #ViSOR
    {
        'metric_name': 'visor_dashboard',
        'urls': {
            'prod': "https://dashboard-visor.REDACTED.eloqua.com",
            'preprod': "https://dashboard-visor.REDACTED.redhat.com"
        }
    },
    {
        'metric_name': 'visor_grafana',
        'urls': {
            'prod': "https://grafana-visor.REDACTED.eloqua.com",
            'preprod': "https://grafana-visor.REDACTED.redhat.com"
        }
    },
    {
        'metric_name': 'visor_monitor',
        'urls': {
            'prod': "https://monitor-visor.REDACTED.eloqua.com",
            'preprod': "https://monitor-visor.REDACTED.redhat.com"
        }
    },
    {
        'metric_name': 'visor_prom',
        'urls': {
            'prod': "https://prom-a-visor.REDACTED.eloqua.com",  # intentionally not consistent because only URLs of key "prod" get alerted upon
            'b_prod': "https://prom-b-visor.REDACTED.eloqua.com",
            'a_preprod': "https://prom-a-visor.REDACTED.redhat.com",
            'b_preprod': "https://prom-b-visor.REDACTED.redhat.com"
        }
    },
    {
        'metric_name': 'visor_alert',
        'urls': {
            'prod': "https://alert-a-visor.REDACTED.eloqua.com",  # intentionally not consistent because only URLs of key "prod" get alerted upon
            'b_prod': "https://alert-b-visor.REDACTED.eloqua.com",
            'a_preprod': "https://alert-a-visor.REDACTED.redhat.com",
            'b_preprod': "https://alert-b-visor.REDACTED.redhat.com"
        }
    },
    {
        'metric_name': 'visor_pushgate',
        'urls': {
            'prod': "https://pushgate-a-visor.REDACTED.eloqua.com",  # intentionally not consistent because only URLs of key "prod" get alerted upon
            'b_prod': "https://pushgate-b-visor.REDACTED.eloqua.com",
            'a_preprod': "https://pushgate-a-visor.REDACTED.redhat.com",
            'b_preprod': "https://pushgate-b-visor.REDACTED.redhat.com"
        }
    },
    #Promtheus general purpose, probably to be deprecated soon
    {
        'metric_name': 'prometheus_general_prom',
        'urls': {
            'prod': "http://prom-prometheus.int.open.paas.redhat.com",
            'dev': "http://prom-prometheus-dev.int.open.paas.redhat.com"
        }
    },
    {
        'metric_name': 'prometheus_general_pgw',
        'urls': {
            'prod': "http://pgw-prometheus.int.open.paas.redhat.com",
            'dev': "http://pgw-prometheus-dev.int.open.paas.redhat.com"
        }
    },
    {
        'metric_name': 'prometheus_general_amg',
        'urls': {
            'prod': "http://amg-prometheus.int.open.paas.redhat.com",
            'dev': "http://amg-prometheus-dev.int.open.paas.redhat.com"
        }
    },
    # Other
    {
        'metric_name': 'workbench_daenerys',
        'urls': {
            'prod': "https://daenerys-workbenchprod.int.open.paas.redhat.com",
            'dev': "https://daenerys-workbenchdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'workbench_tyrion',
        'urls': {
            'prod': "https://tyrion-workbenchprod.int.open.paas.redhat.com",
            'dev': "https://tyrion-workbenchdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'workbench_leia',
        'urls': {
            'prod': "https://leia-workbenchprod.int.open.paas.redhat.com",
            'dev': "https://leia-workbenchdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'workbench_sherlock',
        'urls': {
            'prod': "https://sherlock-workbenchprod.int.open.paas.redhat.com",
            'dev': "https://sherlock-workbenchdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'workbench_columbo',
        'urls': {
            'prod': "https://columbo-workbenchprod.int.open.paas.redhat.com",
            'dev': "https://columbo-workbenchdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'workbench_columbo_backend',
        'urls': {
            'prod': "https://columbo-back-end-workbenchprod.int.open.paas.redhat.com",
            'dev': "https://columbo-back-end-workbenchdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'workbench_gandalf',
        'urls': {
            'prod': "https://gandalf-workbenchprod.int.open.paas.redhat.com",
            'dev': "https://gandalf-workbenchdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'workbench_gandalf_backend',
        'urls': {
            'prod': "https://gandalf-backend-workbenchprod.int.open.paas.redhat.com",
            'dev': "https://gandalf-backend-workbenchdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'workbench_mass_tactic',
        'urls': {
            'prod': "https://mass-tactic-workbenchprod.int.open.paas.redhat.com/",
            'dev': "https://mass-tactic-workbenchdev.int.open.paas.redhat.com/"
        },
    },
    {
        'metric_name': 'workbench_dwm',
        'urls': {
            'prod': "https://dwm-workbenchprod.int.open.paas.redhat.com/",
            'dev': "https://dwm-workbenchdev.int.open.paas.redhat.com/"
        },
    },
    {
        'metric_name': 'workbench',
        'urls': {
            'prod': "https://workbench-workbenchprod.int.open.paas.redhat.com/",
            'dev': "https://workbench-workbenchdev.int.open.paas.redhat.com/"
        },
    },
    {
        'metric_name': 'workflows',
        'urls': {
            'prod': "https://workflows-workflowsprod.int.open.paas.redhat.com",
            'dev': "https://workflows-workflowsdev.int.open.paas.redhat.com"
        },
    },
    {
        'metric_name': 'aip',
        'urls': {
            'prod': "https://aip.int.open.paas.redhat.com/",
            'dev': "https://dev-aip.int.open.paas.redhat.com/",
            'stage': "https://stage-aip.int.open.paas.redhat.com/"
        },
    },
    {
        'metric_name': 'hub',
        'urls': {
            'prod': "https://hub.int.open.paas.redhat.com/",
            'dev': "https://dev-hub.int.open.paas.redhat.com/",
            'stage': "https://stage-hub.int.open.paas.redhat.com/"
        },
    },
    {
        'metric_name': 'site_4tm_upload_wizard',  # "site" prepended to the metricName because prometheus metric names cannot start with a number.
        'urls': {
            'prod': "http://52.1.31.000/?tkn=fc59c0e1-000-000b-bec2-bb4f000dabd6",
        },
    },
    {
        'metric_name': 'ansible_hubspot_api',
        'urls': {
            'prod': "https://ans-hbspt-elq-fidget-hub.b9ad.pro-us-east-1.openshiftapps.com/api/v1/",
            'dev': "https://ans-hbspt-elq-fidget-hub-dev.b9ad.pro-us-east-1.openshiftapps.com/api/v1/",
        },
    },
    {
        'metric_name': 'qwiklab_api',
        'urls': {
            'prod': "https://qwlb-rhmo-qwlb.b9ad.pro-us-east-1.openshiftapps.com/",
        },
    },
]
for ROW in URLS_TO_PING:
    if 'monitor' not in ROW:
        ROW['monitor'] = 'true'

SERVERS_TO_PING = [
    {
        'metric_name': 'sftp_redhat_com',
        'servers': {
            'prod': "sftp.redhat.com",
        },
    },
]
for ROW in SERVERS_TO_PING:
    if 'monitor' not in ROW:
        ROW['monitor'] = 'true'


def visor_url():
    """
    combines all functions
    """
    os.environ['HTTP_PROXY'] = "REDACTED.redhat.com:000"  # this allows less restircted communication with external URLs, necessary for pinging them
    os.environ['HTTPS_PROXY'] = "REDACTED.redhat.com:000"

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # to prevent log noise of insecure warnings

    scriptTime_start = datetime.datetime.now(TIMEZONE)

    # ping all URL and record responses
    metric_list = []

    for site in range(len(URLS_TO_PING)):
        responses = []
        for url in URLS_TO_PING[site]['urls'].items():
            response = url_down(url[1])  # returns a 1 or a 0
            responses.append([url[0], response])
        URLS_TO_PING[site]['responses'] = responses  # add back to the original dictionary

        for response in URLS_TO_PING[site]['responses']:
            if URLS_TO_PING[site]['monitor'] == 'true' and \
                    response[0] == 'prod':
                monitor = 'true'
            else:
                monitor = 'false'
            metric_list.append({
                "metric_name": "{}-{}".format(URLS_TO_PING[site]["metric_name"], response[0]),
                "metric_value": response[1],
                "monitor": monitor
            })

    for site in range(len(SERVERS_TO_PING)):
        responses = []
        for server in SERVERS_TO_PING[site]['servers'].items():
            response = server_down(server[1])  # returns a 1 or a 0
            responses.append([server[0], response])
        SERVERS_TO_PING[site]['responses'] = responses  # add back to the original dictionary

        for response in SERVERS_TO_PING[site]['responses']:
            if SERVERS_TO_PING[site]['monitor'] == 'true' and \
                    response[0] == 'prod':
                monitor = 'true'
            else:
                monitor = 'false'
            metric_list.append({
                "metric_name": "{}-{}".format(SERVERS_TO_PING[site]["metric_name"], response[0]),
                "metric_value": response[1],
                "monitor": monitor
            })


    if PRINT_OUTPUT:
        print("URLs checked", scriptTime_start)

    # prometheus_registry = prometheus_registry_prep(
    #     metric_list=metric_list, job_name=os.path.basename(__file__)
    # )
    # return prometheus_registry

    os.environ['HTTP_PROXY'] = ""  # Because these proxies give more access than is defined by the egress rules (https://REDACTED.redhat.com/paas/egress-firewall-preprod), I remove that access for security.
    os.environ['HTTPS_PROXY'] = ""

    return metric_list


def url_down(url):
    try:
        response = requests.get(url, verify=False)
        if 000 <= response.status_code < 000:
            return 0
        else:
            if PRINT_OUTPUT:
                print(
                    "URL down\n",
                    url,
                    "status:",
                    response.status_code
                )
            return 1
    except:
        pprint(sys.exc_info())
        return 1


def server_down(server):
    """
    Performs a ping through the local terminal and returns a 1 if the server doesn't respond
    """

    # The "-c 1" tells to ping only once. The "2>/dev/null" hides all output, including errors.
    command = "ping -c 1 %s 2>/dev/null" % server
    try:
        subprocess.check_output(command, shell=True)
        return 0
    except subprocess.CalledProcessError:
        return 1


if __name__ == '__main__':
    visor_url()
