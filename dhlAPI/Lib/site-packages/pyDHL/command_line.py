# -*- coding: utf-8 -*
import argparse
from pprint import pprint
from datetime import datetime
from . import Package, Shipment, Person, requests
from json import load, dumps


RATE_HELP = "The Rate request will return DHL’s product capabilities (products,\
 services and estimated delivery time) and prices (where applicable) for a \
 certain set of input data."
SHIPMENT_HELP = "The key elements in the response of the Shipment Request will \
be a base64 encoded PDF label and the Shipment and Piece identification numbers\
, which you can use for tracking on the DHL web site."
UPDATE_HELP = "The updateShipment request allows for additional pieces to be\
 added to a previously created shipment that has not been picked up by DHL\
  Express/had a scan against it."
TRACK_HELP = "The resulting response will provide tracking events at both the\
 Shipment and/or Piece events corresponding to the DHL Waybill(s) submitted."
PICKUP_HELP = "The requestPickup request allows users to request standalone\
 pickup requests for local and remote/import pickups."


def parse_file(file):
    with file as _file:
        conf_shipment = load(_file)

    credentials = {}
    for k in ['account', 'username', 'password']:
        credentials[k] = conf_shipment[k]
        del conf_shipment[k]
    requests.set_credentials(credentials)

    # create packages
    packages = []
    for p in conf_shipment['packages']:
        packages.append(Package(**p))

    sender = Person(**conf_shipment['sender'])
    recipient = Person(**conf_shipment['recipient'])

    # transform ship_timestamp to a date
    ship_timestamp = datetime.strptime(conf_shipment['ship_timestamp'], requests.DATETIME_FORMAT_GMT)

    # reuse conf_timestamp into Shipment object building
    del conf_shipment['packages']
    del conf_shipment['sender']
    del conf_shipment['recipient']
    del conf_shipment['ship_timestamp']

    return Shipment(
        sender=sender,
        recipient=recipient,
        packages=packages,
        ship_timestamp=ship_timestamp,
        **conf_shipment
    )


def main():
    parser = argparse.ArgumentParser(prog='python_dhl', description='DHL REST Webservice integration')
    parser.add_argument('-r', '--rate', help=RATE_HELP, type=argparse.FileType(encoding='UTF-8'))
    parser.add_argument('-s', '--shipment', help=SHIPMENT_HELP, type=argparse.FileType(encoding='UTF-8'))
    parser.add_argument('-u', '--update', help=UPDATE_HELP, type=argparse.FileType(encoding='UTF-8'))
    parser.add_argument('-t', '--track', help=TRACK_HELP, type=argparse.FileType(encoding='UTF-8'))
    parser.add_argument('-p', '--pickup', help=PICKUP_HELP, type=argparse.FileType(encoding='UTF-8'))
    parser.add_argument('-o', '--output', help="Output File", type=argparse.FileType('w', encoding='UTF-8'))
    parser.add_argument('-snd', '--sandbox', help="Set sandbox mode", default=False, nargs='?', type=bool)

    args = parser.parse_args()

    if args.sandbox:
        requests.set_sandbox()

    results = {}

    if args.rate:
        shipment = parse_file(args.rate)
        results = requests.rate(shipment)
    elif args.shipment:
        shipment = parse_file(args.shipment)
        results = requests.shipment(shipment)
    elif args.update:
        shipment = parse_file(args.update)
        results = requests.update(shipment)
    elif args.track:
        shipment = parse_file(args.track)
        results = requests.tracking(shipment)
    elif args.pickup:
        shipment = parse_file(args.pickup)
        results = requests.pickup(shipment)

    if results:
        if args.output:
            with args.output as output:
                output.write(dumps(results, indent=2, separators=(',', ': ')))
        else:
            pprint(results, width=100)
