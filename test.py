import pygatt
import time, math
from struct import *
import requsts
import jsonify
#from bluetooth.ble import DiscoveryService

# 0x00  
# 0x01 - set interval
# 0x02, 0x03, 0x04, 0x05 - interval value

ada = pygatt.GATTToolBackend()
ADDRESS_TYPE = pygatt.BLEAddressType.random

headers = {'Content-type': 'application/json'}

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

    # don't hardcode this address
    device = ada.connect('F6:8D:14:D4:8D:10', address_type=ADDRESS_TYPE) 

    address = device.address

    hydro_resp = requests.get(f'http://localhost:5000/api/hydrometers/{address}', headers=headers)

    if hydro_resp.status_code != 200:
        print(f"no such hydrometer {address}, adding via API")
        
        data = {}
        data["color"] = "#000000"
        data["battery"] = battery
        create_resp = requests.put(f'http://localhost:5000/api/hydrometers/', data=json.dumps(data), headers=headers)

        if create_resp.status_code != 200:
            print("Error with the add hydrometer request, terminating...")
            return
        
        hydro_resp = create_resp
        
    hydrometer = jsonify(hydro_resp.text)

    '''characteristics = device.discover_characteristics(100)

    for c in characteristics:
        val = device.char_read(c)
        print(c)
        if len(val) == 8:
            to_print = unpack('ff', val)
            print(f"    {to_print}")
       # print(c)
    '''
    xyz_bytes = device.char_read('00000001-0000-1000-8000-00805f9b34fb')
    temp_bytes = device.char_read('00000004-0000-1000-8000-00805f9b34fb')
    battery_bytes = device.char_read('00000003-0000-1000-8000-00805f9b34fb')

    #device.char_write('00000002-0000-1000-8000-00805f9b34fb', [0x00]) # LED off
    #time.sleep(2)
    #device.char_write('00000002-0000-1000-8000-00805f9b34fb', [0x02]) # LED on

    # x,y, temp
    x,y,z = unpack('fff', xyz_bytes)
    temp = unpack('B', temp_bytes)
    battery = unpack('B', battery_bytes)

    # use get
    data = {}
    data["battery"] = battery
    data["rssi"] = device.get_rssi()

    # TAKEN FROM ISPINDLE https://github.com/universam1/iSpindel/
    pitch = math.atan2(y, sqrt(x**2 + z**2))) * 180.0 / math.PI
    roll = math.atan2(x, sqrt(y**2 + z**2))) * 180.0 / math.PI
    tilt = math.sqrt(pitch**2 + roll**2)
    data["angle"] = -0.00031 * tilt**2 + 0.557 * tilt - 14.054

    resp = requests.put(f'http://localhost:5000/api/hydrometers/{hydrometer["id"]}/reading/', data=json.dumps(data), headers=headers)
    
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
