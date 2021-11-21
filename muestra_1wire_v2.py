#!/usr/bin/python
# -*- coding: utf-8 -*-


import time

import os
import paho.mqtt.publish as publish

import configparser

import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
        level=logging.INFO,
        handlers=[RotatingFileHandler('./logs/log_temperatures.log', maxBytes=1000000, backupCount=10)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')


devices_dir = '/sys/bus/w1/devices'

contenido = os.listdir(devices_dir)

sondas = []

for fichero in contenido:
    if os.path.islink(os.path.join(devices_dir, fichero)) and fichero.startswith('28-'):
       # sondas.append(os.path.join(devices_dir, fichero))
       sondas.append(os.path.join(os.path.join(devices_dir, fichero),'w1_slave'))
logging.info(contenido)
logging.info(sondas)

# Parseo de variables del .ini
parser = configparser.ConfigParser()
parser.read('config_temperatures.ini')

# Parseo de las variables de emonCMS
listener_name = parser.get('talker','name')
mqtt_ip = parser.get('talker','mqtt_ip')
publish_time = parser.get('talker','publish_time')



while 1:   
    for sonda in sondas:
        result = 'ok'
        try:
            sonda_name = sonda.split("/")[5]
            sonda_name = sonda_name[9:15]
            
            sonda_file = open(sonda,'r')
            sonda_text = sonda_file.read()
            sonda_file.close()
            
            sonda_temper = sonda_text.split("\n")[1].split(" ")[9]
            sonda_temper = float(sonda_temper[2:])
            sonda_temper = sonda_temper/1000
            sonda_temper = round(sonda_temper,1)
            
        except:
            result="time_out"
            logging.info("time_out sonda reading")
            
        if result == 'ok':
            logging.info(sonda_name + ": " + str(sonda_temper))
            publish.single("t_sensor/" + sonda_name, sonda_temper, hostname= mqtt_ip)
        
        time.sleep(int(publish_time))

    
    
    
    

