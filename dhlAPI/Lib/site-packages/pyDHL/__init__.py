from functools import wraps
from . import requests

UNITS_METRIC = 'SI'
UNITS_IMPERIAL = 'SU'

CUSTOMS_PAYMENTS_CLIENT = 'DDU'
CUSTOMS_PAYMENTS_CUSTOMER = 'DAP'
CUSTOMS_PAYMENTS = 'DDP'

SERVICE_TYPE_EU = 'U'
SERVICE_TYPE_WORLD = 'P'
SERVICE_TYPE_WORLD_DOCUMENTS = 'D'
SERVICE_TYPE_DOMESTIC = 'N'

PAYMENT_SHIPPER = 'S'
PAYMENT_RECEIVER = 'R'
PAYMENT_BILLING = 'T'

DROP_OFF_REGULAR = 'REGULAR_PICKUP'
DROP_OFF_COURIER = 'REQUEST_COURIER'

CURRENCY_EUR = 'EUR'
CURRENCY_USD = 'USD'

CONTENT_DOCUMENTS = 'DOCUMENTS'
CONTENT_NON_DOCUMENTS = 'NON_DOCUMENTS'

EU_CODES = ['AT', 'BE', 'BG', 'DE', 'CY', 'CZ', 'DK', 'EE', 'ES', 'FI', 'FR', 'GB', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT',
            'LU', 'LV', 'MC', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK']

WORLD_CODES = EU_CODES + ['AD', 'AE', 'AF', 'AG', 'AI', 'AL', 'AM', 'AO', 'AR', 'AT', 'AU', 'AW', 'AZ',
                          'BA', 'BB', 'BD', 'BE', 'BF', 'BH', 'BI', 'BJ', 'BM', 'BN', 'BO', 'BR', 'BS', 'BT', 'BW',
                          'BY', 'BZ', 'CA', 'CD', 'CF', 'CG', 'CH', 'CI', 'CK', 'CL', 'CM', 'CN', 'CO', 'CR', 'CU',
                          'DJ', 'DM', 'DO', 'DZ', 'EC', 'EG', 'ER', 'ET', 'FJ', 'FK', 'FO', 'GA', 'GD', 'GE', 'GG',
                          'GH', 'GI', 'GL', 'GM', 'GN', 'GP', 'GQ', 'GT', 'GW', 'GY', 'HK', 'HN', 'HT', 'ID', 'IL',
                          'IN', 'IQ', 'IR', 'IS', 'JE', 'JM', 'JO', 'JP', 'KG', 'KI', 'KM', 'KN', 'KP', 'KR', 'KV',
                          'KW', 'KY', 'KZ', 'LA', 'LB', 'LC', 'LI', 'LK', 'LR', 'LS', 'LV', 'LY', 'MA', 'MD', 'ME',
                          'MG', 'MK', 'ML', 'MM', 'MN', 'MO', 'MQ', 'MR', 'MS', 'MU', 'MV', 'MW', 'MX', 'MY', 'MZ',
                          'NA', 'NC', 'NE', 'NG', 'NI', 'NO', 'NP', 'NR', 'NU', 'NZ', 'OM', 'PA', 'PE', 'PF', 'PG',
                          'PH', 'PK', 'PY', 'QA', 'RE', 'RS', 'RU', 'RW', 'SA', 'SB', 'SC', 'SD', 'SG', 'SH', 'SL',
                          'SM', 'SN', 'SO', 'SR', 'SS', 'ST', 'SV', 'SY', 'SZ', 'TC', 'TD', 'TG', 'TH', 'TJ', 'TL',
                          'TN', 'TO', 'TR', 'TT', 'TV', 'TW', 'TZ', 'UA', 'UG', 'US', 'UY', 'UZ', 'VA', 'VC', 'VE',
                          'VG', 'VN', 'VU', 'WS', 'XB', 'XC', 'XE', 'XM', 'XN', 'XS', 'XY', 'YE', 'YT', 'ZA', 'ZM',
                          'ZW']

LABEL_DIR = 'labels/'

INVALID_CHARACTERS = (':', '&', '>', '<')
STR_MAX_LENGTH = 35


def validate_characters(func):
    @wraps(func)
    def wrapper_validate(f_name, *args, **kwargs):
        for value in list(args) + list(kwargs.values()):
            if value and any(char in str(value) for char in INVALID_CHARACTERS):
                raise AttributeError(f'ERROR: invalid characters ({INVALID_CHARACTERS}) in {value}')
        return func(f_name, *args, **kwargs)
    return wrapper_validate


def validate_country(country, codes=WORLD_CODES):
    if country not in codes:
        raise AttributeError(f'ERROR: country code in {country} is invalid, please enter a valid code')
    return country


def validate_length(input, length=STR_MAX_LENGTH):
    if input and len(input) > length:
        raise AttributeError(f'ERROR: max length is {length}, {input} was {len(input)}')
    return input


def validate_pickup(timestamp, pickup_around=None):
    if pickup_around and pickup_around < timestamp:
        raise ValueError(f'The Pickup Location Close Time ({pickup_around}) cannot be earlier than Pickup Time.')
    return timestamp, pickup_around


class _ContainerInterface:
    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __contains__(self, item):
        return hasattr(self, item)

    def get(self, item, default=None):
        if item in self and self[item]:
            return self[item]
        return default

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.__dict__}>'


