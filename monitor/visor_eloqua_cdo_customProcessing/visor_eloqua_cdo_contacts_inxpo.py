#Author     : wgreene
#Created    : 000-12-16_04.34
#Modified   : 000-01-31_11.00
#Description: Contacts.INXPO CDO to match show keys to only one offer ID; will output number of show key and offer pairs that have either a show key or an offer matching with another show key and offer pair (there should be only 1 combination of offer and show key).

#Load necessities
import os
import datetime
import re
import pytz
from function_defintions_visor import printObject


# os.environ['PRINT_OUTPUT'] = True  # devonly
try:
    if os.environ['PRINT_OUTPUT'] == 'True':
        PRINT_OUTPUT = True
    else:
        PRINT_OUTPUT = False
except (KeyError):
    PRINT_OUTPUT = False
# if PRINT_OUTPUT:
#     from pprint import pprint

TIMEZONE = pytz.timezone("America/New_York")
NOW_RALEIGH = datetime.datetime.now(TIMEZONE)


def visor_eloqua_cdo_contacts_inxpo(records, metric_list, adhoc=None):
    #options:
    PRINT_OUTPUT = True  # devonly
    recentDayRange = 1 #(days) the timeframe from which to pull records and compare those records against all previous records.
    processAllCdoData = 0

    global NOW_RALEIGH
    NOW_RALEIGH = datetime.datetime.now(TIMEZONE)  # need to reinstantiate NOW_RALEIGH because the date grows stale otherwise since it's declared outside of this function. This is where using class variables and these scripts as subclass would be handy

    # runningLocally = 0
    # # if os.getenv('OPENSHIFT_NAMESPACE', 'local') == 'local':
    # #     runningLocally = 1

    # timezone = pytz.timezone("America/New_York")
    # NOW_RALEIGH = datetime.datetime.now(timezone)
    # print(datetime.datetime.strftime(NOW_RALEIGH,'%Y-%m-%d %H:%M:%S')) 
    if PRINT_OUTPUT:
        print('INXPO monitoring. \n This script will output number of show key and offer pairs that have either a show key or an offer matching with another show key and offer pair (there should be only 1 combination of offer and show key).') 

    # username    = os.environ['ELOQUA_USER']
    # password    = os.environ['ELOQUA_PASSWORD']
    # company     = os.environ['ELOQUA_COMPANY']
    #     ## Setup logging
    # if runningLocally != 1:
    #     scriptTime_start = datetime.datetime.now()
    #     exported_job_prefix = "c.ix_"
    #     scriptName       = 'Unique_ShowKey_OfferId_Relationship'
    #     metricPrefix     = 'DATA_DAILY_ELOQUA_INXPO_'
    #     logname          = '/' + scriptName + ' ' + format(datetime.datetime.now(), '%Y-%m-%d') + '.log'
    #     try:
    #         logging.basicConfig(filename=os.environ['OPENSHIFT_LOG_DIR'] + logname, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    #     except:
    #         None

    # #log in
    # elq = Eloqua(company=company, username=username, password=password)
    # print('\nYou signed in as') 
    # print(username) 
    # logging.info('Eloqua session established')

    # #1) Pull records with A_TrueRespondedDate greater than A_Timestamp

    #     ##set CDO specific variable
    recordCreatedDate       = 'CreatedAt'
    recordUpdatedDate       = 'UpdatedAt'
    recordShowKey           = 'Contacts_Inxpo_UDF_07_Answer1'
    recordOfferId           = 'Contacts_Inxpo_A_OfferID1'
    recordWebinarType       = 'Contacts_Inxpo_UDF_15_Answer1' # this field will grab the type of wedinar that the user is signing up for
    # # elq.GetFields('customObjects',cdoId) #show the fields of the cdo
    # findTheseFields = [ recordUID
    #                    ,recordCreatedDate
    #                    ,recordUpdatedDate
    #                    ,recordShowKey
    #                    ,recordOfferId
    #                    ,recordDataStatus
    #                    ,'Contacts_Inxpo_A_Timestamp1'
    #                    ]

    #     ##Confirm connection
    # print('Elq Site ID: ') 
    # print(elq.siteId) 
    # print('Elq username: ') 
    # print(elq.userDisplay) 

    #     ##Find CDO ID
    # cdoId = elq.GetCdoId(cdoName)
    # print('\nCDO ID of ') 
    # print(cdoName) 
    # print(': ') 
    # print(cdoId) 

    #     ##1 sync prep
    # myFields = elq.CreateFieldStatement(entity          ='customObjects'
    #                                 ,   cdoID           = cdoId
    #                                 ,   fields          = findTheseFields
    #                                     )
    # print('\nFields to be returned: ') 
    # for row in myFields:
    #     print(row) 
    # if filterExport == 1:
    #     todayMinusX = NOW_RALEIGH + datetime.timedelta(-10)
    #     todayMinusY = NOW_RALEIGH + datetime.timedelta(-0)
    #     dateRangeDays = todayMinusY - todayMinusX
    #     todayMinusX = datetime.datetime.strftime(todayMinusX,'%Y-%m-%d %H:%M:%S') #convert to str
    #     todayMinusY = datetime.datetime.strftime(todayMinusY,'%Y-%m-%d %H:%M:%S') #convert to str
    #     print('\nDate range to be returned: ') 
    #     print(todayMinusX) 
    #     print(' to ') 
    #     print(todayMinusY) 
    #     print('; ') 
    #     print(dateRangeDays.days) 
    #     print('days') 
    #     myFilter = elq.FilterDateRange(
    #                                    entity   = 'customObjects'
    #                                 ,  field    = 'DataCard Updated At'
    #                                 ,  start    = todayMinusX
    #                                 ,  end      = todayMinusY
    #                                 ,  cdoID    = cdoId
    #                                 )
    # myExport = elq.CreateDef( entity     ='customObjects'
    #                         , defType    ='exports'
    #                         , cdoID      = cdoId
    #                         , fields     = myFields
    #                         , filters    = (myFilter if filterExport == 1 else '' ) #filter only on local runs
    #                         , defName    = 'scriptFor.'+cdoName
    #                         )
    # print('\nSync-ing export (please wait)') 
    # mySync = elq.CreateSync(defObject=myExport)
    # status = elq.CheckSyncStatus(syncObject=mySync)
    # print('\nSync: ') 
    # print(status) 

    #     ##2 Pull cdoDataAll
    # print('\nPulling data (please wait)') 
    # cdoDataAll = elq.GetSyncedData(defObject=myExport)
    # print('\nTotal records pulled: ') 
    # print(len(cdoDataAll)) 
    # print('\nFirst row of data: ') 
    # print(cdoDataAll[0]) 

    ## Removing the records from all pulled cdoData having excluded domain emailaddress
    email_domains_exluded = ['@REDHAT.COM', '@INXPO.COM'] #pasomaya 000-02-26 email domain exlusion

    if PRINT_OUTPUT:
        print('\nRemoving records of these domain: ')
        print(email_domains_exluded)
        # last_prnt_tmstmp = datetime.datetime.now()
        # last_prnt_rw_cnt = 0
        # prnt_frqncy = 5
        # all_cdo_records_count = len(cdoDataAll)

    for loop_num, cdoDataRow in enumerate(records):
        if any(emailDomainRow in cdoDataRow['Contacts_Inxpo_C_EmailAddress1'].upper() for emailDomainRow in email_domains_exluded):
            cdoDataRow['removedForDomain'] = '1'
        else:
            cdoDataRow['removedForDomain'] = '0'
        # if PRINT_OUTPUT:
        #     loop_timestamp = datetime.datetime.now()
        #     if last_prnt_tmstmp < loop_timestamp - relativedelta(seconds=+prnt_frqncy):
        #         processing_rate = (loop_num - last_prnt_rw_cnt) / prnt_frqncy
        #         remaining_records = (all_cdo_records_count - loop_num)
        #         remaining_time = remaining_records / processing_rate
        #         estimated_completion_time = \
        #             loop_timestamp + relativedelta(seconds=+remaining_time)
        #         print("Processing at", int(processing_rate), \
        #             "records per second; complete in", \
        #             round(remaining_time/60, 1), "minutes at", \
        #             datetime.datetime.strftime(estimated_completion_time, '%Y-%m-%d %H:%M'), \
        #             "; currently", datetime.datetime.strftime(loop_timestamp, '%Y-%m-%d %H:%M'), \
        #             )
        #         last_prnt_tmstmp = loop_timestamp
        #         last_prnt_rw_cnt = loop_num
        #         prnt_frqncy += 1

    cdoDataAll_domainsRemoved = []
    for row in records:
        if row['removedForDomain'] == '0':
            cdoDataAll_domainsRemoved.append(row)

    if PRINT_OUTPUT:
        print('\nTotal records after removing selected domains: ')
        print(len(cdoDataAll_domainsRemoved))

        ##2.1 split cdoDataAll into cdoDataOld and cdoDataRecentMod
    recentDate      = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(-1 * recentDayRange),'%Y-%m-%d %H:%M:%S')
    if processAllCdoData == 0:
        cdoDataRecentMod   = [recordAll for recordAll in cdoDataAll_domainsRemoved if recordAll[recordUpdatedDate] >= recentDate]
        cdoDataRecentCreate   = [recordAll for recordAll in cdoDataAll_domainsRemoved if recordAll[recordCreatedDate] >= recentDate]
        cdoDataOld      = [recordAll for recordAll in cdoDataAll_domainsRemoved if recordAll[recordUpdatedDate] <  recentDate]
        if PRINT_OUTPUT:
            print('\nDay range considered ''recent'':') 
            print(recentDayRange) 
            print('\nRecent records to process:') 
        modified_recent = len(cdoDataRecentMod)
        created_recent = len(cdoDataRecentCreate)
        if PRINT_OUTPUT:
            print(modified_recent) 
            print('\nOld records to compare against:') 
            print(len(cdoDataOld)) 
    else:
        cdoDataRecentMod   = [recordAll for recordAll in cdoDataAll_domainsRemoved]
        cdoDataOld      = [recordAll for recordAll in cdoDataAll_domainsRemoved]
        if PRINT_OUTPUT:
            print('Comparing all data against all data. (this will take a very long time)') 


        ##additional inputs, maybe useful. 000-01-16
    regexTest = re.compile(r'[xX]{1,}') #INXPO replaces the show key or offer ID with all "X"s when performing tests.
    badShowKey = []
    for row in cdoDataRecentMod:
        try:
            if row[recordShowKey] == '' or regexTest.match(row[recordShowKey]) or int(row[recordShowKey]) >= 000:
                None
        except:
            badShowKey.append(row)
    countVariables = {}
    campaignIdRegex_18 = re.compile(r'000[a-zA-Z0-9]{15}$')
    badOfferId = [row for row in cdoDataRecentMod if not campaignIdRegex_18.match(row[recordOfferId]) and not regexTest.match(row[recordOfferId]) and row[recordOfferId] != None]
    countVariables['showKeyTest']    = len([row for row in cdoDataRecentMod if regexTest.match(row[recordShowKey])])
    countVariables['offerIdTest']    = len([row for row in cdoDataRecentMod if regexTest.match(row[recordOfferId])])
    countVariables['showKeyMissing'] = len([row for row in cdoDataRecentMod if row[recordShowKey] == ''])
    countVariables['offerIdMissing'] = len([row for row in cdoDataRecentMod if row[recordOfferId] == ''])
    countVariables['showKeyBad']     = len(badShowKey)
    countVariables['offerIdBad']     = len(badOfferId)
    if PRINT_OUTPUT:
        printObject(countVariables)

            ##2.2 export records where show keys match to more than one offer ID
        ##increase efficency by reducing both cdoDatas to unique values (sets)
    cdoDataUniqueRecent = set()
    for row in cdoDataRecentMod:
        cdoDataUniqueRecent.add((row[recordShowKey],row[recordOfferId],row[recordWebinarType]))
    cdoDataUniqueOld    = set()
    for row in cdoDataOld:
        cdoDataUniqueOld.add((row[recordShowKey],row[recordOfferId],row[recordWebinarType]))
    if PRINT_OUTPUT:
        print('\nFiltering out duplicate records, recent records that remain to process:') 
        print(len(cdoDataUniqueRecent)) 
        print('\nFiltering out duplicate records, old records that remain to compare against:') 
        print(len(cdoDataUniqueOld)) 
    cdoDataIncorrect = set()
    forCount1 = 0
    forCount2 = 0
    if PRINT_OUTPUT:
        print('\nExtracting from the data, records with show key') 
        print(recordShowKey) 
        print('NOT uniquely associated with ONE offer ID') 
        print(recordOfferId) 
        print('\nRecords to process: ') 
        print(len(cdoDataUniqueRecent)) 
        print('\nProcessing record number:') 
        print(forCount1) 
    for rowRecent in cdoDataUniqueRecent:
        for rowOld in cdoDataUniqueOld:
            if  rowRecent[0] == rowOld[0] and rowRecent[1] != rowOld[1] and rowRecent[0] != '' and not regexTest.match(rowRecent[0]) and rowRecent[2] != 'webinar-series' and rowOld[2]!= 'webinar-series' ): # last 2 arrguments check if a webinar response has been marked as a webinar series in both collections:
                cdoDataIncorrect.add(rowOld) #000-02-02_15.41 wgreene: added so the output would reveal both the original and culprit
                cdoDataIncorrect.add(rowRecent)
            if  rowRecent[1] == rowOld[1] and rowRecent[0] != rowOld[0] and rowRecent[1] != '' and not regexTest.match(rowRecent[1]) and rowRecent[2] != 'webinar-series' and rowOld[2]!= 'webinar-series' ): # last 2 arrguments check if a webinar response has been marked as a webinar series in both collections:
                cdoDataIncorrect.add(rowOld)
                cdoDataIncorrect.add(rowRecent)
            if PRINT_OUTPUT:
                forCount2 += 1
                if forCount2 <= 3:
                    print('-', forCount2) 
        if PRINT_OUTPUT:
            forCount1 += 1
            if forCount1 <= 3:
                print(forCount1) 
                forCount2 =  0
            elif forCount1 <= 000:
                if forCount1 % 000==0:
                    print(forCount1) 
                    forCount2 =  0
            elif forCount1 <= 000:
                if forCount1 % 000==0:
                    print(forCount1) 
                    forCount2 =  0
            elif forCount1 % 000==0:
                print(forCount1) 
                forCount2 =  0

    if PRINT_OUTPUT:
        print('\nUnique pairs processed: ') 
        print(forCount1) 
        print('\nPairs of show key and offer ID that share a key or ID with another pair: ') 
    countCdoDataIncorrect = len(cdoDataIncorrect)
    if countCdoDataIncorrect != 0:
        print('THERE ARE SHOW KEY PAIRED TO MULTIPLE OFFER ID! Here is the count and data:')
        print(countCdoDataIncorrect)
        for row in cdoDataIncorrect:
            print(row)
        #'\nPortion of incorrect data: ')
        # print((str(cdoDataIncorrect)[:35] + '...') if len(str(cdoDataIncorrect)) > 35 else cdoDataIncorrect) #to provide a 35 character snippet in case results are very long
    else:
        if PRINT_OUTPUT:
            print('\nNo Show Key are paired to multiple Offer ID') 

    # if runningLocally != 1:
    #     exported_job         = 'cInxpoMonitoring'
        # # Prometheus logging
        # registry = CollectorRegistry()
        # metricName      = 'last_success_unixtime'
        # metricDesc      = 'Last time the script successfully finished.'
        # gauge_last_success_unixtime           = Gauge(metricPrefix + metricName, metricDesc, registry=registry)
        # gauge_last_success_unixtime.set_to_current_time()
        # #
        # scriptTime_end      = datetime.datetime.now()
        # scriptTime_duration = scriptTime_end - scriptTime_start
        # gauge_scriptTime_duration   = Gauge(metricPrefix + 'scriptDuration_seconds', 'Amount of time the script used to complete.', registry=registry)
        # gauge_scriptTime_duration.set(scriptTime_duration.seconds)
        # #
        # push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+exported_job, registry=registry)

        # metricName      = 'health'
        # metricDesc      = 'Multiple inputs that highlight CDO data that may be concerning.'
            #
        # countVariables['modified'] = modified_recent
        # countVariables['created'] = created_recent
        # countVariables['uniqueShows'] = forCount1
        # countVariables['showKeyToOffer_nonUnique'] = countCdoDataIncorrect
        # for key,value in countVariables.items():
        #     registry    = CollectorRegistry()
        #     gauge       = Gauge(metricPrefix + metricName, metricDesc, registry=registry)
        #     exported_job     = key
        #     gauge.set(value)
        #     push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+exported_job, registry=registry)
        #
        # registry = CollectorRegistry()
        # gauge           = Gauge(metricPrefix + metricName, metricDesc, registry=registry)
        #  #
        # exported_job         = 'new_pastDay'
        # gauge.set(        forCount1)
        # push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+exported_job, registry=registry)
        #  #
        # exported_job         = 'showKeyToOffer_nonUnique'
        # gauge.set(         countCdoDataIncorrect)
        # push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+exported_job, registry=registry)
    
    metric_desc = ("Count of unique Show Key")
    metric_name = 'uniqueShowKey'
    metric_value = forCount1
    metric_list.append({'metric_name': metric_name, 'metric_value': metric_value, 'metric_desc': metric_desc})
    metric_desc = ("Count of pairs of Show Key and Offer IDs that share a Show Key or Offer Id with another pair.")
    metric_name = 'showKeyToOffer_nonUnique'
    metric_value = countCdoDataIncorrect
    metric_list.append({'metric_name': metric_name, 'metric_value': metric_value, 'metric_desc': metric_desc})
    if PRINT_OUTPUT:
        print('\n')
        pprint(metric_list) 

    return records, metric_list
