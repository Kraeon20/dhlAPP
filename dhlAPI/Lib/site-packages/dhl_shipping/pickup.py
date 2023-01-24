import dhl_shipping
import dhl_shipping.config
import dhl_shipping.common
import dhl_shipping.dhl_process

import xmltodict

import urllib2
import datetime
import random

class Pickup:

    def __init__(self):
        self.date_now = datetime.datetime.now()

    def schedule_pickup(self, dict_param):
        return_status = True
        return_message = ''
        pickup_confirmation_number = ''
        return_dict = dict()
        common_obj = dhl_shipping.common.Common()

        # get the prepared XML data as string - this portion also check if xml wel formated  -  ie user sending correct data 
        xml_formated_data = self.pickup_xml(dict_param)
        if xml_formated_data['status']:
            xml_formated_data_string = xml_formated_data['data']
        else:
            return_dict.update(
                {
                    'status': False,
                    'message': xml_formated_data['message'],
                }
            )
            return return_dict
        
        try:
            url_response_data = dict()
            dhl_process_obj = dhl_shipping.dhl_process.DhlProcess()
            returned_data = dhl_process_obj.process_pickup(xml_formated_data_string)
            if 'return_dhl_api_response' in returned_data.keys():
                return_status = True
                url_response_data = returned_data['return_dhl_api_response']
            else:
                return_status = False
                return_message = dhl_shipping.config.message_max_response_time
                return_dict.update(
                    {
                        'status': return_status,
                        'message': return_message,
                    }
                )
                return return_dict
        except:
            return_status = False
            return_message = dhl_shipping.config.message_dhl_url_down
            return_dict.update(
                {
                    'status': return_status,
                    'message': return_message,
                }
            )
        else:
            # format the data to dictionary and return
            dict_response = xmltodict.parse(url_response_data)
            
            # get the action note returned by DHL and check if it is  Success - if success then all are fine proceed 
            try:
                action_note = common_obj.in_dictionary_all('ActionNote', dict_response)
                try:
                    if action_note == False:
                        action_note = list()
                except Exception as e:
                    action_note = list()
            except Exception as e:
                action_note = list()

            if 'Success' in action_note: # action_note is a list type
                # get the confirmation number
                pickup_confirmation_number = common_obj.in_dictionary_all('ConfirmationNumber', dict_response)
                pickup_confirmation_number = ''.join(map(str, pickup_confirmation_number))
                return_status = True
                return_message = dhl_shipping.config.message_pickup_success
            else:
                # some error by dhl which stopping to proceed
                error_found = common_obj.in_dictionary_all('ConditionData', dict_response)
                if error_found != False:
                    # some error by dhl
                    return_status = False
                    return_message = error_found[0]

            if dhl_shipping.dhl_response_flag:
                return_dict.update({'dhl_response': dict_response})
            if dhl_shipping.dhl_xml_flag:
                return_dict.update({'request_xml_to_dhl': xml_formated_data_string})

            return_dict.update(
                {
                    'status': return_status,
                    'message': return_message,
                    'pickup_confirmation_number': str(pickup_confirmation_number),
                }
            )
        return return_dict

    def pickup_xml(self, dict_param):
        try:
            common_obj = dhl_shipping.common.Common()
            addresses = dict_param['addresses']  # From and To Address
            pieces = dict_param['pieces']  # Measurement Units
            package = dict_param['package'] # shipment package
            pickup_details = dict_param['pickup_details']  # pickup time and schedule
            
            optional_data = dict_param['optional_data']  # Measurement Units

            message_reference = ''.join(random.choice('0123456789') for i in range(28))  # as per DHL its must be between 28 to 32 char
            #pickup_date = datetime.datetime.now() # changable

            # piece info 
            piece_details_info = '<Pieces>' + str(len(pieces)) + '</Pieces>'
            piece_details_info += '<weight>'
            piece_details_info += '<Weight>' + package['total_weight'] + '</Weight>'
            piece_details_info += '<WeightUnit>' + package['weight_unit'] + '</WeightUnit>'
            piece_details_info += '</weight>'

            # reagon code based on country
            region_code = common_obj.get_dhl_region_code(addresses['from_country'])  # AP|AM|EU 
            x_region_code_str = ''
            xsd_region_code_str = ''
            phone_extn_str = ''
            requestor_company_name = ''
            #place_details_str = '<DivisionName>' + addresses['from_state'] + '</DivisionName>'  # State of the pickup place - Optional - Max 35 char
            place_details_str = '<CountryCode>' + addresses['from_country'] + '</CountryCode>'
            place_details_str += '<PostalCode>' + addresses['from_zipcode'] + '</PostalCode>'
            region_code = addresses['from_region_code']  # AP|AM|EA
            if region_code == 'AP':
                x_region_code_str = region_code
                xsd_region_code_str = ''
                phone_extn_str = '<PhoneExtension></PhoneExtension>'
            elif region_code == 'AM':
                x_region_code_str = ''
                xsd_region_code_str = ''
                phone_extn_str = '<PhoneExtension></PhoneExtension>'
            elif region_code == 'EA':
                x_region_code_str = region_code
                xsd_region_code_str = '_' + region_code
                phone_extn_str = ''
                piece_details_info = ''  # only for EA
                requestor_company_name = '<CompanyName>' + addresses['from_company_name'] + '</CompanyName>'
                place_details_str = '<CountryCode>' + addresses['from_country'] + '</CountryCode>'
                place_details_str += '<PostalCode>' + addresses['from_zipcode'] + '</PostalCode>'

            # prepare the xml
            xml_str = '<?xml version="1.0" encoding="UTF-8"?>'

            xml_str += '<req:BookPickupRequest' + x_region_code_str + ' xmlns:req="http://www.dhl.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' 
            xml_str += 'xsi:schemaLocation="http://www.dhl.com ship-val-req' + xsd_region_code_str + '.xsd">'

            # Request Service Header
            xml_str += '<Request>'
            xml_str += '<ServiceHeader>'
            xml_str += '<MessageTime>' + self.date_now.strftime("%Y-%m-%dT%I:%M:%S+00:00") + '</MessageTime>'
            xml_str += '<MessageReference>' + message_reference +  '</MessageReference>'
            xml_str += '<SiteID>' + dhl_shipping.dhl_site_id +'</SiteID>'
            xml_str += '<Password>' + dhl_shipping.dhl_site_password +'</Password>'
            xml_str += '</ServiceHeader>'
            xml_str += '</Request>'
            # Request Service Header ENDS

            # Requestor -- ie the sender - ie from where package will be collected - ie the from address
            xml_str += '<Requestor>'
            xml_str += '<AccountType>D</AccountType>'  # C (Credit Card) | D (DHL account).
            xml_str += '<AccountNumber>' + dhl_shipping.dhl_account_no + '</AccountNumber>' #?? 
            xml_str += '<RequestorContact>'
            xml_str += '<PersonName>' + addresses['from_name'] + '</PersonName>'
            xml_str += '<Phone>' + addresses['from_phone_no'] + '</Phone>'
            xml_str += phone_extn_str
            xml_str += '</RequestorContact>'
            xml_str += requestor_company_name
            xml_str += '</Requestor>'

            # Place
            xml_str += '<Place>'
            xml_str += '<LocationType>' + addresses['from_location_type'] + '</LocationType>'  # B (Business), R (Residence) C (Business/Residence)
            xml_str += '<CompanyName>' + addresses['from_company_name'] + '</CompanyName>'  
            xml_str += '<Address1>' + addresses['from_address_line_one'] + '</Address1>'
            xml_str += '<Address2>' + addresses['from_address_line_two'] + '</Address2>'
            xml_str += '<PackageLocation>' + addresses['from_package_location'] + '</PackageLocation>'  # Package Location in the pickup place. E.g. Front Desk
            xml_str += '<City>' + addresses['from_city'] + '</City>'
            xml_str += place_details_str
            xml_str += '</Place>'
            # Billing ENDS

            # Pickup
            xml_str += '<Pickup>'
            xml_str += '<PickupDate>' + pickup_details['pickup_date'] + '</PickupDate>'  # YYYY-MM-DD format
            xml_str += '<ReadyByTime>' + pickup_details['ready_by_time'] + '</ReadyByTime>'  # hh:mm ie 14:35
            xml_str += '<CloseTime>' + pickup_details['close_time'] + '</CloseTime>'  # hh:mm ie 15:35
            xml_str += piece_details_info
            xml_str += '</Pickup>'
            # Pickup ENDS

            # Pickup Contact
            xml_str += '<PickupContact>'
            xml_str += '<PersonName>' + addresses['from_name'] + '</PersonName>' 
            xml_str += '<Phone>' + addresses['from_phone_no'] + '</Phone>' 
            xml_str += phone_extn_str 
            xml_str += '</PickupContact>'
            # Pickup Contact ENDS

            xml_str += '</req:BookPickupRequest' + x_region_code_str + '>'

            return_dict = {
                'status': True,
                'message': '',
                'data': xml_str,
            }
            return return_dict
        except:
            return_dict = {
                'status': False,
                'message': dhl_shipping.config.message_request_data_bad_format,
                'data': '',
            }
            return return_dict
