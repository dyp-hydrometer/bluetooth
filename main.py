import bluetooth
import requests, json

# need a way to differentiate between different hydrometers
# cant be by address, because that can change?

target_name = "dyp_hydrometer"
target_address = None

nearby_devices = bluetooth.discover_devices()

for addr, name in nearby_devices:
    print(f"{addr} - {name}")
    if target_name == name:
        target_address = addr
        #break

if target_address is not None:
    print ("found target bluetooth device with address ", target_address)

    # obtain characteristic data from target
    # battery
    # interval
    # 

    headers = {'Content-type': 'application/json'}

    hydrometers = requests.get('http://localhost:5000/api/hydrometers/', headers=headers)

    # look for already matching hydrometer
    found = False
    for hydrometer in hydrometers.json():
        if hydrometer["colorname"] == "#FFFF00":
            found = True

    # insert new record if none exist for this hydrometer
    if not found:
        insert_new = requests.post('http://localhost:5000/api/hydrometers/',
                                    data=json.dumps({'color':,target["color"] 'battery':taget["battery"]}),
                                    headers=headers)


    # poll for new readings and update if found
    while(True):
        

else:
    print("could not find target bluetooth device nearby")
