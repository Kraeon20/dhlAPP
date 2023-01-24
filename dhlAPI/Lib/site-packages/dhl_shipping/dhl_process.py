import time
from datetime import datetime
import multiprocessing

import dhl_shipping
import dhl_shipping.config
import urllib2

class DhlProcess:
    def __init__(self):
        pass

    @staticmethod
    def check_utilities(n, return_dict):
        return_dict['return_check_utilities'] = True

    @staticmethod
    def stop_process(p, start_time, time_to_stop_in_second):
        start_this = time.time()
        while time.time() < start_this + time_to_stop_in_second:
            time_end_this = datetime.now()
            delta = time_end_this - start_time
            time_interval_in_second = delta.total_seconds()

            if time_interval_in_second >= time_to_stop_in_second:
                try:
                    p.terminate()
                except:
                    pass
    
    def process_quote(self, xml_formated_data_string):
        time_now = datetime.now()

        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        p_one = multiprocessing.Process(target=self.check_utilities, name="name_check_utilities", args=(20, return_dict))
        jobs.append(p_one)
        p_two = multiprocessing.Process(target=self.call_dhl_quote_api, name="name_call_dhl_quote_api", args=(xml_formated_data_string, return_dict))
        jobs.append(p_two)
        p_stop = multiprocessing.Process(target=self.stop_process, name="name_stop_process", args=(p_two, time_now, dhl_shipping.max_response_time))

        # Start the jobs
        p_one.start()
        p_two.start()
        p_stop.start()

        for job in jobs:
            job.join()

        return return_dict

    @staticmethod
    def call_dhl_quote_api(xml_formated_data_string, return_dict):
        url = dhl_shipping.config.dhl_api_url
        url_request = urllib2.Request(url, xml_formated_data_string)
        url_response = urllib2.urlopen(url_request)
        url_response_data = url_response.read()  # getting as XML String from DHL Response
        return_dict['return_dhl_api_response'] = url_response_data

    def process_shipment(self, xml_formated_data_string):
        time_now = datetime.now()

        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        p_one = multiprocessing.Process(target=self.check_utilities, name="name_check_utilities", args=(20, return_dict))
        jobs.append(p_one)
        p_two = multiprocessing.Process(target=self.call_dhl_shipment_api, name="name_call_dhl_shipment_api", args=(xml_formated_data_string, return_dict))
        jobs.append(p_two)
        p_stop = multiprocessing.Process(target=self.stop_process, name="name_stop_process", args=(p_two, time_now, dhl_shipping.max_response_time))

        # Start the jobs
        p_one.start()
        p_two.start()
        p_stop.start()

        for job in jobs:
            job.join()

        return return_dict

    @staticmethod
    def call_dhl_shipment_api(xml_formated_data_string, return_dict):
        url = dhl_shipping.config.dhl_api_url
        url_request = urllib2.Request(url, xml_formated_data_string)
        url_response = urllib2.urlopen(url_request)
        url_response_data = url_response.read()  # getting as XML String from DHL Response
        return_dict['return_dhl_api_response'] = url_response_data


    def process_pickup(self, xml_formated_data_string):
        time_now = datetime.now()

        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        jobs = []
        p_one = multiprocessing.Process(target=self.check_utilities, name="name_check_utilities", args=(20, return_dict))
        jobs.append(p_one)
        p_two = multiprocessing.Process(target=self.call_dhl_pickup_api, name="name_call_dhl_pickup_api", args=(xml_formated_data_string, return_dict))
        jobs.append(p_two)
        p_stop = multiprocessing.Process(target=self.stop_process, name="name_stop_process", args=(p_two, time_now, dhl_shipping.max_response_time))

        # Start the jobs
        p_one.start()
        p_two.start()
        p_stop.start()

        for job in jobs:
            job.join()

        return return_dict

    @staticmethod
    def call_dhl_pickup_api(xml_formated_data_string, return_dict):
        url = dhl_shipping.config.dhl_api_url
        url_request = urllib2.Request(url, xml_formated_data_string)
        url_response = urllib2.urlopen(url_request)
        url_response_data = url_response.read()  # getting as XML String from DHL Response
        return_dict['return_dhl_api_response'] = url_response_data
