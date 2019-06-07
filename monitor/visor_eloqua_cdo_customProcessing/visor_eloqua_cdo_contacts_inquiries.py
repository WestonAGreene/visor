"""
Author     : wgreene
Created    : 000-01-18_11.32
Description: This script contains SLIs on Contacts.Inquiries.
"""

import os
import datetime
import sys
import pytz
sys.path.insert(0, '../')  #  This adds the parent folder to the list of scripts able to be imported; needed for the next line
from visor_eloqua_cdo import generic_analysis

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

TIMEZONE = pytz.timezone("America/New_York")
NOW_RALEIGH = datetime.datetime.now(TIMEZONE)


def visor_eloqua_cdo_contacts_inquiries(records, metric_list, adhoc=None):
    """
    Combines all the functions

    Runs analysis on all Contacts.Inquiries records sourced from upload-wizard-integration
    Then on all other records
    """
    if PRINT_OUTPUT:
        records_count = len(records)
        print("Records to be analyzed:", records_count)
    records = analysis(records=records)  # analyzes, returning the results of the analyses into new fields per record
    if PRINT_OUTPUT:
        pprint(records[0])


    if PRINT_OUTPUT:
        print("Monitoring on all records")
    metric_list = monitoring_all(records=records, metric_list=metric_list, adhoc=adhoc)

    global NOW_RALEIGH
    NOW_RALEIGH = datetime.datetime.now(TIMEZONE)  # need to resubstantiate NOW_RALEIGH because the date grows stale otherwise since it's declared outside of this function. This is where using class variables and these scripts as subclass would be handy

    if not adhoc:
        if PRINT_OUTPUT:
            print("Monitoring on subsets of records")
        records_sourceOfUpload = []
        records_sourceOfUpload_not = []
        for row in records:
            if row['Contacts_Inquiries_F_FormData_Source1'][:25] == "upload-wizard-integration":
                records_sourceOfUpload.append(row)
            else:
                records_sourceOfUpload_not.append(row)

        lists_to_be_monitored = {
            'srcOfUpld__': records_sourceOfUpload,
            'srcOfUpldNot__': records_sourceOfUpload_not
        }

        for key, item in lists_to_be_monitored.items():
            if PRINT_OUTPUT:
                count = len(item)
                print("Of the", records_count, "records,", count, "were", key, "\n")
            metric_list = monitoring_subset(records=item, src=key, metric_list=metric_list)

    return records, metric_list


