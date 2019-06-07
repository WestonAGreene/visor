#Author     : jecolema
#Adopted by : wgreene 000-04-29_06.12
#Created    : 000-04-29_06.12
#Modified   : 000-04-29_06.12

from datetime import datetime, timedelta
import os
import pytz

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
NOW_RALEIGH = datetime.now(TIMEZONE)


def visor_eloqua_cdo_contacts_vivastream(records, metric_list, adhoc=None):
    # scriptTime_start = datetime.now()
    # exported_job_prefix = "c.vs_"
    # metricPrefix    = 'DATA_HOURLY_ELOQUA_VIVASTREAM_'
    # logname         = '/' + metricPrefix + format(scriptTime_start, '%Y-%m-%d') + '.log'
    # try:
    #     logging.basicConfig(filename=os.environ['OPENSHIFT_LOG_DIR'] + logname, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # except:
    #     None

    # #log in
    # username    = os.environ['ELOQUA_USER']
    # password    = os.environ['ELOQUA_PASSWORD']
    # company     = os.environ['ELOQUA_COMPANY']
    # elq         = Eloqua(company=company, username=username, password=password)


    ## Setup export vars
    # timerange = 24 #hours

    # cdoID = elq.GetCdoId(cdoName = 'Contacts.Vivastream')
    # from operator import itemgetter; fieldInformation = sorted(elq.GetFields('customObjects',cdoID)  , key=itemgetter('name')); maxFieldNameLength = max(len(fieldName['name']) for fieldName in fieldInformation); [print(row['name'].ljust(maxFieldNameLength),': ',row['internalName']) for row in fieldInformation]

    # findFields = ['A_OfferID1'
    #             , 'A_TacticID_External1'
    #             , 'C_EmailAddress1'
    #             , 'Contacts.Vivastream.S_Milestone_01_LastPostedDate'
    #             , 'S_Data_Status1'
    #             , 'QA_Imatestrecord1'
    #             , 'UDF_01_Answer1'
    #             , 'UDF_01_Question1'
    #             , 'CreatedAt'
    #             , 'UpdatedAt'
    #             , 'DataCardIDExt'
    # ]

    # myFields = elq.CreateFieldStatement(entity='customObjects', cdoID=cdoID, fields=findFields)

    # timezone = pytz.timezone("America/New_York")
    # now_raleigh = datetime.now(timezone)
    # timestampNow = format(now_raleigh, "%Y-%m-%d %H:%M:%S")
    # timestampLast = format(now_raleigh - timedelta(hours=timerange), "%Y-%m-%d %H:%M:%S")

    # filterBase = elq.FilterDateRange(entity='customObjects', cdoID=cdoID, field='CreatedAt', start=timestampLast, end=timestampNow)

    # exportDefName = metricPrefix + str(now_raleigh)
    # cdoDef = elq.CreateDef(defType='exports', entity='customObjects', cdoID=cdoID, fields=myFields, filters = filterBase, defName=exportDefName)
    # logging.info("export definition created: " + cdoDef['uri'])

    # cdoSync = elq.CreateSync(defObject=cdoDef)
    # logging.info("export sync started: " + cdoSync['uri'])

    # status = elq.CheckSyncStatus(syncObject=cdoSync)
    # logging.info("sync successful; retreiving data")

    # data = elq.GetSyncedData(defObject=cdoDef)
    # logging.info("# of records:" + str(len(data)))

    global NOW_RALEIGH
    NOW_RALEIGH = datetime.now(TIMEZONE)  # need to reinstantiate NOW_RALEIGH because the date grows stale otherwise since it's declared outside of this function. This is where using class variables and these scripts as subclass would be handy

    campaign_one_cnt = 0
    campaign_two_cnt = 0
    # blankOfferId = 0
    # blankTacticId = 0
    # blankEmail = 0
    # notProcessed = 0
    notPosted = 0
    totalNew = len(records)

    # sessionExclude = ['session.DS', 'session.DP', 'session.75', 'session.89', 'session.68', 'session.90']
    campaign_one = '000f000ttFkAAI'
    campaign_two = '000dJVLAA2'

    if totalNew>0:

        time_inPast = datetime.strftime(NOW_RALEIGH + timedelta(-12/24),'%Y-%m-%d %H:%M:%S')
        # Why 12 hours:
        #   2 hours for 'CDO Services: Process records from Contacts.Vivastream' to run and then
        #   the '4TM CDOFormSubmitter' takes about 1 hour for every 1k submissions; 
        # Essentially, any time 10k or more records are created in Contacts.Vivastream, an alert will be triggered.
        # 10k is rare.
        
        for row in records:

            if row['A_OfferID1'] == campaign_one:
                campaign_one_cnt += 1

            if row['A_OfferID1'] == campaign_two:
                campaign_two_cnt += 1

            # hasExc = False
            # for exc in sessionExclude:
            #     if exc in row['UDF_01_Answer1']:
            #         hasExc = True

            # if row['A_OfferID1'] == '':
            #     #if (('session.DS' not in row['UDF_01_Answer1']) and ('session.DP' not in row['UDF_01_Answer1'])):
            #     if not hasExc:
            #         blankOfferId += 1

            # if row['A_TacticID_External1'] == '':
            #     if not hasExc:
            #         blankTacticId += 1

            # if row['C_EmailAddress1'] == '':
            #     blankEmail += 1

            # if row['S_Data_Status1'] == 'NEW':
            #     created = datetime.strptime(row['CreatedAt'] + '000', "%Y-%m-%d %H:%M:%S.%f")
            #     timeDiff = (scriptTime_start - created).total_seconds() / 60 / 60
            #     if (timeDiff>4):
            #         notProcessed += 1

            if row['S_Data_Status1'] == 'PROCESSING' and row['S_Milestone_01_LastPostedDate1'] == '':
                if time_inPast > row['UpdatedAt']:
                    notPosted += 1


    # scriptTime_end = datetime.now()
    # scriptDuration_seconds = (scriptTime_end-scriptTime_start).seconds


    #Push each prometheus input into a single job
    gaugesToReport = [
    #  {'gaugeName'  : 'blankEmail'
    #  ,'gaugeValue' :  blankEmail
    #  ,'gaugeDesc'  : 'Records with their email feild unpopulated.'
    #  }
    # ,{'gaugeName'  : 'blankOfferId'
    #  ,'gaugeValue' :  blankOfferId
    #  ,'gaugeDesc'  : 'Records with their Offer ID feild unpopulated.'
    #  }
    # ,{'gaugeName'  : 'blankTacticId'
    #  ,'gaugeValue' :  blankTacticId
    #  ,'gaugeDesc'  : 'Records with their Tactic ID feild unpopulated.'
    #  }
    # ,{'gaugeName'  : 'notProcessed'
    #  ,'gaugeValue' :  notProcessed
    #  ,'gaugeDesc'  : 'Records with a S_Data_Status1 field of "NEW".'
    #  }
    {'gaugeName'  : 'notPosted'
     ,'gaugeValue' :  notPosted
     ,'gaugeDesc'  : 'Records with a blank S_Milestone_01_LastPostedDate1 field.'
     }
    # ,{'gaugeName'  : 'totalNew'
    #  ,'gaugeValue' :  totalNew
    #  ,'gaugeDesc'  : 'All records created in the past %s hours.' %(timerange)
    #  }
    ,{'gaugeName'  :  "campaign_%s" %(campaign_one)
     ,'gaugeValue' :  campaign_one_cnt
     ,'gaugeDesc'  : 'Records with their offer ID equal to the default session campaign: %s.' %(campaign_one)
     }
    ,{'gaugeName'  :  "campaign_%s" %(campaign_two)
     ,'gaugeValue' :  campaign_two_cnt
     ,'gaugeDesc'  : 'Records with their offer ID equal to the default register campaign: %s.' %(campaign_two)
     }
    ]

    for row in gaugesToReport:
        metric_desc = row['gaugeDesc']
        metric_name = row['gaugeName']
        metric_value = row['gaugeValue']
        metric_list.append({'metric_name': metric_name, 'metric_value': metric_value, 'metric_desc': metric_desc})


    # metricName      = 'health'
    # metricDesc      = 'Multiple inputs that highlight CDO data that may be concerning.'
     #
    # for row in gaugesToReport:
    #     registry    = CollectorRegistry()
    #     gauge       = Gauge(metricPrefix + metricName, metricDesc, registry=registry)
    #     gauge.set(row['gaugeValue'])
    #     push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+row['gaugeName'], registry=registry)


    # #input rates of total
    # gaugesToReport_rates = []
    # dividerSoAsToNotDivideByZero = (totalNew if totalNew > 0 else 1)
    # for row in gaugesToReport:
    #     if row['gaugeName'] != 'totalNew':
    #         gaugesToReport_rates.append(
    #          {'gaugeName'  : row['gaugeName']  + '_rate'
    #          ,'gaugeValue' : row['gaugeValue'] / dividerSoAsToNotDivideByZero
    #          ,'gaugeDesc'  : 'Rate out of total of ' + row['gaugeDesc']
    #          }
    #         )
    # metricName      = 'health_rates'
    # metricDesc      = 'Rates out of total records created of inputs that highlight CDO data that may be concerning.'
    #  #
    # for row in gaugesToReport_rates:
    #     registry    = CollectorRegistry()
    #     gauge       = Gauge(metricPrefix + metricName, metricDesc, registry=registry)
    #     gauge.set(row['gaugeValue'])
    #     push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+row['gaugeName'], registry=registry)


    # #Push each prometheus input as a separate job
    # registry = CollectorRegistry()
    # exported_job         = 'monitoring'
    # additionalGauges = [
    #  {'gaugeName'  : 'last_success_unixtime'
    #  ,'gaugeValue' : datetime.now().timestamp()
    #  ,'gaugeDesc'  : 'Last time job successfully finished'
    #  }
    # ,{'gaugeName'  : 'scriptDuration_seconds'
    #  ,'gaugeValue' : scriptDuration_seconds
    #  ,'gaugeDesc'  : 'Total number of seconds to complete job'
    #  }
    # ]
    # for row in additionalGauges:
    #     gaugesToReport.append(row)
    # for row in gaugesToReport:
    #     gauge = Gauge(metricPrefix + row['gaugeName'], row['gaugeDesc'], registry=registry)
    #     gauge.set(row['gaugeValue'])
    # push_to_gateway(os.environ['PUSHGATEWAY'], job=exported_job_prefix+exported_job, registry=registry)


    return records, metric_list


if __name__ == '__main__':
    visor_eloqua_cdo_contacts_vivastream()



    #http://prometheus-marketingdev.itos.redhat.com/graph?g0.range_input=1w&g0.expr=DATA_HOURLY_ELOQUA_VIVASTREAM_noEmailAddress&g0.tab=0&g1.range_input=1w&g1.expr=DATA_HOURLY_ELOQUA_VIVASTREAM_noOfferID&g1.tab=0&g2.range_input=1w&g2.expr=DATA_HOURLY_ELOQUA_VIVASTREAM_notPosted&g2.tab=0&g3.range_input=1w&g3.expr=DATA_HOURLY_ELOQUA_VIVASTREAM_total&g3.tab=0
