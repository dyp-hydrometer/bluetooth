"""
.. module:: main
    :platform: Linux
    :synopsis: Handles bluetooth connection to hydrometers and sends API requests with the appropriate data

.. moduleauthor:: Evan Campbell
"""

import pygatt
import time as ptime
import math
import threading
from struct import *
import requests
import json
import datetime

# 0x00  
# 0x01 - set interval
# 0x02, 0x03, 0x04, 0x05 - interval value

class Reading:
    """Class to get, store, and update reading info

    Utilizes the flask API to store reading info to the database 
    """
    x = 0.0
    y = 0.0
    z = 0.0
    temp = 0

    hydrometer = None

    def __init__(self, hydrometer):
        """A simple initialization method.

        Args:
            hydrometer dictionary
        """
        self.hydrometer = hydrometer

    def check_for_interval_update(self):
        """Sends API GET request for the hydrometer stored when initializing the class.
        Updates the interval if a 200 response recieved, otherwise prints that an error occured 

        Args:
            None
        """
        headers = {'Content-type': 'application/json'}
        resp = requests.get(f"http://localhost:5000/api/hydrometers/{self.hydrometer['id']}/interval/", data=json.dumps(''), headers=headers)
        if resp.status_code == 200:
            self.hydrometer['interval'] = resp.json()['interval']
            self.hydrometer['interval']
            #    #device.char_write('00000002-0000-1000-8000-00805f9b34fb', [0x01, ]) # LED off
            print(f"Interval reading {self.hydrometer['interval']} - sucessfully updated")
        else:
            print(f"Error retrieving interval from API")


    def update_battery(self, battery):
        """Sends API PUT request to update the current battery level for the connected hydrometer

        Args:
            Battery level
        """
        headers = {'Content-type': 'application/json'}
        resp = requests.put(f"http://localhost:5000/api/hydrometers/{self.hydrometer['id']}/battery", data=json.dumps(battery), headers=headers)
        if resp.status_code == 200:
            print(f"Battery reading {battery} - sucessfully updated")
        else:
            print(f"Battery reading {battery} - error updating")

    def send(self):
        """Sends API PUT request to insert a new row for the current reading. Also calculated the SG by using the function returned by the tilts.py calibration tool.

        Args:
            None
        """
        headers = {'Content-type': 'application/json'}
        data = {}
        data["temp"] = self.temp
        data["time"] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        # TAKEN FROM ISPINDLE https://github.com/universam1/iSpindel/
        # pitch = math.atan2(self.y, math.sqrt(self.x**2 + self.z**2)) * 180.0 / math.pi
        # roll = math.atan2(self.x, math.sqrt(self.y**2 + self.z**2)) * 180.0 / math.pi
        #tilt = math.sqrt(math.pow(self.x,2) + math.pow(self.y,2))
        data["specific_gravity"] = 0.2501056273878099* self.y**2 - 17.46183152398347 * self.y + 1305.112360122884

        resp = requests.put(f"http://localhost:5000/api/hydrometers/{self.hydrometer['id']}/reading/", data=json.dumps(data), headers=headers)

        if resp.status_code == 201:
            print(f"Succesfully added reading from hydrometer #{self.hydrometer['id']}")
            print(data)
        else:
            print(f"Error adding reading for hydrometer #{self.hydrometer['id']}")
            print(data)

    def data_cb(self, handle, value):
        """ PyGaTT callback used when the hydrometer notifies that the xyztemp characteristic has updated. 

        Args:
            Handle
            Value
        """
        
        self.x, self.y, self.z, self.temp = unpack('fffB', value)
        print(f"xyz: {self.x}, {self.y}, {self.z}")
        self.send()

def get_or_create_hydrometer(addr):
    """Checks if the newly connected hydrometer exists in the database, creates a new entry if it doesn't exist, and returns the hydrometer data

    Args:
        MAC_ADDR
    """
    headers = {'Content-type': 'application/json'}
    hydro_resp = requests.get("http://localhost:5000/api/hydrometers/"+addr, headers=headers)

    if hydro_resp.status_code != 200:
        print(f"no such hydrometer {addr}, adding via API")

        data = {}
        data["color"] = "#000000"
        data["battery"] = 0.0
        data["mac_addr"] = addr
        create_resp = requests.post(f"http://localhost:5000/api/hydrometers/", data=json.dumps(data), headers=headers)

        if create_resp.status_code != 201:
            print("Error adding hydrometer")
            ada.stop()
            return None

        hydro_resp = create_resp
        
    return json.loads(hydro_resp.text)

def run():
    """Infinite loop searching for new, unconnected hydrometers and connecting to them with new threads for each

    Args:
        None
    """
    adapter = pygatt.GATTToolBackend()
    ADDRESS_TYPE = pygatt.BLEAddressType.random

    # TODO if a thread is killed then this will never reestablish a new one since connections never has elements removed
    while True:
        try:
            for device in adapter.scan():
                if device["name"] == "DYP Hydrometer":
                    print("NEW HYDROMETER FOUND")
                    t = threading.Thread(target=handle_connection, args=(device["address"],))
                    t.start()
        except:
            pass
        ptime.sleep(5)

def handle_connection(addr):
    """Main logic for a hydrometer's connection thread. Exists gracefully on a connection error

    Args:
        MAC_ADDR
    """
    ada = pygatt.GATTToolBackend()
    ADDRESS_TYPE = pygatt.BLEAddressType.random

    hydrometer = get_or_create_hydrometer(addr)

    reading = Reading(hydrometer)

    ada.start()

    device = ada.connect(addr, address_type=ADDRESS_TYPE, auto_reconnect=False) 
    device.bond()
    device.subscribe('00000001-0000-1000-8000-00805f9b34fb',
                        callback=reading.data_cb,
                        indication=False)

    print("subbed and looping now")
    start = ptime.time()

    while True:
        interval = reading.hydrometer['interval']
        h,m,s = [ int(x) for x in interval.split(':') ]
        delta = ((h*60+m)*60)+s
        if (ptime.time() - start) > (delta * 2):
            print("interval has passed")
            reading.check_for_interval_update()
            try:
                battery_bytes = device.char_read('00000003-0000-1000-8000-00805f9b34fb')

                battery = unpack('B', battery_bytes)[0]
                reading.update_battery(battery)
            except:
                print("exception, breaking")
                break
            finally:
                print("start reset")
                start = ptime.time()
                #print("connection dropped? value obtained?")
                #ada.stop()
        else:
            ptime.sleep(.5)
            continue
    ada.stop()

if __name__ == "__main__":
    run()