def analysis(records):
    """
    Analysis on Contacts.Inquiries records
    This analysis applies to all records; 
        no filtering necessary before passing to this function.
    """

    true_resp_unreasonably_in_past = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(days=-000), '%Y-%m-%d %H:%M:%S')
    true_resp_unreasonably_in_future = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(days=000), '%Y-%m-%d %H:%M:%S')
    hours_ago_29 = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(-(29/24)), '%Y-%m-%d %H:%M:%S')
    hours_ago_24 = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(-(24/24)), '%Y-%m-%d %H:%M:%S')
    hours_ago_5 = datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(-(5/24)), '%Y-%m-%d %H:%M:%S')
    for row in records:
        row['true_responded_date_unreasonable'] = 0
        if (row['Contacts_Inquiries_A_Timestamp1'] != '' and
                (row['Contacts_Inquiries_A_Timestamp1'] > true_resp_unreasonably_in_future or
                 row['Contacts_Inquiries_A_Timestamp1'] < true_resp_unreasonably_in_past
                 )
            ):
            row['true_responded_date_unreasonable'] = 1

        row['entered_lead_funnel'] = 0
        if row['C_Timestamp__Last_Entered_Lead_Funnel_Date1'] > row['CreatedAt']:
            row['entered_lead_funnel'] = 1

        row['createdAfter29HoursAgo'] = 0
        if row['CreatedAt'] > hours_ago_29:
            row['createdAfter29HoursAgo'] = 1

        row['createdBefore5HoursAgo'] = 0
        if row['CreatedAt'] < hours_ago_5:
            row['createdBefore5HoursAgo'] = 1

        row['createdBetween5And29HoursAgo'] = 0
        if (row['createdBefore5HoursAgo'] == 1 and
                row['createdAfter29HoursAgo'] == 1
                ):
            row['createdBetween5And29HoursAgo'] = 1

        row['createdAfter24HoursAgo'] = 0
        if row['CreatedAt'] > hours_ago_24:
            row['createdAfter24HoursAgo'] = 1

        row['campaigns_valid'] = 0
        row['campaigns_valid_missing_memberships'] = 0
        row['campaigns_valid_missing_membership_offer'] = 0
        row['campaigns_valid_missing_membership_tactic'] = 0
        row['offer_valid_missing_membership'] = 0
        row['tactic_valid_missing_membership'] = 0
        if (row['offer_valid'] == 1 and
                row['tactic_valid'] == 1
                ): #has both valid offer and tactic
            row['campaigns_valid'] = 1

        if (row['C_SFDCLeadID'] != ''
        and row['createdBetween5And29HoursAgo'] == 1):
            if row['campaigns_valid'] == 1:
                if (row['Contacts_Inquiries_S_Offer_Member_ID_Lead1'] == '' and
                        row['Contacts_Inquiries_S_Tactic_Ext_Member_ID_Lead1'] == ''
                        ): #missing both memberships
                    row['campaigns_valid_missing_memberships'] = 1
                elif row['Contacts_Inquiries_S_Offer_Member_ID_Lead1'] == '': #missing just offer membership
                    row['campaigns_valid_missing_membership_offer'] = 1
                elif row['Contacts_Inquiries_S_Tactic_Ext_Member_ID_Lead1'] == '': #missing just tactic membership
                    row['campaigns_valid_missing_membership_tactic'] = 1
            elif (row['offer_valid'] == 1 and
                    row['Contacts_Inquiries_S_Offer_Member_ID_Lead1'] == ''):
                row['offer_valid_missing_membership'] = 1
            elif (row['tactic_valid'] == 1 and
                    row['Contacts_Inquiries_S_Tactic_Ext_Member_ID_Lead1'] == ''):
                row['tactic_valid_missing_membership'] = 1


    pathcodesBad = {'E65': 'a null lead ranking',
                    'E66': 'a null lead record type ID',
                    'E67': 'a bad first name',
                    'E68': 'a Red Hat email address domain',
                    'E69': 'Red Hat as company',
                    'E70': 'a Red Hat partner company',
                    'E71': 'a Red Hat partner email domain',
                    'E72': 'a Latin America partner email domain',
                    'E81': 'an invalid lead record type',
                    'E82': 'a missing last name',
                    'E83': 'a missing company',
                    'E84': 'no details about the lead source',
                    'E85': 'a missing country',
                    'F47': 'a recent conversion date to a contact',
                    'B52': 'a recent conversion date to a contact', #why are there two pathcodes for basically the same thing?
                    'G73': 'a flag as a test record',
                    'O92': 'a flag as a hard bounce email'
                    }

    # Why the record is missing a Salesforce Lead ID
    disqualifyingFieldValues_default = "Record disqualified for "
    disqualifyingPathcodes_default = "Record disqualified by pathcodes: "
    disqualifyingFieldValues_default_len = len(disqualifyingFieldValues_default)
    disqualifyingPathcodes_default_len = len(disqualifyingPathcodes_default)
    recordHasLeadId = "Record had or already received a lead ID"
    recordHasNotFinishedLeadFunnel = "Record had not finished the Lead Funnel"
    recordIsNotOldEnough = "Record had not enough time to receive a Lead ID"  # that is "disqualified"
    for row in records:
        disqualified_fieldValues = 0
        disqualified_pathcodes = 0
        #check if the data qualifies to become a lead
        disqualifyingFieldValues = disqualifyingFieldValues_default
        if (row['C_SFDCLeadID'] != ''):
            disqualifyingFieldValues = recordHasLeadId
            disqualifyingPathcodes = recordHasLeadId
        elif (
                row['C_Timestamp__Last_Entered_Lead_Funnel_Date1']
                >
                datetime.datetime.strftime(NOW_RALEIGH + datetime.timedelta(-12 / 24), '%Y-%m-%d %H:%M:%S')
        ):
            disqualifyingFieldValues = recordHasNotFinishedLeadFunnel
            disqualifyingPathcodes = recordHasNotFinishedLeadFunnel
        elif row['createdBefore5HoursAgo'] == 0:
            disqualifyingFieldValues = recordIsNotOldEnough
            disqualifyingPathcodes = recordIsNotOldEnough
        else:
            if row['Contacts_Inquiries_S_Data_Status1'] != "PROCESSED":
                disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, ("not having finished being processed; wait 3 hours after %s00, when the record was created" %(row['CreatedAt'][:13])))
            # if row['C_Invalid_Email_Address_Domain_Extension1'] == '1':   # unreliable population; like gmail and yahoo getting marked as invalid
            #     disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "an invalid email domain extension")
            if row['C_Partner_Email_Address_Domain1'] == '1':
                disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, pathcodesBad['E71'])
            # if (row['C_Has_an_Undeliverable_Email_Address1'] == '1'
            # ):
            # disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "an undeliverable email address")
            # if (row['C_Do_Not_Contact1'] == '1'
            # ):
            # disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "being marked not to contact")
            if row['IsBounced'] == 'True':
                disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, pathcodesBad['O92'])
            if (row['Contacts_Inquiries_C_FirstName1'] == ''
                and row['C_FirstName'] == ''):
                disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, pathcodesBad['E67'])
            if (row['Contacts_Inquiries_C_LastName1'] == ''
                and row['C_LastName'] == ''):
                disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, pathcodesBad['E82'])
            if (row['Contacts_Inquiries_C_Company1'] == ''
                and row['C_Company'] == ''):
                disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, pathcodesBad['E83'])
            # if (row[recordFieldNames['recordPhoneBusiness']] == ''
            # and row[recordFieldNames['recordPhoneMobile']] == ''
            # ):
            # if (row['C_BusPhone'] == ''
            # and row['C_MobilePhone'] == ''
            # ):
            # disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "a missing phone number") #where is this required?! 000-02-17_12.25 wgreene
            #
            if row['Contacts_Inquiries_C_Country1'] != '':
                if (row['Contacts_Inquiries_C_Country1'].upper() == 'IN'
                    or row['Contacts_Inquiries_C_Country1'].upper() == 'INDIA'
                    ):
                    if (row['Contacts_Inquiries_C_State_Prov1'] == ''
                        and row['C_State_Prov'] == ''
                        ):
                        disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "missing a province but being from India")
            else:
                if (row['C_Country'] == 'IN'
                    or row['C_Country'] == 'INDIA'
                    ):
                    if (row['Contacts_Inquiries_C_State_Prov1'] == ''
                        and row['C_State_Prov'] == ''
                        ):
                        disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "missing a province but being from India") #filtered for the lead validation in SFDC called State_Mandatory_for_India: https://na4.salesforce.com/03d000CoRo
            #
            if (row['offer_blank'] == 1
                and row['tactic_blank'] == 1):
                disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "missing an offer and tactic ID")
            else:
                if row['offer_valid'] == 0:
                    disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "having a bad offer ID")
                if row['tactic_valid'] == 0:
                    disqualifyingFieldValues = "%s%s, " %(disqualifyingFieldValues, "having a bad tactic ID")
            #check for disqualifying pathcodes:
            disqualifyingPathcodes = disqualifyingPathcodes_default
            if row['C_Last_Lead_Funnel_Path11'] == '':
                disqualifyingPathcodes = "C_Last_Lead_Funnel_Path11 is blank; this should never happen since these records should be captured by 'recordHasNotFinishedLeadFunnel'."
            else:
                for pathcode, pathcodeDesc in pathcodesBad.items():
                    if pathcode in row['C_Last_Lead_Funnel_Path11']:
                        disqualifyingPathcodes = "%s%s: %s, " %(disqualifyingPathcodes, pathcode, pathcodeDesc)
            #
        if len(disqualifyingFieldValues) > disqualifyingFieldValues_default_len:
            disqualified_fieldValues = 1
        else:
            disqualifyingFieldValues = "Record NOT disqualified by field values"
        if len(disqualifyingPathcodes) > disqualifyingPathcodes_default_len:
            disqualified_pathcodes = 1
        else:
            disqualifyingPathcodes = "Record NOT disqualified by pathcodes"
        row['should_have_received_lead_id'] = 0
        row['discrepancy_in_lead_disqualification'] = 0
        if (disqualified_fieldValues == 0
                and disqualified_pathcodes == 0
                ):
            row['should_have_received_lead_id'] = 1
        if (disqualified_fieldValues != disqualified_pathcodes):
            row['discrepancy_in_lead_disqualification'] = 1
        row["disqualifyingFieldValues"] = disqualifyingFieldValues
        row["disqualifyingPathcodes"] = disqualifyingPathcodes

    return records


