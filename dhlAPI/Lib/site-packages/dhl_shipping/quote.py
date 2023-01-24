import dhl_shipping
import dhl_shipping.config
import dhl_shipping.common
import dhl_shipping.dhl_process

import xmltodict

import urllib2
import datetime
import random

class Quote:

    def __init__(self):
        self.date_now = datetime.datetime.now()
        pass

    def get_quote(self, dict_param):
        return_status = True
        return_message = ''
        return_dict = dict()

        # get the prepared XML data as string - this portion also check if xml wel formated  -  ie user sending correct data 
        xml_formated_data = self.quote_xml(dict_param)
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
            # here prepare to call the dhl api through the process which will check max execution time
            url_response_data = dict()
            dhl_process_obj = dhl_shipping.dhl_process.DhlProcess()
            returned_data = dhl_process_obj.process_quote(xml_formated_data_string)
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

            # check if error returned by dhl
            common_obj = dhl_shipping.common.Common()
            error_found = common_obj.in_dictionary_all('ConditionData', dict_response)
            if error_found != False:
                # some error by dhl
                return_status = False
                return_message = error_found[0]
            else:
                # no error
                return_status = True
                return_message = dhl_shipping.config.message_quote_success
                dimensional_weight = common_obj.in_dictionary_all('DimensionalWeight', dict_response)[0]
                currency_code = common_obj.in_dictionary_all('CurrencyCode', dict_response)[0]
                weight_charge = common_obj.in_dictionary_all('WeightCharge', dict_response)[0]
                shipping_charge = common_obj.in_dictionary_all('ShippingCharge', dict_response)[0]
                product_shortName = common_obj.in_dictionary_all('ProductShortName', dict_response)[0]
                local_product_name = common_obj.in_dictionary_all('LocalProductName', dict_response)[0]
                weight_unit = common_obj.in_dictionary_all('WeightUnit', dict_response)[0]
                
                return_dict.update({
                    'quote_data':{
                        'dimensional_weight': dimensional_weight,
                        'weight_unit': weight_unit,
                        'currency_code': currency_code,
                        #'weight_charge': weight_charge,
                        'shipping_charge': shipping_charge,
                        'product_shortName': product_shortName,
                        'local_product_name': local_product_name,
                    }
                })

            if dhl_shipping.dhl_xml_flag:
                return_dict.update({'request_xml_to_dhl': xml_formated_data_string})
            if dhl_shipping.dhl_response_flag:
                return_dict.update({'dhl_response': dict_response})

            return_dict.update(
                {
                    'status': return_status,
                    'message': return_message,
                }
            )
        return return_dict

    def quote_xml(self, dict_param):
        try:
            addresses = dict_param['addresses']  # From and To Address
            units = dict_param['units']  # Measurement Units
            pieces = dict_param['pieces']  # Measurement Units
            optional_data = dict_param['optional_data']  # Measurement Units

            message_reference = ''.join(random.choice('0123456789') for i in range(28))  # as per DHL its must be between 28 to 32 char
            #pickup_date = datetime.datetime.now() # changable

            xml_str = '<?xml version="1.0" encoding="UTF-8"?>'

            xml_str += '<p:DCTRequest xmlns:p="http://www.dhl.com" xmlns:p1="http://www.dhl.com/datatypes" xmlns:p2="http://www.dhl.com/DCTRequestdatatypes" '
            xml_str += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.dhl.com DCT-req.xsd ">'

            # GetQuote
            xml_str += '<GetQuote>'

            # Request
            xml_str += '<Request>'
            xml_str += '<ServiceHeader>'
            xml_str += '<MessageTime>' + self.date_now.strftime("%Y-%m-%dT%I:%M:%S+00:00") + '</MessageTime>'
            xml_str += '<MessageReference>' + message_reference +  '</MessageReference>'
            xml_str += '<SiteID>' + dhl_shipping.dhl_site_id +'</SiteID>'
            xml_str += '<Password>' + dhl_shipping.dhl_site_password +'</Password>'
            xml_str += '</ServiceHeader>'
            xml_str += '</Request>'
            # Request ENDS

            # From Address
            xml_str += '<From>'
            xml_str += '<CountryCode>' + addresses['from_country'] + '</CountryCode>'
            xml_str += '<Postalcode>' + addresses['from_zipcode'] + '</Postalcode>'
            xml_str += '<City>' + addresses['from_city'] + '</City>'
            xml_str += '</From>'
            # From Address ENDS

            # BkgDetails
            try:
                if 'quote_for_date' in optional_data.keys():
                    quote_for_date = optional_data['quote_for_date']
                    quote_for_date = str(quote_for_date)
                else:
                    quote_for_date = self.date_now.strftime("%Y-%m-%d")
            except Exception as e:
                quote_for_date = self.date_now.strftime("%Y-%m-%d")
            
            xml_str += '<BkgDetails>'
            xml_str += '<PaymentCountryCode>MY</PaymentCountryCode>'
            xml_str += '<Date>' + quote_for_date + '</Date>' # for weekend its change for us
            xml_str += '<ReadyTime>PT10H21M</ReadyTime>'
            xml_str += '<ReadyTimeGMTOffset>+01:00</ReadyTimeGMTOffset>'
            xml_str += '<DimensionUnit>' + units['dimension_unit'] + '</DimensionUnit>'
            xml_str += '<WeightUnit>' + units['weight_unit'] + '</WeightUnit>'

            xml_str += '<Pieces>'
            piece_id = 1
            for piece in pieces:
                xml_str += '<Piece>'
                xml_str += '<PieceID>' + str(piece_id) + '</PieceID>'
                xml_str += '<Height>' + str(piece['piece_height']) + '</Height>'
                xml_str += '<Depth>' + str(piece['piece_depth']) + '</Depth>'
                xml_str += '<Width>' + str(piece['piece_width']) + '</Width>'
                xml_str += '<Weight>' + str(piece['piece_weight']) + '</Weight>'
                xml_str += '</Piece>'
                piece_id = piece_id + 1
            xml_str += '</Pieces>'

            xml_str += '<PaymentAccountNumber>' + dhl_shipping.dhl_account_no + '</PaymentAccountNumber>'
            xml_str += '<IsDutiable>' + optional_data['is_dutiable'] + '</IsDutiable>'
            xml_str += '<NetworkTypeCode>AL</NetworkTypeCode>'  # decide

            xml_str += '<QtdShp>'
            xml_str += '<GlobalProductCode>P</GlobalProductCode>'
            #xml_str += '<LocalProductCode>P</LocalProductCode>'  # taken away as for GB to other countries it will not work - confirmed with dhl
            xml_str += '</QtdShp>'

            ins_val = optional_data.get('insured_value', 0)
            ins_ccy = optional_data.get('insured_currency', '')
            if ins_val:
                """ as per dhl new instruction we should pass it if we want qoute with insurance.
                The new change on dhl side is that if it even passsed as 0 still it will return quote with insurance.
                therefore no choice but to remove it if insurance value is 0 or empty to get quote without insurance.
                This change made on 14.11.2017
                """
                xml_str += '<InsuredValue>' + str(ins_val) + '</InsuredValue>'
                xml_str += '<InsuredCurrency>' + ins_ccy + '</InsuredCurrency>'
            xml_str += '</BkgDetails>'
            # BkgDetails ENDS

            # To Address
            xml_str += '<To>'
            xml_str += '<CountryCode>' + addresses['to_country'] + '</CountryCode>'
            xml_str += '<Postalcode>' + addresses['to_zipcode'] + '</Postalcode>'
            xml_str += '<City>' + addresses['to_city'] + '</City>'
            xml_str += '</To>'
            # To Address ENDS

            xml_str += '<Dutiable>'
            xml_str += '<DeclaredCurrency>' + optional_data['declared_currency'] + '</DeclaredCurrency>' # decide
            xml_str += '<DeclaredValue>' + optional_data['declared_value'] + '</DeclaredValue>'
            xml_str += '</Dutiable>'

            xml_str += '</GetQuote>'
            # GetQuote ENDS

            xml_str += '</p:DCTRequest>'

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
