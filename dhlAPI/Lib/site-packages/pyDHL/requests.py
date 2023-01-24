from requests import post as _post
from datetime import datetime, timedelta
from collections import OrderedDict as _dict


CONFIG = {
    'sandbox': True,
}


def set_credentials(credentials):
    CONFIG['account'] = credentials['account']
    CONFIG['username'] = credentials['username']
    CONFIG['password'] = credentials['password']


def set_sandbox(mode=True):
    CONFIG['sandbox'] = True if mode is True else False


def _get_endpoint(tail):
    return 'https://wsbexpress.dhl.com/rest/{}/{}'.format('sndpt' if CONFIG['sandbox'] else 'gbl', tail)


TRACKING_LAST = 'LAST_CHECK_POINT_ONLY'
TRACKING_ALL = 'ALL_CHECK_POINTS'

DATETIME_FORMAT_GMT = "%Y-%m-%dT%H:%M:%SGMT"
DATETIME_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT_Z = "%Y-%m-%dT%H:%M:%SZ"
HOUR_MIN_FORMAT = "%H:%M"


def date_to_str(date, format=DATETIME_FORMAT_GMT):
    date_str = date.strftime(format)
    if format == DATETIME_FORMAT_GMT:
        if date.strftime("%z") == "":
            date_str += "+00:00"
        else:
            date_str += date.strftime("%z")[:3] + ':' + date.strftime("%z")[3:]

    return date_str


def post(endpoint, body):
    response = _post(endpoint, auth=(CONFIG['username'], CONFIG['password']), json=body)

    if not response.ok:
        response.code, response.error_type = response.status_code, response.reason
    else:
        # find 'Notification' dictionary
        response_body = response.json()
        for element in response_body.values():

            # special case for rate response
            if element.get('Provider'):
                element = element['Provider'][0]

            notification = element.get('Notification')
            if notification:
                code, message = notification[0]["@code"], notification[0]["Message"]
                if code != "0":
                    # there was a error, build new response with error data
                    response.code = code
                    response.error_type = message
                    response.status_code = 500

    return response


def _prepare_requested_packages(shipment):
    # prepare requested packages
    packages = []
    d_packages = {}
    for number, package in enumerate(shipment['packages']):
        str_number = str(number + 1)
        reference = package.get('reference', "Piece " + str_number)

        packages.append({
            '@number': str_number,
            'Weight': package['weight'],
            'Dimensions': {'Length': package['length'], 'Width': package['width'], 'Height': package['height']},
            'CustomerReferences': reference
        })

        d_packages[str_number] = package

    return packages, d_packages


def _ship(shipment, upper_case=False):
    def upper_values(dictionary):
        return {k: str(v).upper() for k, v in dictionary.items()}

    shipper, recipient = shipment['sender'], shipment['recipient']
    ship = _dict({
        'Shipper': {
            'Contact': {
                'PersonName': shipper['name'],
                'CompanyName': shipper['company'],
                'PhoneNumber': shipper['phone'],
                'EmailAddress': shipper['email']
            },
            'Address': {
                'StreetLines': shipper['street_lines'],
                'StreetLines2': shipper['street_lines2'],
                'City': shipper['city'],
                'PostalCode': shipper['postal_code'],
                'CountryCode': shipper['country']
            }
        },
        'Recipient': {
            'Contact': {
                'PersonName': recipient['name'],
                'CompanyName': recipient['company'],
                'PhoneNumber': recipient['phone'],
                'EmailAddress': recipient['email']
            },
            'Address': {
                'StreetLines': recipient['street_lines'],
                'StreetLines2': recipient['street_lines2'],
                'City': recipient['city'],
                'PostalCode': recipient['postal_code'],
                'CountryCode': recipient['country']
            }
        }
    })

    street_lines3 = shipper.get('street_lines3')
    if street_lines3:
        ship['Shipper']['Address']['StreetLines3'] = street_lines3

    street_lines3 = recipient.get('street_lines3')
    if street_lines3:
        ship['Recipient']['Address']['StreetLines3'] = street_lines3

    if upper_case:
        # Shipment request address fields must be upper case (A v1.3)
        ship['Shipper']['Address'] = upper_values(ship['Shipper']['Address'])
        ship['Recipient']['Address'] = upper_values(ship['Recipient']['Address'])

    return ship


