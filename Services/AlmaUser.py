# -*- coding: utf-8 -*-
import os
# external imports
import json
import logging
import xml.etree.ElementTree as ET
from math import *
import re
from Services import Alma_api_fonctions



class Lecteur(object):
    """"
    """

    def __init__(self, apikey='', service='', user_id= '') :
        if apikey is None:
            raise Exception("Merci de fournir une clef d'APi")
        self.apikey = apikey
        self.service = service
        self.est_erreur = False
        self.id = user_id
        self.logger = logging.getLogger(service)
        self.appel_api = Alma_api_fonctions.Alma_API(apikey=self.apikey,service=self.service)
        status,response = self.appel_api.request('GET', 
                                  
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/users/{}?user_id_type=all_unique&view=full'.format(self.id),
                                        accept='json')
        self.lecteur = self.appel_api.extract_content(response)
        if status == 'Error':
            self.est_erreur = True
            self.error_message = response


        

    def bloque_lecteur(self, bib="") :
        ''' Créer un blocge lecteur de type Retard > 35 j
        '''
        bloquage = {
            "block_type": {
                "value": "LOAN",
                "desc": "Loan"
            },
            "block_description": {
                "value": "RETARD",
                "desc": "Retard > 35 jours"
            },
            "block_status": "ACTIVE",
            "block_note": "",
            "segment_type": "Internal"
            }
        bloquage["block_note"] = "Retard sur document emprunté à {}".format(bib)
        self.lecteur["user_block"].append(bloquage)
        status,response = self.appel_api.request('PUT', 
                                  
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/users/{}?user_id_type=all_unique&view=full'.format(self.id),
                                        accept='json', content_type='json', data=json.dumps(self.lecteur))
        if status == 'Error':
            self.est_erreur = True
            self.error_message = response

    def supprime_blocage_contentieux(self):
        types_blocages_contentieux = ["CONTACT1","CONTACT2","CONTACT3","RETARD"]
        liste_blocages = self.lecteur["user_block"]
        self.logger.debug(self.id)
        self.logger.debug(json.dumps(liste_blocages,indent=4))
        # On parcourt la liste des blocages
        liste_blocages_filtree = [blocage for blocage in liste_blocages if blocage["block_description"]["value"] not in ["CONTACT1","CONTACT2","CONTACT3","RETARD"]]
        self.logger.debug(json.dumps(liste_blocages_filtree,indent=4))
        self.lecteur["user_block"] = liste_blocages_filtree
        status,response = self.appel_api.request('PUT', 
                                  
                                       'https://api-eu.hosted.exlibrisgroup.com/almaws/v1/users/{}?user_id_type=all_unique&view=full'.format(self.id),
                                        accept='json', content_type='json', data=json.dumps(self.lecteur))
        if status == 'Error':
            self.est_erreur = True
            self.error_message = response


