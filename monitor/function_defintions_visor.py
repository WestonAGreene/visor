"""
#Author     : wgreene
#Created    : 000-02-22_05.58
#Modified   : 000-02-22_05.58
#Description: This script contains general use functions I've come to like.
from function_defintions_visor
"""
import ssl
import urllib
import sys
from datetime import datetime
import os
import pytz
from slugify import slugify
from prometheus_client import CollectorRegistry, pushadd_to_gateway, Gauge
from pprint import pprint

try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except (KeyError):
    PRINT_OUTPUT = False
PRINT_OUTPUT = True  # devonly


def format_text_for_vars(ugly_text):
    """Recieves text that will not look clean in or will be rejected as a variable and tidies it up"""
    return(slugify(ugly_text).replace("-", "_"))


def prometheus_registry_prep(metric_list, job_name, prometheus_registry=None):
    """Prepares the provided information to be passed to prometheus_registry_push"""

    if prometheus_registry is None:
        prometheus_registry=CollectorRegistry()
    # pprint(prometheus_registry.__dict__)

    # gitlab_base_visorpython_url = "https://REDACTED.redhat.com/marketing-ops/visor/blob/master/visorPythonMonitoring/"

    if str(type(metric_list)) != "<class 'list'>":
        exception = "metric_list must be a list of dictionaries of metric_name, metric_desc, and metric_value"
        print(exception)
        Exception(exception)

    job_name = format_text_for_vars(job_name)  # every job name must be unique in pushgateway
    
    for metric in metric_list:
        metric['metric_name'] = format_text_for_vars(metric['metric_name'])
        # metric['metric_desc'] = "%s\n%s%s" % (metric['metric_desc'],
        #                                       gitlab_base_visorpython_url,
        #                                       job_name,  # yes, this assumes that the job_name is also the file name of the script
        #                                       )

        labels = {}
        labels['original_name'] = metric['metric_name']

        if 'monitor' in metric:
            labels['monitor'] = metric['monitor']
        else:
            labels['monitor'] = 'true'

        default_freq = 1 * 60 * 60  # Second * minute * hour
        if 'freq' in metric:
            labels['freq'] = metric['freq']
        else:
            labels['freq'] = default_freq

        if 'custom_label' in metric:
            labels['custom_label'] = metric['custom_label']

        gauge = Gauge(
            metric['metric_name'],
            '',
            list(labels.keys()),
            registry=prometheus_registry
        )
        gauge.labels(*labels.values()).set(metric['metric_value'])

    # if PRINT_OUTPUT:
    #     print("\n\nMetrics prepared to be pushed to Prometheus")
    #     for metric in metric_list:
    #         print(metric['metric_name'], metric['metric_value'])
    #     print("\n\nMetrics prepared to be pushed to Prometheus")

    return prometheus_registry

    
def prometheus_registry_push(job_name, prometheus_registry, pushgateway=os.environ['PUSHGATEWAY_A']):
    """Pushes the provided information to pushgateway where it will be scraped by Prometheus"""

    job_name = format_text_for_vars(job_name)  # every job name must be unique in pushgateway

    try:
        if PRINT_OUTPUT:
            print("\n", pushgateway)
            pprint(job_name)
            # pprint(prometheus_registry.__dict__['_collector_to_names'])
            # from prometheus_client.parser import text_string_to_metric_families
            # for row in prometheus_registry._names_to_collectors:
            #     for family in text_string_to_metric_families(row):
            #         print("Name: {0} Labels: {1} Value: {2}".format(*sample))
            # prometheus_registry._names_to_collectors["crtd"]._metrics['crtd', 'true', '000']._value._value
            gauges = list(prometheus_registry._names_to_collectors)
            for row in gauges:
                gauge_name = list(prometheus_registry._names_to_collectors[row]._metrics.items())[0][0]
                print(row, prometheus_registry._names_to_collectors[row]._metrics[gauge_name]._value._value)

        pushadd_to_gateway(pushgateway, job=job_name, registry=prometheus_registry)
    except (ssl.SSLCertVerificationError, urllib.error.URLError):
        print("Error handled: ssl.SSLCertVerificationError or urllib.error.URLError: access to pushgateway was unverified and therefore rejected")



def printObject(object_to_print, keysOrValues="keys", rowsToPrint=1):
    try:
        objectType = type(object_to_print)
        if   str(objectType) == '<class \'list\'>':
            recordsToPrint = object_to_print[0:rowsToPrint] if rowsToPrint != 0 else object_to_print
            listFields = [row for row in recordsToPrint[0]]; listFields.sort()
            maxFieldNameLength = max(len(fieldName) for fieldName in listFields)
            for row in recordsToPrint:
                for field in listFields:
                    print(field.ljust(maxFieldNameLength) + ': ' + row[field])
        elif str(objectType) == '<class \'dict\'>':
            if keysOrValues == 'keys':
                dictKeys = []
                [dictKeys.append(row) for row in object_to_print.keys()]
                dictKeys.sort()
                maxFieldNameLength = max(len(row) for row in dictKeys)
                for row in dictKeys:
                    print(row.ljust(maxFieldNameLength),': ',object_to_print[row])
            else:
                dictValues = []
                [dictValues.append((rowValue, rowKey)) for rowKey,rowValue in object_to_print.items()]
                dictValues = sorted(dictValues, reverse=True)
                maxFieldNameLength = max(len(str(row[0])) for row in dictValues)
                loopCount = 0
                for row in dictValues:
                    print(str(row[0]).ljust(maxFieldNameLength),': ',row[1]) if loopCount < 15 else None
                    loopCount += 1
        else:
            print('Unsupported object type: ' + str(objectType))
        return;
    except:
        pprint(sys.exc_info())
        None


def export_json_to_csv(json, unique_name):
    """
    Converts json into a CSV with a header row
    In this function, json is defined as a list of dictionaries one dictionary deep where each dictionary has the same keys
    """
    if not json:
        print("json file is empty")
        return
    else:
        field_names = [] #sort  the dict key names before creating the CSV.
        for row in json[0].keys():
            field_names.append(row)
        field_names.sort()
        json_as_csv = []
        for loop_num, row in enumerate(json):
            if loop_num == 0:
                json_as_csv.append(field_names)
            new_row = []
            for field in field_names:
                try:
                    new_row.append(row[field])
                except:
                    new_row.append("BlankField")
            json_as_csv.append(new_row)
        import csv
        time_stamp = datetime.now(pytz.timezone("America/New_York")).strftime('%Y-%m-%d_%H.%M.%S')
        csv_file_name = 'monitor-pvc/testing/testing' + unique_name + time_stamp + '.csv'
        csv_export = csv.writer(open(csv_file_name, 'w'))
        for row in json_as_csv:
            csv_export.writerow(row)
        return ('\nExported to csv:', csv_file_name), csv_export


        #Other useful code snippets:
            #show the fields of the cdo or contact
            # from operator import itemgetter; fieldInformation = sorted(elq.GetFields('contacts')             , key=itemgetter('name')); maxFieldNameLength = max(len(fieldName['name']) for fieldName in fieldInformation); [print(row['name'].ljust(maxFieldNameLength),': ',row['internalName']) for row in fieldInformation]
            # from operator import itemgetter; fieldInformation = sorted(elq.GetFields('customObjects',cdoId)  , key=itemgetter('name')); maxFieldNameLength = max(len(fieldName['name']) for fieldName in fieldInformation); [print(row['name'].ljust(maxFieldNameLength),': ',row['internalName']) for row in fieldInformation]
