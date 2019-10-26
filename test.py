import pygatt
import time
from struct import *
#from bluetooth.ble import DiscoveryService

# 0x00  
# 0x01 - set interval
# 0x02, 0x03, 0x04, 0x05 - interval value

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
    xytemp_bytes = device.char_read('00000001-0000-1000-8000-00805f9b34fb')
    battery_bytes = device.char_read('00000003-0000-1000-8000-00805f9b34fb')

    device.char_write('00000002-0000-1000-8000-00805f9b34fb', [0x00]) # LED off
    time.sleep(2)
    device.char_write('00000002-0000-1000-8000-00805f9b34fb', [0x02]) # LED on

                                                              #0x01 is command byte (sleep), next 4 are bytes for value
    device.char_write('00000002-0000-1000-8000-00805f9b34fb', [0x01, 0x00, 0x00, 0x00, 0x0A]) # sleep interval
    
    # x,y, temp
    xytemp = unpack('ffB', xytemp_bytes)
    battery = unpack('B', battery_bytes)
    
    print(xytemp)
    print(battery)
    
    device.bond()
    #device.subscribe('00000001-0000-1000-8000-00805f9b34fb',
    #                     callback=data_handler_cb,
    #                    indication=True)
   #print(value)
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
