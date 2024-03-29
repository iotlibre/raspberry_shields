#!/usr/bin/env python
import sys

from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

import paho.mqtt.publish as publish

import configparser

import time
import sched, threading

import logging
from logging.handlers import RotatingFileHandler

# Para obtener mas detalle: level=logging.DEBUG
# Para comprobar el funcionamiento: level=logging.INFO
logging.basicConfig(
        level=logging.INFO,
        handlers=[RotatingFileHandler('./logs/log_modbus_tcp.log', maxBytes=10000000, backupCount=4)],
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')

#################################
# Parseo de variables del .ini
# Este fichero debe estar en el mimo directorio
#################################

parser = configparser.ConfigParser()
parser.read('config_modbus_tcp.ini')

# devuelve una list con todas las secciones
sections = parser.sections()

# Lista para incluir los servidores
servers_list=[]
# Lista para incluir los registros
registers_list=[]
# Lista de registros ordenados por sservidor
# [[aa,ab,ac],[ba,bb,bc],[ca,cb,cc],[da,db,dc]]
server_register_list=[]


# Listas separadas de servidores y registros
for section in sections:
    if parser.has_option(section,'port'):
        servers_list.append(section)
    if parser.has_option(section,'server'):
        registers_list.append(section)


# lista de servidores y registros de cada servidor
# Para el uso de ini para la lectura de registros
for server in servers_list:
    registers_temp_list=[]
    for register in registers_list:
        if server == parser.get(register,'server'):
            registers_temp_list.append(register)
    server_register_list.append(registers_temp_list)
logging.info("*" * 4 + ' Servidores')
logging.info(servers_list)
logging.info("*" * 4 + ' Registros agrupados por servidor')
logging.info(server_register_list)



###########################################
# definicion de funciones
###########################################


def mqtt_tx(m_server, s_register, s_value):
    logging.info(m_server + "  " + s_register + "  " + s_value)
    mqtt_site = parser.get('mqtt_broker','site')
    mqtt_ip = parser.get('mqtt_broker','mqtt_ip')
    mqtt_username = parser.get('mqtt_broker','login')
    mqtt_password = parser.get('mqtt_broker','password')
    mqtt_auth = { 'username': mqtt_username, 'password': mqtt_password }
    publish.single(mqtt_site + "/" + m_server + "/" + s_register, s_value, hostname=mqtt_ip, auth=mqtt_auth)  


# FUNCION: preguntar holding valor por MODBUS
def read_holding_value(tx_server_, tx_register_):
    time.sleep(0.2)
    tx_start = int(parser.get(tx_register_,'start'))
    tx_count = int(parser.get(tx_register_,'registers'))
    tx_slave = int(parser.get(tx_server_,'slave'))
    st_byteorder = parser.get(tx_server_,'byteorder')
    exec("global tx_byteorder\ntx_byteorder = %s" % (st_byteorder))
    st_wordorder = parser.get(tx_server_,'wordorder')
    exec("global tx_wordorder\ntx_wordorder = %s" % (st_wordorder))

    register_red = True
    value = 33.33

    try:
        res1 = cli.read_holding_registers(tx_start, count=tx_count, slave=tx_slave)
        logging.debug('tx_byteorder: '+ tx_byteorder)
        logging.debug('tx_wordorder: '+ tx_wordorder)
        decoder = BinaryPayloadDecoder.fromRegisters(res1.registers,
                                                     byteorder= tx_byteorder,
                                                     wordorder= tx_wordorder)

        st_tipe = "decoder.decode_" + parser.get(tx_register_,'tipe') + "()"
        # logging.debug("global decoded\ndecoded = %s" % (st_tipe))
        exec("global decoded\ndecoded = %s" % (st_tipe))

        value = "%.2f" % decoded

        logging.debug('st_tipe: '+ st_tipe)
        logging.debug("registros:" + str(res1.registers))

    except:
        # print("Error:", sys.exc_info()[0])
        logging.warning("Error al leer el registro: " + tx_register_)
        register_red = False

    if register_red == True:
        logging.debug("mqtt_tx(): " + tx_server_ + " " + tx_register_ +" " + value)
        mqtt_tx(tx_server_ , tx_register_, value)


# FUNCION: Recorremos los registros del fichero .ini
def matrix_reading(tm):
    threading.Timer(tm, matrix_reading,args=[tm]).start()

    logging.debug("*" * 4 + ' Recorremos servidores y sus registros')

    for s in range(len(servers_list)):
        tx_server = servers_list[s]
              
        tx_url = parser.get(tx_server,'url')
        tx_port = parser.get(tx_server,'port')

        logging.debug('------ ' + tx_url)
        logging.debug('------ ' + tx_port)        

        global cli

        # cli = ModbusClient(method=c_method, port=c_port, timeout=1, baudrate=c_baudrate)
        cli = ModbusClient(tx_url, port=tx_port)
        connexion = True
        

      
        try:
            # sin el assert el fallo en la conexión no se toma como error
            assert cli.connect()
        except:
            connexion = False
            logging.warning("Error al establecer la conexión MODBUS tcp")

        if connexion == True:
            for r in range(len(server_register_list[s])):
                tx_register = server_register_list[s][r]
                read_holding_value(tx_server, tx_register)
            cli.close()

###########################################
# Ejecución temporal de las funciones
###########################################

query_time = float(parser.get('mqtt_broker','query_time'))
matrix_reading(query_time)


