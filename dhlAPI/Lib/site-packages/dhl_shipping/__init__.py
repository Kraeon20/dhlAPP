import dhl_shipping.quote
import dhl_shipping.pickup
import dhl_shipping.shipment

dhl_site_id = ''
dhl_site_password = ''
dhl_account_no = ''  

dhl_response_flag = False
dhl_xml_flag = False
dhl_shipping_label_path = ''

dhl_shipping.dhl_site_id = dhl_site_id
dhl_shipping.dhl_site_password = dhl_site_password
dhl_shipping.dhl_account_no = dhl_account_no

dhl_shipping.dhl_shipping_label_path = dhl_shipping_label_path
dhl_shipping.dhl_xml_flag = dhl_xml_flag
dhl_shipping.dhl_response_flag = dhl_xml_flag
dhl_shipping.max_response_time = 60

# for shipment
dhl_shipping.shipping_payment_type = 'S'  # S -  always paid by shipper 
dhl_shipping.duty_payment_type = 'R'  # duty always will be paid by Reciver

quote = dhl_shipping.quote.Quote()
pickup = dhl_shipping.pickup.Pickup()
shipment = dhl_shipping.shipment.Shipment()
