import time
import paho.mqtt.publish as publish
import json 
import sys
from utils import get_config_attr
import logging

LOGFILE=get_config_attr("LOGFILE", '/openvpn-status.log')
NAME=get_config_attr("NAME","openvpn")
UPDATE_TIME = int(get_config_attr("UPDATE_TIME",300))

MQTT=get_config_attr("MQTT_HOST","127.0.0.1") # broker address
MQTT_PORT=int(get_config_attr("MQTT_PORT",1883)) # basic mqtt port
MQTT_USER=get_config_attr("MQTT_USER","") # None)
MQTT_PASSWORD=get_config_attr("MQTT_PASSWORD","") 
mqtt_auth={ "username":MQTT_USER,"password":MQTT_PASSWORD} if MQTT_USER else None # mqtt broker login 

DEBUG=get_config_attr("DEBUG",False)
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG if DEBUG else logging.INFO)

class openvpn2mqtt():
    """OpenVPN status to MQTT"""
    def __init__(self, filename, name="openvpn"):

        self.name = name
        self.filename = filename
        self.devicename = "openvpn"
        self._topic = f"{self.devicename}/{name}"
        self._last = None
        self._clients = {}
        self._device = {
            "name": self.name.capitalize(),
            "identifiers": [
                f"{self.devicename}_{self.name}"
            ],
            "manufacturer": "OpenVPN",
            "model": "openvpn2mqtt",
            "sw_version": "0.1.0"
        }

        _LOGGER.debug(f"Initializing MQTT: {MQTT}:{MQTT_PORT}")
        self.publish_discovery()
        _LOGGER.debug(f"Starting monitoring '{LOGFILE}' as {NAME}")
        self.run()

    
    def run(self):
        while True:
            data = self.parse_file()
            if data.get("error"):
                _LOGGER.error(data['error'])
            else:   
                _LOGGER.debug(data)
                self.publish_data(data)
                self._last = data
            time.sleep(UPDATE_TIME)

    def parse_file(self):
        def convert(d):
            if d.isnumeric():
                return float(d) if "." in d else int(d) 
            return d

        parsed = {}
        try:
            with open(self.filename) as logfile:
                lines = logfile.readlines()

            headers = {}
            for line in lines:
                ss = line.split(",")
                key = ss[0].strip("\n")
                data = [convert(s.strip("\n")) for s in ss[1:]]
                if key == "HEADER":
                    headers[data[0]] = data[1:]
                elif key in headers:
                    if key not in parsed:
                        parsed[key] = []
                    items = {}
                    for i, item in enumerate(headers[key]):
                        items[item] = data[i] 
                    parsed[key].append(items) 
                elif key == "END":
                    continue
                else:
                    parsed[key] = data 
        except Exception as e:
            parsed["error"] = e    
        
        return parsed

    def publish_discovery(self):
        """Setup MQTT topics for HA auto discovery"""
        def server_sensor():
            availability = {
                "topic": f"{self._topic}/status",
                "payload_available": "available"
            }
            topic = F"homeassistant/sensor/{self.name}/{self.name}/config"
            config = {
                "name": self.name.capitalize()+" Clients",
                "unique_id": f"{self.name}_clients",
                "icon": "mdi:vpn",
                "device": self._device,
                "availability": availability,
                "json_attributes_topic":f"{self._topic}/clients/attributes",
                "state_topic": f"{self._topic}/clients/count",
                "state_class": "measurement"
            }
            return {"topic": topic, "payload": json.dumps(config)}

        msgs=[]
        # server sensor
        msgs.append( server_sensor())
        publish.multiple(msgs, MQTT, MQTT_PORT, auth=mqtt_auth)
        
    def publish_data(self, data):
        """Sends MQTT data packet"""
        def rate_sensor(client, name):
            availability = {
                "topic": f"{self._topic}/status",
                "payload_available": "available"
            }
            topic = F"homeassistant/sensor/{self.name}/{self.name}_{client}_{name}/config"
            config = {
                "name": client.capitalize() + " " + name,
                "unique_id": f"{self.name}_{client}_{name}",
                "icon": "mdi:download-network" if "down" in name else "mdi:upload-network",
                "device": self._device,
                "availability": availability,
                #"json_attributes_topic":f"{self._topic}/{client}/attributes",
                "state_topic": f"{self._topic}/{client}/{name}",
                "unit_of_measurement":  "kB/s",
                "state_class": "measurement"
            }
            return {"topic": topic, "payload": json.dumps(config)}

        ts = data['TIME'][1]
        secs = ts - self._last['TIME'][1] if self._last else 0
        print("time:",secs)
        clients = data.get('CLIENT_LIST')
        msgs = [
            #{'topic':f"{self._topic}/title", 'payload': data.get("TITLE") },
            {'topic':f"{self._topic}/clients/count", 'payload': len(clients) if clients else 0 },
            {'topic':f"{self._topic}/clients/attributes", 'payload':json.dumps({'client_list': clients}) },
            {'topic':f"{self._topic}/status", 'payload': "available" },
            {'topic':f"{self._topic}/timestamp", 'payload': ts },
            {'topic':f"{self._topic}/routes", 'payload':json.dumps({'routing_table': data.get('ROUTING_TABLE')}) }
        ]
        
        for client in clients:
            name = client['Common Name']
            if name not in self._clients and name != "UNDEF":
                _LOGGER.info(f"New client detected: {name}")
                msgs.append( rate_sensor(name, "rate_down") )
                msgs.append( rate_sensor(name, "rate_up") )
            client_topic = f"{self._topic}/{name}"
            client_last = self._clients.get(name)
            msgs.append({'topic':f"{client_topic}/connected", 'payload':client.get('Connected Since')})
            msgs.append({'topic':f"{client_topic}/attributes", 'payload':json.dumps(client)})
            if client_last and secs: 
                bps_in = (client['Bytes Received'] - client_last['Bytes Received']) / secs
                bps_out = (client['Bytes Sent'] - client_last['Bytes Sent']) / secs
                msgs.append({'topic':f"{client_topic}/rate_down", 'payload': round(bps_in/1024,3)})
                msgs.append({'topic':f"{client_topic}/rate_up", 'payload': round(bps_out/1024,3)})
            self._clients[name] = client
        publish.multiple(msgs, MQTT, MQTT_PORT, auth=mqtt_auth)

openvpn2mqtt(LOGFILE, NAME)
