# -*- coding: utf-8 -*-
import os
# external imports
import json
import logging
import xml.etree.ElementTree as ET
from math import *
import re
from Services import Alma_api_fonctions



class AlmaReport(object):
    """A set of function for interact with Alma Apis in area "Analytics"
    """

    def __init__(self, apikey='', service='') :
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.error_status = False
        self.logger = logging.getLogger(service)
        self.appel_api = Alma_api_fonctions.Alma_API(apikey=self.apikey,service=self.service)
        self.users_list = {'33PUDB_UB':[],
                          '33PUDB_UBM':[],
                          '33PUDB_IEP':[],
                          '33PUDB_BXSA':[],
                          '33PUDB_INP':[],}
        
    def row_to_dict(self,rows):
        ns = {'ns': 'urn:schemas-microsoft-com:xml-analysis:rowset'}
        for row in rows.findall('.//ns:Row', ns):
            institution = row.find('ns:Column0', ns).text
            data = {
                'Institution': institution,
                'User_id': row.find('ns:Column1', ns).text,
                'BID': row.find('ns:Column2', ns).text,
                'BIB': row.find('ns:Column3', ns).text
            }
            self.users_list[institution].append(data)

    def get_user_list_by_token(self, token='', accept='xml'):
        status,response = self.appel_api.request('GET', 
                                
                                    'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/analytics/reports?token={}'.format(token),
                                    accept=accept)
        response = self.appel_api.extract_content(response)
        if status == 'Error':
            self.error_status = True
            return (self.error_status, response)
        root = ET.fromstring(response)
        self.row_to_dict(root)
        return root.find('.//IsFinished').text


    def get_user_list(self, path='',limit='100',accept='xml'):
        status,response = self.appel_api.request('GET', 
                                
                                    'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/analytics/reports?path={}&limit={}&col_names=true'.format(path,limit),
                                    accept=accept)
        response = self.appel_api.extract_content(response)
        if status == 'Error':
            self.error_status = True
            return (self.error_status, response)
        root = ET.fromstring(response)
        self.row_to_dict(root)
        est_fini = root.find('.//IsFinished').text
        while est_fini == 'false':
            token = root.find('.//ResumptionToken').text
            est_fini = self.get_user_list_by_token(token)
        return self.error_status, self.users_list

    