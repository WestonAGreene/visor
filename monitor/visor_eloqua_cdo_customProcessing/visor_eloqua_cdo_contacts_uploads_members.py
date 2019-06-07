#Author     : wgreene
#Created    : 000-07-20_07.39
#Description: This script contains SLIs on Contacts.Uploads.Members.

import os
import datetime
import pytz

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
    from function_defintions_visor import printObject

TIMEZONE = pytz.timezone("America/New_York")
NOW_RALEIGH = datetime.datetime.now(TIMEZONE)


def visor_eloqua_cdo_contacts_uploads_members(records, metric_list, adhoc=None):
    # # Setup logging
    # runningLocally = 0
    # # if os.getenv('OPENSHIFT_NAMESPACE', 'local') == 'local': #000-06-03 no need. wgreene
    # #     runningLocally = 1
    # if runningLocally != 1:
    #     scriptTime_start = datetime.datetime.now()
    #     metricPrefix    = 'DATA_HOURLY_ELOQUA_UPLOADSMEMBERS_'
    #     exported_job_prefix = "c.um_"
    #     logname         = '/' + metricPrefix + format(scriptTime_start, '%Y-%m-%d') + '.log'
    #     try:
    #         logging.basicConfig(filename=os.environ['OPENSHIFT_LOG_DIR'] + logname, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    #     except:
    #         None
    # #set local time
    # timezone = pytz.timezone("America/New_York")
    # NOW_RALEIGH = datetime.datetime.now(timezone)
    # #log in
    # username    = os.environ['ELOQUA_USER']
    # password    = os.environ['ELOQUA_PASSWORD']
    # company     = os.environ['ELOQUA_COMPANY']
    # elq         = Eloqua(company=company, username=username, password=password)
    # None if printOutput == 0 else print('Elq Site ID: ')
    # None if printOutput == 0 else print(elq.siteId)
    # None if printOutput == 0 else print('Elq username: ')
    # None if printOutput == 0 else print(elq.userDisplay)
    # logging.info('Eloqua session established')
    #     ##set CDO specific variable
    # cdoName                 = 'Contacts.Uploads.Members'
    # cdoId = elq.GetCdoId(cdoName)
    # None if printOutput == 0 else print('\nCDO ID of ')
    # None if printOutput == 0 else print(cdoName)
    # None if printOutput == 0 else print(': ')
    # None if printOutput == 0 else print(cdoId)
    # #show the fields of the cdo
    # # from operator import itemgetter; fieldInformation = sorted(elq.GetFields('contacts')             , key=itemgetter('name')); maxFieldNameLength = max(len(fieldName['name']) for fieldName in fieldInformation); [print(row['name'].ljust(maxFieldNameLength),': ',row['internalName']) for row in fieldInformation]
    # # from operator import itemgetter; fieldInformation = sorted(elq.GetFields('customObjects',cdoId)  , key=itemgetter('name')); maxFieldNameLength = max(len(fieldName['name']) for fieldName in fieldInformation); [print(row['name'].ljust(maxFieldNameLength),': ',row['internalName']) for row in fieldInformation]
    recordFieldNames = {
        #  'recordCreatedDate'        : 'CreatedAt'
        # ,'recordModifiedDate'       : 'UpdatedAt'
        # #
        # ,'recordIdOffer'            : 'Contacts_Inxpo_A_OfferID1'
        # ,'recordIdTactic'           : 'Contacts_Uploads_Members_A_TacticID1'
        # ,'recordTrueRespondedDate'  : 'Contacts_Uploads_Members_A_TrueRespondedDate1'
        # ,'recordEmail'              : 'Contacts_Inxpo_C_EmailAddress1'
        'prequalified_true'       : 'Contacts_Uploads_C_Pre_qualified11'
        ,'sendToLeadDev_true'      : 'Contacts_Members_C_Send_to_Lead_Development11'
        ,'isLeadActivity_false'     : 'Contacts_Uploads_Members_F_FormData_IsLeadAct1'
        ,'imATestRecord_true'      : 'Contacts_Uploads_Members_QA_IMATESTRECORD1'
        # ,'recordDataStatus'         : 'Contacts_Uploads_Members_S_Data_Status1'
        # ,'recordTargetFormName'     : 'Contacts_Uploads_Members_S_Target_FormName1'
        # ,'recordUploadedBy'         : 'Contacts_Uploads_Members_S_Upload_By1'
        # ,'recordUploadedFile'       : 'Contacts_Uploads_Members_S_Upload_File1'
        # ,'recordUploadedName'       : 'Contacts_Uploads_Members_S_Upload_Name1'
        }
        ##1 sync prep
    # myFields = elq.CreateFieldStatement(entity                  ='customObjects'
    #                                 ,   cdoID                   = cdoId
    #                                 ,   fields                  = list(recordFieldNames.values())
    #                                     )
    # todayMinusX = NOW_RALEIGH + datetime.timedelta(-timeRange)
    # todayMinusY = NOW_RALEIGH + datetime.timedelta(-0)
    # dateRangeDays = todayMinusY - todayMinusX
    # todayMinusX = datetime.datetime.strftime(todayMinusX,'%Y-%m-%d %H:%M:%S') #convert to str
    # todayMinusY = datetime.datetime.strftime(todayMinusY,'%Y-%m-%d %H:%M:%S') #convert to str
    # None if printOutput == 0 else print('\nDate range to be returned: ')
    # None if printOutput == 0 else print(todayMinusX)
    # None if printOutput == 0 else print(' to ')
    # None if printOutput == 0 else print(todayMinusY)
    # None if printOutput == 0 else print('; ')
    # None if printOutput == 0 else print(dateRangeDays.days)
    # None if printOutput == 0 else print('days')
    # #
    # myFilter = elq.FilterDateRange(
    #                                entity   = 'customObjects'
    #                             ,  field    = 'DataCard Created At'
    #                             ,  start    = todayMinusX
    #                             ,  end      = todayMinusY
    #                             ,  cdoID    = cdoId
    #                             )
    # #
    # myExport = elq.CreateDef( entity     ='customObjects'
    #                         , defType    ='exports'
    #                         , cdoID      = cdoId
    #                         , fields     = myFields
    #                         , filters    = myFilter
    #                         , defName    = 'scriptFor.'+cdoName
    #                         )
    # #
    # None if printOutput == 0 else print('\nSync-ing export (please wait)')
    # mySync = elq.CreateSync(defObject=myExport)
    # status = elq.CheckSyncStatus(syncObject=mySync)
    # None if printOutput == 0 else print('\nSync: ')
    # None if printOutput == 0 else print(status)
    #     ##2 Pull cdoData_all
    # None if printOutput == 0 else print('\nPulling data (please wait)')
    # cdoData_all = elq.GetSyncedData(defObject=myExport)
    # None if printOutput == 0 else print('\nTotal records pulled: ')
    # cdoData_all_count = len(cdoData_all)
    # None if printOutput == 0 else print(cdoData_all_count)
    # None if printOutput == 0 else print('\nFirst row of data: ')
    # None if printOutput == 0 else printObject(cdoData_all)
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
        # None if printOutput == 0 else print("\n\n\n\n\n")
        # NOW_RALEIGH = datetime.datetime.now(timezone)
    # if PRINT_OUTPUT:
    #     print(datetime.datetime.strftime(NOW_RALEIGH,'%Y-%m-%d %H:%M:%S'))
    #     print("This script will:")
    #     print("check Contacts.Uploads.Members reocords that have NEW in their S_dataStatus field.")
    #     print("So that:")
    #     print("we are notified for records that are not processing due to system overload as all records should only have a S_dataStatus of NEW for less than 2 hours.")
    #     print("")

    global NOW_RALEIGH
    NOW_RALEIGH = datetime.datetime.now(TIMEZONE)  # need to reinstantiate NOW_RALEIGH because the date grows stale otherwise since it's declared outside of this function. This is where using class variables and these scripts as subclass would be handy

        ##Frequency of concerning fields
    positive_values = [
        "true"
    , "yes"
    , "Yes || Yes"
    , "1"
    ]
    negative_values = [
        "false"
    , "no"
    , "No || No"
    , "0"
    ]
    concerning_fields = [ # [key value, value that is concerning]
        ['prequalified_true', positive_values],
        ['sendToLeadDev_true', positive_values],
        ['isLeadActivity_false', negative_values],
        ['imATestRecord_true', positive_values],
    ]
    concerning_fields_counts = []
    for row in concerning_fields:
        current_field_count = 0
        current_field_count = len([row_of_cdo for row_of_cdo in records if row_of_cdo[recordFieldNames[row[0]]] in row[1]])
        concerning_fields_counts.append([row[0], current_field_count])
        current_field_unique_values = set()
        for row_all in records:
            current_field_unique_values.add(row_all[recordFieldNames[row[0]]]) 
        current_field_unique_values_count = {}
        for row_unique_value in current_field_unique_values:
            current_field_unique_values_count[row_unique_value] = len([rowAll for rowAll in records if rowAll[recordFieldNames[row[0]]] == row_unique_value])
        if PRINT_OUTPUT:
            print('Pivot on', row[0])
            printObject(current_field_unique_values_count)
            print('\n')
    if PRINT_OUTPUT:
        print("Concerning fields and counts:")
        pprint(concerning_fields_counts)
        print("\n")
        #
        #     ##pivot on data status
        # dataStatusUnique = set()
        # for row in cdoData_all:
        #     dataStatusUnique.add(row[recordFieldNames['recordDataStatus']])
        # status_count = {}
        # for row in dataStatusUnique:
        #     status_count[row] = len([rowAll for rowAll in cdoData_all if rowAll[recordFieldNames['recordDataStatus']] == row])
        # if PRINT_OUTPUT:
        #     None if printOutput == 0 else print('A count of records with each data status:')
        #     None if printOutput == 0 else printObject(status_count)
        # #
        # #
        #     ##not PROCESSED
        # unusual_data_status = ["NEW"
        #                        , "PROCESSED"
        #                        , "PROCESSED as NEW"
        #                        , "PROCESSING"
        #                       ]
        # cdoStatusNotProcessedNotNew = [row for row in cdoData_all \
        #                                if row[recordFieldNames['recordDataStatus']] \
        #                                not in unusual_data_status \
        #                               ]
        # statusOfNotProcessedNotNew_count = len(cdoStatusNotProcessedNotNew)
        # if statusOfNotProcessedNotNew_count > 0:
        #     print('\nstatusOfNotProcessedNotNew_count:', statusOfNotProcessedNotNew_count  )
        #     print('\nThere is an abnormal data status. Here is a pivot on data status:')
        #     printObject(status_count)
        #
        # cdoData_new = [row for row in cdoData_all if row[recordFieldNames['recordDataStatus']] == 'NEW']
            ##pull records that are data status new and older than x minutes
        # time_inPast = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(minutes = -30),'%Y-%m-%d %H:%M:%S')
        # statusOfNewAndOlderThan000m_count = len([row for row in cdoData_new if row[recordFieldNames['recordDataStatus']] == 'NEW' and row[recordFieldNames['recordModifiedDate']] < time_inPast])
        # None if printOutput == 0 else print('statusOfNewAndOlderThan000m_count:')
        # None if printOutput == 0 else print(statusOfNewAndOlderThan000m_count)
        # #
        # time_inPast = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(minutes = -60),'%Y-%m-%d %H:%M:%S')
        # statusOfNewAndOlderThan000m_count = len([row for row in cdoData_new if row[recordFieldNames['recordDataStatus']] == 'NEW' and row[recordFieldNames['recordModifiedDate']] < time_inPast])
        # None if printOutput == 0 else print('statusOfNewAndOlderThan000m_count:')
        # None if printOutput == 0 else print(statusOfNewAndOlderThan000m_count)
        # #
        # time_inPast = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(minutes = -90),'%Y-%m-%d %H:%M:%S')
        # statusOfNewAndOlderThan000m_count = len([row for row in cdoData_new if row[recordFieldNames['recordDataStatus']] == 'NEW' and row[recordFieldNames['recordModifiedDate']] < time_inPast])
        # None if printOutput == 0 else print('statusOfNewAndOlderThan000m_count:')
        # None if printOutput == 0 else print(statusOfNewAndOlderThan000m_count)
        # #
        # time_inPast = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(minutes = -000),'%Y-%m-%d %H:%M:%S')
        # statusOfNewAndOlderThan000m_count = len([row for row in cdoData_new if row[recordFieldNames['recordDataStatus']] == 'NEW' and row[recordFieldNames['recordModifiedDate']] < time_inPast])
        # None if printOutput == 0 else print('statusOfNewAndOlderThan000m_count:')
        # None if printOutput == 0 else print(statusOfNewAndOlderThan000m_count)
        # #
        # time_inPast = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(minutes = -000),'%Y-%m-%d %H:%M:%S') #5 hours; this provides sufficient time for program builder to run twice (on paper: 2 hours; practically: 2.25; 4.5hrs total) and then have 30 minutes of wiggle room. If records still remain after that point, we should be concerned. 000-01-26_15.13 wgreene
        # statusOfNewAndOlderThan000m_count = len([row for row in cdoData_new if row[recordFieldNames['recordDataStatus']] == 'NEW' and row[recordFieldNames['recordModifiedDate']] < time_inPast])
        # None if printOutput == 0 else print('statusOfNewAndOlderThan000m_count:')
        # None if printOutput == 0 else print(statusOfNewAndOlderThan000m_count)
        # #
        # #average together the age (time post created) of all Contacts.Inquiries records with data status of NEW
        # sumRecordAgeNew = 0
        # for row in cdoData_new:
        #     createdStampConvertedToDateType = datetime.datetime.strptime(row[recordFieldNames['recordCreatedDate']], "%Y-%m-%d %H:%M:%S.%f")
        #     # sumRecordAgeNew += (NOW_RALEIGH - createdStampConvertedToDateType).seconds
        #     sumRecordAgeNew += (NOW_RALEIGH.replace(tzinfo=None) - createdStampConvertedToDateType).seconds
        # try:
        #     statusOfNew_averageAge_minutes = (sumRecordAgeNew/len(cdoData_new))/60
        # except:
        #     statusOfNew_averageAge_minutes = 0
        # None if printOutput == 0 else print('statusOfNew_averageAge_minutes:')
        # None if printOutput == 0 else print( statusOfNew_averageAge_minutes  )
        #
        # if runningLocally != 1:
        #     try:
        #         cdoData_new_count = status_count['NEW']
        #     except:
        #         cdoData_new_count = 0
            # gaugesReported = {
            #     #  'created'       : cdoData_all_count
            #     # ,'statusOfNew'                : cdoData_new_count
            #     ,'statusOfNotProcessedNotNew' : statusOfNotProcessedNotNew_count
            #     # ,'statusOfNewAndOlderThan000m': statusOfNewAndOlderThan000m_count
            #     # ,'statusOfNewAndOlderThan000m': statusOfNewAndOlderThan000m_count
            #     # ,'statusOfNewAndOlderThan000m': statusOfNewAndOlderThan000m_count
            #     # ,'statusOfNewAndOlderThan000m': statusOfNewAndOlderThan000m_count
            #     # ,'statusOfNewAndOlderThan000m': statusOfNewAndOlderThan000m_count
            #     # ,'statusOfNew_averageAge_minutes'   : statusOfNew_averageAge_minutes
            # }
            # for row in concerning_fields_counts:
            #     gaugesReported[row[0]] = row[1]

    for row in concerning_fields_counts:
        metric_desc = ("Fields that may be used inappropriately.")
        metric_name = row[0]
        metric_value = row[1]
        metric_list.append({'metric_name': metric_name, 'metric_value': metric_value, 'metric_desc': metric_desc})



            # # Prometheus logging
            # metricName      = 'health'
            # metricDesc      = 'Multiple inputs that highlight CDO data that may be concerning.'
            #  #
            # for loopNum,dic in enumerate(gaugesReported.items()):
            #     registry    = CollectorRegistry()
            #     loopNum       = Gauge(metricPrefix + metricName, metricDesc, registry=registry)
            #     exported_job     = dic[0]
            #     loopNum.set(dic[1])
            #     push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+exported_job, registry=registry)
    #
    #
    #
    #
    #
    #
    #
    # ##pivot uploads made
    # uploadsUnique_set = set()
    # for row in cdoData_all:
    #     # uploadsUnique_set.add(row[recordFieldNames['recordUploadedBy']])
    #     uploadsUnique_set.add({
    #          'recordUploadedBy'      : row[recordFieldNames['recordUploadedBy']]
    #         ,'recordUploadedFile'    : row[recordFieldNames['recordUploadedFile']]
    #         ,'recordCreatedDate'     : row[recordFieldNames['recordCreatedDate']]
    #     })
    #     # uploadsUnique_set.add((
    #     #      row[recordFieldNames['recordUploadedBy']]
    #     #     ,row[recordFieldNames['recordUploadedFile']]
    #     #     ,row[recordFieldNames['recordCreatedDate']]
    #     # ))
    # uploadsUnique_list = list
    # for row in uploadsUnique_set:
    #     for row2 in row.items()
    #         uploadsUnique_list.add() #incomplete 000-07-20_14.30
    #     uploadsUnique_list = [
    #      {row2 for row2 in row.items()}
    #     #  [row2 for row2 in row]
    #     ]
    # uploads_count = {}
    # for row in uploadsUnique_list:
    #     uploadsUnique_list["uploadCount"] = len([rowAll for rowAll in cdoData_all if rowAll[recordFieldNames['recordUploadedBy']] == row[0] and rowAll[recordFieldNames['recordUploadedFile']] == row[1] and rowAll[recordFieldNames['recordCreatedDate']] == row[2]])
    #     # uploads_count[row[0]+"|"+row[1]+"|"+row[2]] = len([rowAll for rowAll in cdoData_all if rowAll[recordFieldNames['recordUploadedBy']] == row[0] and rowAll[recordFieldNames['recordUploadedFile']] == row[1] and rowAll[recordFieldNames['recordCreatedDate']] == row[2]])
    # None if printOutput == 0 else print('A count of records with each data status:')
    # None if printOutput == 0 else printObject(uploads_count)
    #

    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    # if runningLocally != 1:
    #     exported_job         = 'monitoring'
    #     scriptTime_end      = datetime.datetime.now()
    #     scriptTime_duration = scriptTime_end - scriptTime_start
    #     # Prometheus logging
    #     registry = CollectorRegistry()
    #     #
    #     metricName      = 'scriptDuration_seconds'
    #     metricDesc      = 'Amount of time the script used to complete.'
    #     gauge_scriptDuration_seconds           = Gauge(metricPrefix + metricName, metricDesc, registry=registry)
    #     gauge_scriptDuration_seconds.set(scriptTime_duration.seconds)
    #     #
    #     #
    #     metricName      = 'last_success_unixtime'
    #     metricDesc      = 'Last time the script successfully finished.'
    #     gauge_last_success_unixtime           = Gauge(metricPrefix + metricName, metricDesc, registry=registry)
    #     gauge_last_success_unixtime.set_to_current_time()
    #     #
    #     push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+exported_job, registry=registry)
    # return cdoData_all;
    return records, metric_list


if __name__ == '__main__':
    visor_eloqua_cdo_contacts_uploads_members()



    # results = visor_eloqua_cdo_contacts_uploads_members()
    # ##3 export to CSV
    # fieldNames = [] #sort  the dict key names before creating the CSV.
    # [fieldNames.append(row) for row in results[0].keys()]
    # fieldNames.sort()
    # csvOfResults = []
    # for loopNum,row in enumerate(results):
    #     if loopNum == 0:
    #         csvOfResults.append(fieldNames)
    #     newRow = []
    #     for field in fieldNames:
    #         newRow.append(row[field])
    #     csvOfResults.append(newRow)
    # import datetime
    # import csv
    # timeStamp   = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M')
    # csvFileName = timeStamp+'.Contacts.Uploads.Members.bulkEmailfilter.csv'
    # csvExport   = csv.writer(open(csvFileName, 'w'))
    # [csvExport.writerow(row) for row in csvOfResults]
    # print('\nExported to csv:', csvFileName)
