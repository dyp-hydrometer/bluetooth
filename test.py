import pygatt
import time
from struct import *
#from bluetooth.ble import DiscoveryService

ada = pygatt.GATTToolBackend()
ADDRESS_TYPE = pygatt.BLEAddressType.random

def data_handler_cb(handle, value):
    """
        Indication and notification come asynchronously, we use this function to
        handle them either one at the time as they come.
    :param handle:
    :param value:
    :return:
    """
    print("Data: {}".format(value.hex()))
    print("Handle: {}".format(handle))

try:
    ada.start()
    device = ada.connect('F6:8D:14:D4:8D:10', address_type=ADDRESS_TYPE) 
    
    characteristics = device.discover_characteristics(100)

    '''for c in characteristics:
        val = device.char_read(c)
        print(c)
        if len(val) == 8:
            to_print = unpack('ff', val)
            print(f"    {to_print}")
       # print(c)
    '''
    value = device.char_read('00000001-0000-1000-8000-00805f9b34fb')
    print(len(value))
    # x,y 
    to_floats = unpack('ff', value)
    print(to_floats)
    device.bond()
    #device.subscribe('00000001-0000-1000-8000-00805f9b34fb',
    #                     callback=data_handler_cb,
    #                    indication=True)
    print(value)
   # val = unpack('f', value)
   # print(val)
finally:
    #time.sleep()
    ada.stop()
'''

service = DiscoveryService()
devices = service.discover(2)

for addr, name in devices.items():
    print(f"{addr} - {name}")
'''