def monitoring_all(records, metric_list, adhoc):
    """gathers in the metric_list metrics that apply to all pulled records"""

    if not adhoc:
        if sum(row['createdAfter24HoursAgo'] for row in records) > 0:
            records = [row for row in records if row['createdAfter24HoursAgo'] == 1]

    # Count per source
    records__assessing_source = records
    for row in records__assessing_source:
        row["source_matched"] = 0
    sources_to_monitor = {
        'account-to-subscription',
        'ansible-hubspot-integration',
        'blind-clickthrough-integration',
        'cee-escalation-integration',
        'certain-integration',
        'developers-redhat-com-integration',
        'dynamic-form-integration',
        'enterprisersproject-com-integration',
        'integrate-integration',
        'inxpo-integration',
        'jboss-org-integration',
        'lookbookhq-integration',
        'MktgUserCreSvc-integration',
        'openshiftio-integration',
        'opensource-com-integration',
        'orbitera-integration',
        'RHDCPreferenceCenter',
        'qualtrics-integration',
        'redhat-com-integration',
        'seertech-integration',
        'skills-assessment-integration',
        'training-redhat-academy-integration',
        'training-video-library-integration',
        'UNAVAILABLE',
        'RHLS-Free-Integration',
        'RHDCPreferenceCenter',
        'vivastream-integration',
        'upload-wizard-integration-0',
        'upload-wizard-integration-1',
        'upload-wizard-integration-2',
        'upload-wizard-integration-3',
        'upload-wizard-integration-4',
        'upload-wizard-integration-5',
        'upload-wizard-integration-6',
        'upload-wizard-integration-7',
        'upload-wizard-integration-8',
        'upload-wizard-integration-9',
        'upload-wizard-integration-az',
    }
    pivot_dict = {}
    for value in sources_to_monitor:
        occurrences = 0
        for row in records__assessing_source:
            if row['Contacts_Inquiries_F_FormData_Source1'] == value:
                occurrences += 1
                row["source_matched"] = 1
        pivot_dict[value] = occurrences

    records__assessing_source = [row for row in records__assessing_source if row["source_matched"] == 0]
    occurrences = 0
    for row in records__assessing_source:
        if row['Contacts_Inquiries_F_FormData_Source1'] == '':
            occurrences += 1
            row["source_matched"] = 1
    pivot_dict["is_blank"] = occurrences

    nurture_campaign_indicators = [
        "campaign",
        "get ready",
        "go faster",
        "nurture"
    ]
    records__assessing_source = [row for row in records__assessing_source if row["source_matched"] == 0]
    occurrences = 0
    for row in records__assessing_source:
        for indicator in nurture_campaign_indicators:
            if indicator in row['Contacts_Inquiries_F_FormData_Source1'].lower():
                occurrences += 1
                row["source_matched"] = 1
                break
    pivot_dict["nurture_campaign"] = occurrences

    records__assessing_source = [row for row in records__assessing_source if row["source_matched"] == 0]
    pivot_dict["unaccounted_for"] = len(records__assessing_source)

    metric_desc = ("Count of occurences of this F_FormData_Source1.")
    metric_name_prefix = 'formsource_'
    for key, value in pivot_dict.items():
        metric_value = value
        metric_list.append({'metric_name': "%s%s" % (metric_name_prefix, key), 'metric_value': metric_value, 'metric_desc': metric_desc})

    if PRINT_OUTPUT:
        print("pivot of accounted sources\n")
        pprint(pivot_dict)
        print("pivot of unaccounted_for\n")
        pivot_dict = {}
        pivot_field = set()
        for row in records__assessing_source:
            pivot_field.add(row['Contacts_Inquiries_F_FormData_Source1'])
        for value in pivot_field:
            occurrences = 0
            for row in records__assessing_source:
                if row['Contacts_Inquiries_F_FormData_Source1'] == value:
                    occurrences += 1
            pivot_dict[value] = occurrences
        sorted_by_value = sorted(pivot_dict.items(), key=lambda kv: kv[1], reverse=True)
        pprint(sorted_by_value)

    return metric_list