def rate(shipment):
    # shipment date cannot be in the past or more than 10 days in future
    today = datetime.today()
    if shipment['ship_timestamp'] < today or shipment['ship_timestamp'] > today + timedelta(days=10):
        return {'error': 400,
                'message': f"shipment date cannot be in the past or more than 10 days in future [{shipment['ship_timestamp']}]"}

    packages = []
    for number, package in enumerate(shipment['packages']):
        packages.append({
            '@number': str(number + 1),
            'Weight': {'Value': package['weight']},
            'Dimensions': {'Length': package['length'], 'Width': package['width'], 'Height': package['height']}
        })

    if len(packages) is 1:
        packages = packages.pop()

    # prepare ship
    shipper, recipient = shipment['sender'], shipment['recipient']
    ship = _dict({
        'Shipper': {
            'City': shipper['city'],
            'PostalCode': shipper['postal_code'],
            'CountryCode': shipper['country']
        },
        'Recipient': {
            'City': recipient['city'],
            'PostalCode': recipient['postal_code'],
            'CountryCode': recipient['country']
        }
    })

    rate_request = _dict({
        'RateRequest': {
            'ClientDetails': None,
            'RequestedShipment': {
                'DropOffType': shipment['drop_off'],
                'ShipTimestamp': date_to_str(shipment['ship_timestamp']),
                'UnitOfMeasurement': shipment['unit'],
                'Content': shipment['content'],
                'DeclaredValue': shipment['declared_value'],
                'DeclaredValueCurrencyCode': shipment['currency'],
                'PaymentInfo': shipment['payment'],
                'NextBusinessDay': 'Y',
                'Account': CONFIG['account'],
                'Ship': ship,
                'Packages': {'RequestedPackages': packages},
            }
        }
    })

    # prepare special services if any
    services = []
    for s in shipment['services']:
        services.append({'Service': {
            'ServiceType': 'II',
            'ServiceValue': s['value'],
            'CurrencyCode': s['currency']
        }})

    if services:
        rate_request['RateRequest']['RequestedShipment'].update({'SpecialServices': services})

    response = post(_get_endpoint('RateRequest'), rate_request)
    if response.ok:
        rate_response = response.json()['RateResponse']['Provider'][0]
        # get best service rate
        best_service = rate_response['Service'][0]
        for service in rate_response['Service']:
            total_net = service['TotalNet']
            if total_net['Currency'] and 0 < total_net['Amount'] < best_service['TotalNet']['Amount']:
                best_service = service

        shipment['rate'] = best_service
        return rate_response

    return {'error': response.code, 'message': response.error_type}


def shipment(shipment):
    # prepare requested packages
    packages, d_packages = _prepare_requested_packages(shipment)

    shipment_request = _dict({
        'ShipmentRequest': {
            'RequestedShipment': {
                'ShipmentInfo': {
                    'DropOffType': shipment['drop_off'],
                    'ServiceType': shipment['type'],
                    'Account': CONFIG['account'],
                    'Currency': shipment['currency'],
                    'UnitOfMeasurement': shipment['unit']
                },
                'ShipTimestamp': date_to_str(shipment['ship_timestamp']),
                'PaymentInfo': shipment['payment'],
                'InternationalDetail': {
                    'Commodities': {
                        'Description': shipment['description']
                    },
                    'Content': shipment['content']
                },
                'Ship': _ship(shipment, upper_case=True),
                'Packages': {
                    'RequestedPackages': packages
                }
            }
        }
    })

    if shipment['customs']:
        shipment_request['ShipmentRequest']['RequestedShipment']['InternationalDetail']['Commodities'][
            'CustomsValue'] = shipment['customs']

    response = post(_get_endpoint('ShipmentRequest'), shipment_request)
    if response.ok:
        shipment_response = response.json()['ShipmentResponse']
        label = shipment_response['LabelImage'][0]
        shipment['id'] = shipment_response['ShipmentIdentificationNumber']
        _label, _label_format = label['GraphicImage'], label['LabelImageFormat']
        if hasattr(shipment, 'set_label'):
            shipment.set_label(_label, _label_format)
        else:
            shipment['label'] = (_label, _label_format)
        packages_response = shipment_response['PackagesResult']['PackageResult']
        # search for shipment packages in response in order to update them
        for r_package in packages_response:
            for s_package in packages:
                if r_package['@number'] == s_package['@number']:
                    # modify package
                    d_packages[s_package['@number']]['tracking_number'] = r_package['TrackingNumber']

        return shipment_response

    return {'error': response.code, 'message': response.error_type}


