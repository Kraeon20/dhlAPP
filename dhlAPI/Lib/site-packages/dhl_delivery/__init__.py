import dhl_delivery.quote
import dhl_delivery.pickup
import dhl_delivery.shipment

dhl_site_id = ''
dhl_site_password = ''
dhl_account_no = ''

dhl_response_flag = False
dhl_xml_flag = False
dhl_delivery_label_path = ''

dhl_delivery.dhl_site_id = dhl_site_id
dhl_delivery.dhl_site_password = dhl_site_password
dhl_delivery.dhl_account_no = dhl_account_no

dhl_delivery.dhl_delivery_label_path = dhl_delivery_label_path
dhl_delivery.dhl_xml_flag = dhl_xml_flag
dhl_delivery.dhl_response_flag = dhl_xml_flag
dhl_delivery.max_response_time = 60

# for delivery
dhl_delivery.delivery_payment_type = 'S'  # S -  always paid by shipper
dhl_delivery.duty_payment_type = 'R'  # duty always will be paid by Reciver

quote = dhl_delivery.quote.Quote()
pickup = dhl_delivery.pickup.Pickup()
shipment = dhl_delivery.shipment.Shipment()