class Package(_ContainerInterface):
    def __init__(self, width, length, height, weight, price=None, description=None, reference=None):
        self.width = width
        self.length = length
        self.height = height
        self.weight = weight
        self.price = price or 0.0
        self.description = description
        self.tracking_number = None
        self.reference = reference


class Address(_ContainerInterface):
    @validate_characters
    def __init__(self, street_lines, city, postal_code, country, **kwargs):
        self.street_lines = validate_length(street_lines)
        self.city = city
        self.postal_code = postal_code
        self.country = validate_country(country)
        self.street_lines2 = kwargs.get('street_lines2', 'N/A')
        self.street_lines3 = kwargs.get('street_lines3')


class Contact(_ContainerInterface):
    @validate_characters
    def __init__(self, name, phone, email=None, company=None):
        self.name = name
        self.phone = phone
        self.email = email or "null"
        self.company = company or name


class Person(Contact, Address):
    def __init__(self, **kwargs):
        Contact.__init__(self, kwargs.get('name'), kwargs.get('phone'), kwargs.get('email'), kwargs.get('company'))
        Address.__init__(self, **kwargs)


class Shipment(_ContainerInterface):
    def __init__(self, packages, sender, recipient, **kwargs):
        self.pickup_timestamp, self.pickup_around = validate_pickup(kwargs.get('pickup_timestamp'),
                                                                    kwargs.get('around'))
        self.description = validate_length(kwargs.get('description'))

        self.sender = sender
        self.recipient = recipient
        self.packages = packages
        self.content = kwargs.get('content', CONTENT_NON_DOCUMENTS)
        self.currency = kwargs.get('currency', CURRENCY_EUR)
        self.customs = kwargs.get('customs')
        self.declared_value = kwargs.get('value')
        self.deleted = False
        self.drop_off = kwargs.get('drop_off', DROP_OFF_REGULAR)
        self.id = None
        self.label = None
        self.payment = kwargs.get('payment', CUSTOMS_PAYMENTS)
        self.pickup_location = kwargs.get('location')
        self.pickup_instructions = kwargs.get('instructions')
        self.pickup_requested = False
        self.rate = None
        self.services = kwargs.get('services', [])
        self.shipping_payment = kwargs.get('shipping_payment', PAYMENT_SHIPPER)
        self.ship_timestamp = kwargs.get('ship_timestamp')
        self.type = kwargs.get('service', SERVICE_TYPE_WORLD)
        self.unit = kwargs.get('units', UNITS_METRIC)

        if self.sender.country == self.recipient.country:
            self.type = SERVICE_TYPE_DOMESTIC
        elif self.sender.country in EU_CODES and self.recipient.country in EU_CODES:
            self.type = SERVICE_TYPE_EU
        elif self.content != CONTENT_NON_DOCUMENTS:
            self.type = SERVICE_TYPE_WORLD_DOCUMENTS

        if self.type in [SERVICE_TYPE_DOMESTIC, SERVICE_TYPE_EU]:
            self.content = CONTENT_DOCUMENTS

    def set_customs(self, customs_values):
        self.customs = customs_values

    def set_pickup(self, timestamp, **kwargs):
        self.pickup_timestamp, self.pickup_around = validate_pickup(timestamp, kwargs.get('around'))
        self.pickup_location = kwargs.get('location')
        self.pickup_instructions = kwargs.get('instructions')

    def set_label(self, graphic_img, format='pdf'):
        from os import path, makedirs
        from base64 import decodebytes

        if not path.exists(LABEL_DIR):
            makedirs(LABEL_DIR)

        label_path = LABEL_DIR + str(self.id) + '.' + format.lower()
        with open(label_path, 'wb') as pdf:
            pdf.write(decodebytes(str.encode(graphic_img)))

        self.label = label_path
        return self.label

    def add_service(self, value, currency=CURRENCY_EUR):
        self.services.append({'value': value, 'currency': currency})