def tracking(waybill=None, level=TRACKING_ALL):
    from random import choice, randint
    from string import ascii_letters, digits

    message_reference = ''.join(choice(ascii_letters + digits) for _ in range(randint(28, 32)))
    if not waybill:
        # testing purposes
        waybill = choice([
            3898464710, 9296347550, 9296392420, 3567549160, 8423914660, 7195064870,
            7895183380, 1191166550, 7780184230, 5220325810, 7895111000, 7898385320,
            5138809620, 6424045110, 6768764450, 3314358460, 9545331390, 7895083910,
            8260591010, 4688745390, 7967566180])

    tracking_request = _dict({'trackShipmentRequest': {
        'trackingRequest': {
            'TrackingRequest': {
                'Request': {
                    'ServiceHeader': {
                        'MessageTime': date_to_str(datetime.now(), format=DATETIME_FORMAT_Z),
                        'MessageReference': message_reference
                    }
                },
                'AWBNumber': {'ArrayOfAWBNumberItem': waybill},
                'LevelOfDetails': level,
                'PiecesEnabled': 'B'
            }
        }
    }
    })

    response = post(_get_endpoint('TrackingRequest'), tracking_request)
    if response.ok:
        tracking_response = response.json()['trackShipmentRequestResponse']['trackingResponse']['TrackingResponse']
        return tracking_response

    return {'error': response.code, 'message': response.error_type}


def update(shipment):
    # prepare requested packages
    packages = []
    d_packages = {}
    for number, package in enumerate(shipment.packages):
        str_number = str(number + 1)
        packages.append({
            '@number': str_number,
            'Weight': package['weight'],
            'Dimensions': {'Length': package['length'], 'Width': packages['width'], 'Height': packages['height']},
        })

        d_packages[str_number] = package

    updated_shipment = _dict({
        'UpdateRequest': {
            'MessageId': "Sample_Message_Id",
            'UpdatedShipment': {
                'ShipmentInfo': {
                    'ServiceType': shipment['type'],
                    'Account': CONFIG['account'],
                    'ShipmentIdentificationNumber': shipment['id'],
                    'LabelType': 'PDF',
                    'LabelTemplate': 'ECOM_TC_A4',
                    'ArchiveLabelTemplate': 'ARCH_8x4',
                    'IncludePreviousPieceLabels': 'Y'
                },
                'OriginalShipDate': shipment.date_str(DATETIME_FORMAT),
                'Packages': {'RequestedPackages': packages}
            }
        }
    })

    response = post(_get_endpoint('UpdateRequest'), updated_shipment)
    if response.ok:
        update_response = response.json()['UpdateShipmentResponse']
        label = update_response['LabelImage'][0]
        shipment['id'] = update_response['ShipmentIdentificationNumber']
        shipment.set_label(label['GraphicImage'], label['LabelImageFormat'])
        packages_response = update_response['PackagesResult']['PackageResult']
        # search for shipment packages in response in order to update them
        for r_package in packages_response:
            for s_package in packages:
                if r_package['@number'] == s_package['@number']:
                    # modify package
                    d_packages[s_package['@number']].set_tracking_number(r_package['TrackingNumber'])

        return update_response

    return {'error': response.code, 'message': response.error_type}


def pickup(shipment):
    packages, d_packages = _prepare_requested_packages(shipment)

    pickup_request = _dict({
        "PickUpRequest": {
            "PickUpShipment": {
                "ShipmentInfo": {
                    "ServiceType": shipment['type'],
                    "Billing": {
                        "ShipperAccountNumber": CONFIG['account'],
                        "ShippingPaymentType": shipment['shipping_payment']
                    },
                    "UnitOfMeasurement": shipment['unit'],
                },
                "PickupTimestamp": date_to_str(shipment['pickup_timestamp']),
                "PickupLocationCloseTime": date_to_str(shipment['pickup_around'], HOUR_MIN_FORMAT),
                "SpecialPickupInstruction": shipment['pickup_instructions'],
                "PickupLocation": shipment['pickup_location'],
                "InternationalDetail": {
                    "Commodities": {
                        'Description': shipment['description']
                    }
                },
                "Ship": _ship(shipment),
                "Packages": {
                    "RequestedPackages": packages
                }
            }
        }
    })

    response = post(_get_endpoint('PickupRequest'), pickup_request)
    if response.ok:
        shipment['pickup_requested'] = True
        return response.json()['PickUpResponse']

    return {'error': response.code, 'message': response.error_type}