def monitoring_subset(records, src, metric_list):
    """gathers in the metric_list metrics that apply to all pulled records"""

    # repeat the generic monitoring that is applied to all CDO
    metric_list = generic_analysis(
                      response=records,
                      date_field='CreatedAt',
                      status_field='Contacts_Inquiries_S_Data_Status1',
                      analyze_campaigns={"offer": "Contacts_Inquiries_A_OfferID1",
                                          "tactic": "Contacts_Inquiries_A_TacticID_External1"
                                          },
                      metric_prefix=src,
                      metric_list=metric_list,
                      print_output=PRINT_OUTPUT
                  )
    # end generic monitoring


    records_createdAfter24HoursAgo = [row for row in records if row['createdAfter24HoursAgo'] == 1]

    true_responded_date_unreasonable_cnt = sum(row['true_responded_date_unreasonable'] for row in records_createdAfter24HoursAgo)
    metric_desc = ("Records that have a true responded date that's more ",
    "than a month in the future or more than half a year in the past.")
    metric_name = 'true_responded_date_unreasonable'
    metric_value = true_responded_date_unreasonable_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})


    records_createdBetween5And29HoursAgo = [row for row in records if row['createdBetween5And29HoursAgo'] == 1]

    sfdc_leads_created = set()
    sfdc_contacts_created = set()
    for row in records_createdBetween5And29HoursAgo:
        if (row['createdAfter29HoursAgo'] == 1 and
            row['C_ZZ___SFDC_Lead_Created_Date1'] > row['CreatedAt']
        ):
            sfdc_leads_created.add(row['C_SFDCLeadID'])

        if (row['createdAfter29HoursAgo'] == 1 and
            row['C_ZZ___SFDC_Contact_Created_Date1'] > row['CreatedAt']
        ):
            sfdc_contacts_created.add(row['C_SFDCContactID'])

    sfdc_leads_created_cnt = len(sfdc_leads_created)
    metric_desc = ("Count of uniqe SFDC Leads that we created after the Contacts.Inquiries record was created.")
    metric_name = 'sfdc_leads_created'
    metric_value = sfdc_leads_created_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})

    sfdc_contacts_created_cnt = len(sfdc_contacts_created)
    metric_desc = ("Count of uniqe SFDC Contacts that we created after the Contacts.Inquiries record was created.",
    "This is not to say they were created by Eloqua integration as Eloqua integration does not create SFDC Contacts.",
    "They simply were coincidentally created after the Contacts.Inquiries record was, likely manually.")
    metric_name = 'sfdc_contacts_created'
    metric_value = sfdc_contacts_created_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})


    entered_lead_funnel_cnt = sum(row['entered_lead_funnel'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Records that have a C_Timestamp__Last_Entered_Lead_Funnel_Date1 greater than their created date.")
    metric_name = 'entered_lead_funnel'
    metric_value = entered_lead_funnel_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})

    entered_lead_funnel_not_cnt = len(records_createdBetween5And29HoursAgo) - entered_lead_funnel_cnt
    metric_desc = ("Records that have not finished the Lead Funnel.")
    metric_name = 'entered_lead_funnel_not'
    metric_value = entered_lead_funnel_not_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})


    should_have_received_lead_id_cnt = sum(row['should_have_received_lead_id'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Records that according to this scripts calculations should have passed to SFDC and received a Lead ID.")
    metric_name = 'should_have_received_lead_id'
    metric_value = should_have_received_lead_id_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})


    discrepancy_in_lead_disqualification_cnt = sum(row['discrepancy_in_lead_disqualification'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Records that according to my two methods of determing whether a record should have received a Lead ID ",
    "(by pathcode or field values), only one methods disqualified the lead."
    )
    metric_name = 'discrepancy_in_lead_disqualification'
    metric_value = discrepancy_in_lead_disqualification_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})


    campaigns_valid_cnt = sum(row['campaigns_valid'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Both the offer and tactic campaigns are populated and of valid format (r'000[a-zA-Z0-9]{15}$').")
    metric_name = 'campaigns_valid'
    metric_value = campaigns_valid_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})

    campaigns_valid_missing_memberships_cnt = sum(row['campaigns_valid_missing_memberships'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Both the offer and tactic campaigns are populated and of valid format but no SFDC Campaign memberships were given.")
    metric_name = 'campaigns_valid_missing_memberships'
    metric_value = campaigns_valid_missing_memberships_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})

    campaigns_valid_missing_membership_tactic_cnt = sum(row['campaigns_valid_missing_membership_tactic'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Both the offer and tactic campaigns are populated and of valid format, but tactic campaign didn't receive a membership.")
    metric_name = 'campaigns_valid_missing_membership_tactic'
    metric_value = campaigns_valid_missing_membership_tactic_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})

    campaigns_valid_missing_membership_offer_cnt = sum(row['campaigns_valid_missing_membership_offer'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Both the offer and Offer campaigns are populated and of valid format, but offer campaign didn't receive a membership.")
    metric_name = 'campaigns_valid_missing_membership_offer'
    metric_value = campaigns_valid_missing_membership_offer_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})

    offer_valid_missing_membership_cnt = sum(row['offer_valid_missing_membership'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Offer is valid but missing membership")
    metric_name = 'offer_valid_missing_membership'
    metric_value = offer_valid_missing_membership_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})

    tactic_valid_missing_membership_cnt = sum(row['tactic_valid_missing_membership'] for row in records_createdBetween5And29HoursAgo)
    metric_desc = ("Tactic is valid but missing membership")
    metric_name = 'tactic_valid_missing_membership'
    metric_value = tactic_valid_missing_membership_cnt
    metric_list.append({'metric_name': "%s%s" % (src, metric_name), 'metric_value': metric_value, 'metric_desc': metric_desc})

    return metric_list
