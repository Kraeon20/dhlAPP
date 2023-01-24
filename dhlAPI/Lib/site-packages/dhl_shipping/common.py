class Common:
    def __init__(self):
        pass

    def in_dictionary(self, field, dict_data):
        """ Search for string by key in a dictionary.
            param 1: the key as string
            param 2: the dictionary data
            returns: if found then returns the value of the key as string else returns False
        """
        found_flag = False
        eureka = ''
        if field in dict_data:
            found_flag = True
            eureka = dict_data[field]
            #return dict_data[field]
        for k, v in dict_data.items():
            if isinstance(v, dict):
                eureka = self.in_dictionary(field, v)
                if eureka is not None:
                    found_flag = True
                    #return eureka
        if found_flag == True:
            return eureka
        else:
            return False

    def in_dictionary_all(self, field, dict_data, not_found_return_str=''):
        """ Search for string by key in a dictionary.
            param 1: the key as string
            param 2: the  dictionary data
            returns: if found then returns the all occurrence-value of the key as a list else returns False or the specifed string
        """
        found_flag = False
        fields_found = []

        for key, value in dict_data.items():

            if key == field:
                found_flag = True
                fields_found.append(value)

            elif isinstance(value, dict):
                results = self.in_dictionary_all(field, value)
                if type(results) == list:
                    for result in results:
                        found_flag = True
                        fields_found.append(result)

            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        more_results = self.in_dictionary_all(field, item)
                        if type(more_results) == list:
                            for another_result in more_results:
                                found_flag = True
                                fields_found.append(another_result)

        if found_flag == True:
            return fields_found
        else:
            if not_found_return_str:
                return not_found_return_str
            else:
                return False

    def get_dhl_region_code(self, country_code):
        """
        Get region code AP|AM|EU by country code
        """
        region_code = ''
        ap_list = ['AE', 'AF', 'AL', 'AM', 'AO', 'AU', 'BA', 'BD', 'BH', 'BN', 
        'BY', 'CI', 'CM', 'CN', 'CY', 'DJ', 'DZ', 'EG', 'ET', 'FJ', 'GA', 'GH', 
        'HK', 'HR', 'ID', 'IL', 'IN', 'IR', 'JO', 'JP', 'KE', 'KR', 'KW', 'KZ', 
        'LA', 'LB', 'LK', 'MA', 'MD', 'MG', 'MK', 'MO', 'MT', 'MU', 'MY', 'NA', 
        'NG', 'NZ', 'OM', 'PH', 'PK', 'QA', 'RE', 'RS', 'RU', 'SA', 'SD', 'SG', 
        'SN', 'TH', 'TR', 'TW', 'TZ', 'UA', 'UG', 'UZ', 'VN', 'YE', 'ZA']

        eu_list = ['AT', 'BE', 'BG', 'CH', 'CZ', 'DE', 'DK', 'EE', 'ES', 
        'FI', 'FR', 'GB', 'GR', 'HU', 'IE', 'IS', 'IT', 'LT', 'LU', 'LV', 
        'NL', 'NO', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK' ]

        am_list = ['AI', 'AR', 'AW', 'BB', 'BM', 'BO', 'BR', 'BS', 'CA', 'CL', 
        'CO', 'CR', 'DM', 'DO', 'EC', 'GP', 'GT', 'GU', 'GY', 'HN', 'HT', 'JM', 
        'KN', 'KY', 'LC', 'MQ', 'MX', 'NI', 'PA', 'PE', 'PR', 'PY', 'SV', 'TC', 
        'TT', 'US', 'UY', 'VE', 'VG', 'VI', 'XM', 'XY']

        if country_code in ap_list:
            region_code = 'AP'
        elif country_code in eu_list:
            region_code = 'EU'
        elif country_code in am_list:
            region_code = 'AM'
        return region_code
