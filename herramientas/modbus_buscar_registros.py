# tool to know the active registers in the client divice

#!/usr/bin/env python

import time

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
#from pymodbus.constants import Endian
#from pymodbus.payload import BinaryPayloadDecoder

UNIT = 0x1

cli = ModbusClient(method='rtu', port='/dev/ttyUSB0', timeout=1, baudrate=9600)
assert cli.connect()

time.sleep(1)
for n in range (0,400) :
    time.sleep(0.1)
    res1 = cli.read_holding_registers(n, count=1, unit=UNIT)
    # assert not res1.isError()
    # Imprime el resultado, No los registros
    # print(str(n) + ' -> ' + str(res1))
    try:
        print(str(n) + ' -> '+  str(res1.registers))
    except:
        # print('error de registros')
        pass

for n in range (20400,20500) :
    time.sleep(0.1)
    res1 = cli.read_holding_registers(n, count=1, unit=UNIT)
    try:
        print(str(n) + ' -> '+  str(res1.registers))
    except:
        pass

