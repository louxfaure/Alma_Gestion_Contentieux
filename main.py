#!/usr/bin/python3
# -*- coding: utf-8 -*-
#Modules externes
import math
import logging
import csv
import xml.etree.ElementTree as ET
from datetime import datetime,date
from os import listdir, path, getenv, remove, mkdir
#Modules maison 
from Services import AlmaReport, logs,mail, AlmaUser

SERVICE = "Alma_Gestion_Contentieux"
REP = '/tmp/Notices_a_fusionner/'
LOGS_LEVEL = 'INFO'
LOGS_DIR = getenv('LOGS_PATH')
EXPORT_JOB_PAREMETERS_FILE = './Conf/export_job_parameters.xml'
INSTITUTIONS = ['33PUDB_UB','33PUDB_UBM','33PUDB_IEP','33PUDB_BXSA','33PUDB_INP']

today = date.today()
now = datetime.now()
group_id = 1
num_fichier = 1
liste_de_cent_groupe = []


#On initialise le logger
logs.setup_logging(name=SERVICE, level=LOGS_LEVEL,log_dir=LOGS_DIR)
log_module = logging.getLogger(SERVICE)

def rediger_envoyer_message(sujet, text):
    message = mail.Mail()
    message.envoie(mailfrom=getenv('MAILFROM'),mailto=getenv('MAILTO'),subject=sujet,text=text)


def traite_liste_lecteur(liste_lecteur=[],action='',liste_anomalie = [],liste_pour_rapport = []):

    # Blocage/Déblocage des lecteurs institutions par institution
    for institution in INSTITUTIONS :
        log_module.info("Traitement de l'institution {} : {} lecteurs à bloquer : ".format(institution, len(user_list[institution])))
        nb_lecteurs_a_traiter = len(user_list[institution])
        nb_lecteurs_traites = len(user_list[institution])
        api_key = getenv('PROD_{}_USER_API'.format(institution[7:]))
        for user in user_list[institution] :
            user_id = user['BID']
            log_module.debug(user)
            lecteur = AlmaUser.Lecteur(apikey=api_key,service=SERVICE,user_id=user_id)
            if lecteur.est_erreur :
                log_module.error(lecteur.error_message)
                nb_lecteurs_traites-=1
                liste_anomalie.append("{} - {} : Impossible d'obtenir les données du compte lecteur :{}".format(institution, user_id,lecteur.error_message))
                next
            if action=="bloquer" :
                lecteur.bloque_lecteur(bib = user["BIB"])
            else :
                lecteur.supprime_blocage_contentieux()
            if lecteur.est_erreur :
                log_module.error(lecteur.error_message)
                nb_lecteurs_traites-=1
                liste_anomalie.append("{} - {} : Impossible de {} le compte du lecteur :{}".format(institution,user_id,action,lecteur.error_message))
                next
        liste_pour_rapport.append("\t- Pour {} : {} sur {} lecteurs à {} ".format(institution,nb_lecteurs_traites,nb_lecteurs_a_traiter,action))
    return liste_pour_rapport,liste_anomalie

log_module.info("Début du traitement")
log_module.debug(today)
# Récupération de la liste des comptes à bloquer
log_module.info("Récupération de la liste des comptes à bloquer")
path="%2Fshared%2FBordeaux%20NZ%2033PUDB_NETWORK%2Fprod%2FServices%20aux%20publics%2FGestion%20des%20retards%20et%20des%20contentieux%2FPour%20Automatisation%2FLecteurs%20Retards%2035j%20a%20bloquer%20SQL"
analytics = AlmaReport.AlmaReport(service=SERVICE,apikey=getenv('PROD_NETWORK_USER_API'))
est_erreur, user_list = analytics.get_user_list(path=path,limit="1000")
if est_erreur :
    log_module.error(user_list)
    rediger_envoyer_message(sujet="Traitement des lecteurs en contentieux - {} - ERREUR : Impossible d'obtenir la liste des comptes à bloquer".format(today),text="Bonjour\nVoici le message d'erreur : {}\nMerci de contacter votre administrateur\n. Cordialement,".format(user_list))
    exit
log_module.debug(user_list)
liste_comptes_bloques, liste_anomalies = traite_liste_lecteur(liste_lecteur=user_list,action="bloquer")

#Récupération de la liste des comptes à débloquer
log_module.info("Récupération de la liste des comptes à débloquer")
#TODO Modifier l'adresse d
path="%2Fshared%2FBordeaux%20NZ%2033PUDB_NETWORK%2Fprod%2FServices%20aux%20publics%2FGestion%20des%20retards%20et%20des%20contentieux%2FPour%20Automatisation%2FLecteurs%20Retards%2035j%20a%20debloquer%20SQL"
analytics = AlmaReport.AlmaReport(service=SERVICE,apikey=getenv('PROD_NETWORK_USER_API'))
est_erreur, user_list = analytics.get_user_list(path=path,limit="1000")
if est_erreur :
    log_module.error(user_list)
    rediger_envoyer_message(sujet="Traitement des lecteurs en contentieux - {} - ERREUR : Impossible d'obtenir la liste des comptes à débloquer".format(today),text="Bonjour\nVoici le message d'erreur : {}\nMerci de contacter votre administrateur\n. Cordialement,".format(user_list))
    exit
liste_comptes_bloques, liste_anomalies = traite_liste_lecteur(liste_lecteur=user_list,action="debloquer",liste_anomalie=liste_anomalies, liste_pour_rapport=liste_comptes_bloques)
sujet = "Traitement des lecteurs en contentieux - {} - Alerte".format(today) if len(liste_anomalies)>0 else "Traitement des lecteurs en contentieux - {} - Succés".format(today)
message = "Bonjour,\n" + "\n".join(liste_comptes_bloques) + "\n"
message =  message +  "\n".join(liste_anomalies) + "\nCordialement," if len(liste_anomalies)>0 else message + "Cordialement,"
log_module.debug(message)
rediger_envoyer_message(sujet=sujet,text=message)

log_module.info("FIN DU TRAITEMENT")