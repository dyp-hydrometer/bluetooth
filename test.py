import pygatt
import time, math
import threading
from struct import *
import requests
from flask import jsonify

# 0x00  
# 0x01 - set interval
# 0x02, 0x03, 0x04, 0x05 - interval value

class Reading:
    x = None
    y = None
    z = None
    temp = None
    battery = None
    complete = False

    #__init__():
    #    self.x = None
    #    self.y = None
    #    self.z = None
    #    self.temp = None
    #    self.battery = None

    def data_complete():
        return self.x is Not None and self.y is not None and self.z is not None
                and self.temp is not None and self.battery is not None

    def xyz_cb(handle, value):
        """
            Indication and notification come asynchronously, we use this function to
            handle them either one at the time as they come.
        :param handle:
        :param value:
        :return:
        """
        self.x, self.y, self.z = unpack('fff', value)

    def temp_cb(handle, value):
        """
            Indication and notification come asynchronously, we use this function to
            handle them either one at the time as they come.
        :param handle:
        :param value:
        :return:
        """
        self.temp = unpack('B', value)
        

    def battery_cb(handle, value):
        """
            Indication and notification come asynchronously, we use this function to
            handle them either one at the time as they come.
        :param handle:
        :param value:
        :return:
        """
        self.battery = unpack('B', battery_bytes)

def run():
    adapter = pygatt.GATTToolBackend()
    ADDRESS_TYPE = pygatt.BLEAddressType.random

    nearby_devices = adapter.scan()

    headers = {'Content-type': 'application/json'}

    #while True:
    for name, addr in nearby_devices:
        if name == "Dyp Hydrometer" and not addr in connections:
            t = threading.Thread(target=handle_connection, args=(addr,))
            t.start()

def handle_connection(addr):
    adapter = pygatt.GATTToolBackend()
    ADDRESS_TYPE = pygatt.BLEAddressType.random

    try:
        ada.start()

        device = ada.connect(addr, address_type=ADDRESS_TYPE) 
        device.bond()
        device.subscribe('00000001-0000-1000-8000-00805f9b34fb',
                            callback=reading.xyz_cb,
                            indication=True)
        device.subscribe('00000004-0000-1000-8000-00805f9b34fb',
                            callback=reading.temp_cb,
                            indication=True)
        device.subscribe('00000003-0000-1000-8000-00805f9b34fb',
                            callback=reading.battery_cb,
                            indication=True)

        hydro_resp = requests.get(f'http://localhost:5000/api/hydrometers/{addr}', headers=headers)

        if hydro_resp.status_code != 200:
            print(f"no such hydrometer {address}, adding via API")

            data = {}
            data["color"] = "#000000"
            data["battery"] = battery
            create_resp = requests.put(f'http://localhost:5000/api/hydrometers/', data=json.dumps(data), headers=headers)

            if create_resp.status_code != 200:
                print("Error adding hydrometer, terminating connection...")
                ada.stop()
                return

            hydro_resp = create_resp
            
        hydrometer = json.jsonify(hydro_resp.text)
        reading = Reading()

        while True:
            #xyz_bytes = device.char_read('00000001-0000-1000-8000-00805f9b34fb')
            #temp_bytes = device.char_read('00000004-0000-1000-8000-00805f9b34fb')
            #battery_bytes = device.char_read('00000003-0000-1000-8000-00805f9b34fb')

            #device.char_write('00000002-0000-1000-8000-00805f9b34fb', [0x00]) # LED off
            #time.sleep(2)
            #device.char_write('00000002-0000-1000-8000-00805f9b34fb', [0x02]) # LED on

            # x,y, temp
            #x,y,z = unpack('fff', xyz_bytes)
            #temp = unpack('B', temp_bytes)
            #battery = unpack('B', battery_bytes)

            if reading.data_complete():
                data = {}
                data["battery"] = battery
                data["rssi"] = device.get_rssi()

                # TAKEN FROM ISPINDLE https://github.com/universam1/iSpindel/
                pitch = math.atan2(y, sqrt(x**2 + z**2)) * 180.0 / math.PI
                roll = math.atan2(x, sqrt(y**2 + z**2)) * 180.0 / math.PI
                tilt = math.sqrt(pitch**2 + roll**2)
                data["angle"] = -0.00031 * tilt**2 + 0.557 * tilt - 14.054

                resp = requests.put(f'http://localhost:5000/api/hydrometers/{hydrometer["id"]}/reading/', data=json.dumps(data), headers=headers)

                if resp.status_code == 200:
                    print(f"Succesfully added reading from hydrometer #{hydrometer['id']}")
                    print(data)
                else:
                    print(f"Error adding reading for hydrometer #{hydrometer['id']}")
                    print(data)

                
                time.sleep(device["interval"])
                continue
            
            time.sleep(.5)
            print()
    finally:
        #time.sleep()
        ada.stop()

if __name__ == "__main__":
    run()
