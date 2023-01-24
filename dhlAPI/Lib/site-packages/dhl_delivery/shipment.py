import dhl_delivery
import dhl_delivery.config
import dhl_delivery.common
import dhl_delivery.dhl_process

import xmltodict

import datetime
import random
import base64
import os
import errno


class Shipment:

    def __init__(self):
        self.date_now = datetime.datetime.now()

    def get_shipment(self, dict_param):
        return_status = True
        return_message = ''
        pickup_return_status = False
        pickup_return_message = ''
        airway_bill_number = ''
        output_pdf_image_str = ''  # base 64 encoded pdf
        awb_pdf_file_path_name = ''
        awb_pdf_file_name = ''
        return_dict = dict()
        pickup_returned_data = dict()
        pickup_confirmation_number = ''
        product_short_name = ''
        package_type = ''
        chargeable_weight = ''
        dimensional_weight = ''
        insured_amount = ''
        shipment_date = ''  # ie pickup or dropoff to dhl date, not the date when its being created

        request_for_pickup = False
        common_obj = dhl_delivery.common.Common()

        # get the prepared XML data as string - this portion also check if xml wel formated  -  ie user sending correct data
        xml_formated_data = self.shipment_xml(dict_param)
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
            dhl_process_obj = dhl_delivery.dhl_process.DhlProcess()
            returned_data = dhl_process_obj.process_shipment(
                xml_formated_data_string)
            if 'return_dhl_api_response' in returned_data.keys():
                return_status = True
                url_response_data = returned_data['return_dhl_api_response']
            else:
                return_status = False
                return_message = dhl_delivery.config.message_max_response_time
                return_dict.update(
                    {
                        'status': return_status,
                        'message': return_message,
                    }
                )
                return return_dict
        except:
            return_status = False
            return_message = dhl_delivery.config.message_dhl_url_down
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
            action_note = common_obj.in_dictionary_all(
                'ActionNote', dict_response, 'nothing found')
            if 'Success' in action_note:  # action_note is a list type
                return_status = True
                return_message = dhl_delivery.config.message_shipment_success
                # set pick up - if pickup provided
                if 'pickup_details' in dict_param:
                    if len(dict_param['pickup_details']) > 0:
                        request_for_pickup = True
                        pickup_returned_data = dhl_delivery.pickup.schedule_pickup(
                            dict_param)
                        if pickup_returned_data['status']:
                            pickup_confirmation_number_temp = pickup_returned_data[
                                'pickup_confirmation_number']
                            pickup_confirmation_number = ''.join(
                                map(str, pickup_confirmation_number_temp))
                        pickup_return_status = pickup_returned_data['status']
                        pickup_return_message = pickup_returned_data['message']

                # get the airway bill number
                airway_bill_number = common_obj.in_dictionary_all(
                    'AirwayBillNumber', dict_response)
                airway_bill_number = ''.join(map(str, airway_bill_number))

                # get product short name
                product_short_name = common_obj.in_dictionary_all(
                    'ProductShortName', dict_response)
                product_short_name = ''.join(map(str, product_short_name))

                # get package type
                package_type = common_obj.in_dictionary_all(
                    'PackageType', dict_response)
                package_type = ''.join(map(str, package_type))

                # Chargeable Weight
                chargeable_weight = common_obj.in_dictionary_all(
                    'ChargeableWeight', dict_response)
                chargeable_weight = ''.join(map(str, chargeable_weight))

                # Dimensional Weight
                dimensional_weight = common_obj.in_dictionary_all(
                    'DimensionalWeight', dict_response)
                dimensional_weight = ''.join(map(str, dimensional_weight))

                # Insured Amount
                insured_amount = common_obj.in_dictionary_all(
                    'InsuredAmount', dict_response)
                insured_amount = ''.join(map(str, insured_amount))

                # Shipment Date ie pickup or dropoff to dhl, not the date when its being created
                shipment_date = common_obj.in_dictionary_all(
                    'ShipmentDate', dict_response)
                shipment_date = ''.join(map(str, shipment_date))

                if 'optional_data' in dict_param.keys():
                    optional_data = dict_param['optional_data']

                    # get the pdf file image pdf (base 64 encoded)
                    if 'return_pdf_image_str' in optional_data.keys():
                        if optional_data['return_pdf_image_str']:
                            output_image_list = common_obj.in_dictionary_all(
                                'OutputImage', dict_response)
                            output_pdf_image_str = ''.join(
                                map(str, output_image_list))

                    # now create the pdf file form the image (base 64 string for pdf)
                    if 'return_pdf_file' in optional_data.keys():
                        if optional_data['return_pdf_file']:
                            create_pdf_data = self.create_pdf_awb(
                                dict_param, dict_response, airway_bill_number)
                            awb_pdf_file_path_name = create_pdf_data['awb_pdf_file_path_name']
                            awb_pdf_file_name = create_pdf_data['awb_pdf_file_name']
            else:
                # some error by dhl which stopping to proceed
                error_found = common_obj.in_dictionary_all(
                    'ConditionData', dict_response)
                if error_found != False:
                    # some error by dhl
                    return_status = False
                    return_message = error_found[0]

            if dhl_delivery.dhl_response_flag:
                return_dict.update(
                    {'dhl_response': {'dhl_shipment_response': dict_response}})
                if 'dhl_response' in pickup_returned_data.keys():
                    return_dict.update({'dhl_response': {'dhl_shipment_response': dict_response,
                                                         'dhl_pickup_response': pickup_returned_data['dhl_response']}})
            if dhl_delivery.dhl_xml_flag:
                return_dict.update(
                    {'request_xml_to_dhl': xml_formated_data_string})

            return_dict.update(
                {
                    'shipment_response': {
                        'status': return_status,
                        'message': return_message,
                        'airway_bill_number': airway_bill_number,
                        'awb_pdf_file_path_name': awb_pdf_file_path_name,
                        'awb_pdf_file_name': awb_pdf_file_name,
                        'output_pdf_image_str': output_pdf_image_str,
                        'product_short_name': product_short_name,
                        'package_type': package_type,
                        'chargeable_weight': chargeable_weight,
                        'dimensional_weight': dimensional_weight,
                        'insured_amount': insured_amount,
                        'shipment_date': shipment_date
                    },
                    'pickup_response': {
                        'status': pickup_return_status,
                        'message': pickup_return_message,
                        # True if user set up request for pickup else False
                        'request_for_pickup': request_for_pickup,
                        'pickup_confirmation_number': pickup_confirmation_number
                    }
                }
            )
        return return_dict

    def create_pdf_awb(self, dict_param, dict_response, airway_bill_number=''):
        common_obj = dhl_delivery.common.Common()
        awb_pdf_file_path_name = ''
        # now create the pdf file form the image (base 64 string for pdf)
        if 'optional_data' in dict_param.keys():
            awb_pdf_file_path = ''
            awb_pdf_file_name = ''
            # awb file name and path to store
            optional_data = dict_param['optional_data']
            if 'awb_pdf_file_path' in optional_data.keys():
                awb_pdf_file_path = optional_data['awb_pdf_file_path']
            if not awb_pdf_file_path:
                awb_pdf_file_path = os.path.join('pdf_shipment_label_default')
            if awb_pdf_file_path:
                # file path and name
                if 'awb_pdf_file_name' in optional_data.keys():
                    awb_pdf_file_name = optional_data['awb_pdf_file_name']
                if not awb_pdf_file_name:
                    awb_pdf_file_name = 'dhl_awb.pdf'
                # Change the name of awb - prefix the file name with Airway Bill Number
                if not airway_bill_number:
                    airway_bill_number = common_obj.in_dictionary_all(
                        'AirwayBillNumber', dict_response)
                    airway_bill_number = ''.join(map(str, airway_bill_number))
                awb_pdf_file_name = airway_bill_number + '__' + awb_pdf_file_name

                # create the pdf file from the base 64
                output_image_list = common_obj.in_dictionary_all(
                    'OutputImage', dict_response)
                output_image_str = ''.join(map(str, output_image_list))
                file_data = base64.urlsafe_b64decode(
                    output_image_str.encode('UTF-8'))

                # if folder not found then create one
                awb_pdf_file_path_name = os.path.join(
                    awb_pdf_file_path, awb_pdf_file_name)
                if not os.path.exists(os.path.dirname(awb_pdf_file_path_name)):
                    try:
                        os.makedirs(os.path.dirname(awb_pdf_file_path_name))
                    except OSError as exc:
                        if exc.errno != errno.EEXIST:
                            raise
                with open(awb_pdf_file_path_name, 'w') as the_file:  # wb dont save
                    the_file.write(file_data)
                    the_file.close()
        return {'awb_pdf_file_path_name': awb_pdf_file_path_name, 'awb_pdf_file_name': awb_pdf_file_name}

    def shipment_xml(self, dict_param):
        try:
            addresses = dict_param['addresses']  # From and To Address
            pieces = dict_param['pieces']  # Measurement Units
            package = dict_param['package']  # shipment package

            # optional_data = dict_param['optional_data']  # Measurement Units

            # as per DHL its must be between 28 to 32 char
            message_reference = ''.join(
                random.choice('0123456789') for i in range(28))
            # pickup_date = datetime.datetime.now() # changable

            xml_str = '<?xml version="1.0" encoding="UTF-8"?>'

            xml_str += '<req:ShipmentValidateRequestAP xmlns:req="http://www.dhl.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            xml_str += 'xsi:schemaLocation="http://www.dhl.com ship-val-req_AP.xsd">'

            # Request Service Header
            xml_str += '<Request>'
            xml_str += '<ServiceHeader>'
            xml_str += '<MessageTime>' + \
                self.date_now.strftime(
                    "%Y-%m-%dT%I:%M:%S+00:00") + '</MessageTime>'
            xml_str += '<MessageReference>' + message_reference + '</MessageReference>'
            xml_str += '<SiteID>' + dhl_delivery.dhl_site_id + '</SiteID>'
            xml_str += '<Password>' + dhl_delivery.dhl_site_password + '</Password>'
            xml_str += '</ServiceHeader>'
            xml_str += '</Request>'
            # Request Service Header ENDS

            xml_str += '<LanguageCode>en</LanguageCode>'
            xml_str += '<PiecesEnabled>Y</PiecesEnabled>'

            # Billing
            xml_str += '<Billing>'
            xml_str += '<ShipperAccountNumber>' + \
                dhl_delivery.dhl_account_no + '</ShipperAccountNumber>'
            xml_str += '<ShippingPaymentType>' + \
                dhl_delivery.shipping_payment_type + '</ShippingPaymentType>'
            xml_str += '<DutyPaymentType>' + \
                dhl_delivery.duty_payment_type + '</DutyPaymentType>'
            xml_str += '</Billing>'
            # Billing ENDS

            # Consignee - ie the receiver - is to where the package will be send to - ie the to address
            xml_str += '<Consignee>'
            xml_str += '<CompanyName>' + \
                addresses['to_company_name'] + '</CompanyName>'
            xml_str += '<AddressLine>' + \
                addresses['to_address_line_one'] + '</AddressLine>'
            xml_str += '<AddressLine>' + \
                addresses['to_address_line_two'] + '</AddressLine>'  # optionl
            xml_str += '<City>' + addresses['to_city'] + '</City>'
            xml_str += '<PostalCode>' + \
                addresses['to_zipcode'] + '</PostalCode>'
            xml_str += '<CountryCode>' + \
                addresses['to_country'] + '</CountryCode>'
            xml_str += '<CountryName>' + \
                addresses['to_country_name'] + '</CountryName>'
            xml_str += '<Contact>'
            xml_str += '<PersonName>' + addresses['to_name'] + '</PersonName>'
            xml_str += '<PhoneNumber>' + \
                addresses['to_phone_no'] + '</PhoneNumber>'
            xml_str += '</Contact>'
            xml_str += '</Consignee>'
            # Consignee ENDS

            # Dutiable
            xml_str += '<Dutiable>'
            xml_str += '<DeclaredValue>' + \
                str(package['declared_value']) + '</DeclaredValue>'
            # currency code  -  3 letter abbriviation
            xml_str += '<DeclaredCurrency>' + \
                package['declared_currency'] + '</DeclaredCurrency>'
            xml_str += '</Dutiable>'
            # Dutiable ENDS

            # Reference
            xml_str += '<Reference>'
            xml_str += '<ReferenceID>' + \
                str(package['reference_id']) + '</ReferenceID>'
            xml_str += '<ReferenceType>St</ReferenceType>'  # optional
            xml_str += '</Reference>'
            # Reference ENDS

            # ShipmentDetails
            xml_str += '<ShipmentDetails>'
            xml_str += '<NumberOfPieces>' + \
                str(len(pieces)) + '</NumberOfPieces>'
            # currency code  -  3 letter abbriviation
            xml_str += '<CurrencyCode>' + \
                package['declared_currency'] + '</CurrencyCode>'
            xml_str += '<Pieces>'
            piece_id = 1
            for piece in pieces:
                xml_str += '<Piece>'
                xml_str += '<PieceID>' + str(piece_id) + '</PieceID>'
                xml_str += '<PackageType>' + \
                    str(piece['package_type']) + '</PackageType>'  # DF|YP etc
                xml_str += '<Weight>' + \
                    str(piece['piece_weight']) + '</Weight>'
                xml_str += '<Depth>' + str(piece['piece_depth']) + '</Depth>'
                xml_str += '<Width>' + str(piece['piece_width']) + '</Width>'
                xml_str += '<Height>' + \
                    str(piece['piece_height']) + '</Height>'
                xml_str += '</Piece>'
                piece_id = piece_id + 1
            xml_str += '</Pieces>'
            xml_str += '<PackageType>' + \
                str(package['package_type']) + '</PackageType>'  # DF|YP etc
            xml_str += '<Weight>' + str(package['total_weight']) + '</Weight>'
            xml_str += '<DimensionUnit>' + \
                str(package['dimension_unit']) + '</DimensionUnit>'
            xml_str += '<WeightUnit>' + \
                str(package['weight_unit']) + '</WeightUnit>'
            xml_str += '<GlobalProductCode>' + \
                str(package['global_product_code']) + \
                '</GlobalProductCode>'  # as P
            xml_str += '<LocalProductCode>' + \
                str(package['local_product_code']) + \
                '</LocalProductCode>'  # as P
            xml_str += '<DoorTo>DD</DoorTo>'
            # Shipment date for when package(s) will be shipped (but usually current date)  ' + self.date_now.strftime("%Y-%m-%d") + '
            xml_str += '<Date>' + str(package['shipment_date']) + '</Date>'
            xml_str += '<Contents>' + \
                str(package['content_description']) + '</Contents>'
            xml_str += '<IsDutiable>' + \
                str(package['is_dutiable']) + \
                '</IsDutiable>'  # Yes|No - Default is No
            # Insured Amount (Required if Special Service of ‘I’ – Insurance is provided in request)
            xml_str += '<InsuredAmount>' + \
                str(package['insured_amount']) + '</InsuredAmount>'
            xml_str += '</ShipmentDetails>'
            # ShipmentDetails ENDS

            # Shipper - is the sender - ie from where package will be collected - ie the from address
            xml_str += '<Shipper>'
            xml_str += '<ShipperID>AXW56546</ShipperID>'  # a random number <=30
            xml_str += '<CompanyName>' + \
                addresses['from_company_name'] + '</CompanyName>'
            xml_str += '<AddressLine>' + \
                addresses['from_address_line_one'] + '</AddressLine>'
            xml_str += '<AddressLine>' + \
                addresses['from_address_line_two'] + \
                '</AddressLine>'  # optional
            xml_str += '<City>' + addresses['from_city'] + '</City>'
            xml_str += '<PostalCode>' + \
                addresses['from_zipcode'] + '</PostalCode>'
            xml_str += '<CountryCode>' + \
                addresses['from_country'] + '</CountryCode>'
            xml_str += '<CountryName>' + \
                addresses['from_country_name'] + '</CountryName>'
            xml_str += '<Contact>'
            xml_str += '<PersonName>' + \
                addresses['from_name'] + '</PersonName>'
            xml_str += '<PhoneNumber>' + \
                addresses['from_phone_no'] + '</PhoneNumber>'
            xml_str += '</Contact>'
            xml_str += '</Shipper>'
            # Shipper ENDS

            # Special Service - Totally optional
            if 'special_service_type' in package.keys():
                if package['special_service_type']:
                    xml_str += '<SpecialService>'
                    # Insured Amount (Required if Special Service of ‘I’ – Insurance is provided in request)
                    xml_str += '<SpecialServiceType>' + \
                        str(package['special_service_type']) + \
                        '</SpecialServiceType>'
                    xml_str += '</SpecialService>'
            # Special Service

            xml_str += '<LabelImageFormat>PDF</LabelImageFormat>'
            xml_str += '</req:ShipmentValidateRequestAP>'

            return_dict = {
                'status': True,
                'message': '',
                'data': xml_str,
            }
            return return_dict
        except:
            return_dict = {
                'status': False,
                'message': dhl_delivery.config.message_request_data_bad_format,
                'data': '',
            }
            return return_dict
