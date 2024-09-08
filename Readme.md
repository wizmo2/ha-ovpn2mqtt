# OpenVPN 2 MQTT

Dockerizable script to monitor OpenVPN server status in Home-Assistant

The script monitors the OpenVPN status log file and published tp a MQTT broker and Home-Assistant utilizing MQTT Discovery 

## Log file
The default OpenVPN log file is stored in `/etc/openvpn/<server>` folder. _NOTE:  default refresh time is 60s_

You can specify the location within the OpenVpn server configuration file
```
state /var/logs/openvpn-status.log
```

## Docker
The docker file must be run on the openvpn server host.  Typically root access is required to view the log file.

Build the docker
```
cd ~/ha-ovpn2mqtt
sudo docker build -t ha-ovpn2mqtt .
```

Run the docker
```
sudo docker run -itd \
 --name ovpn2mqtt \
 --restart=unless-stopped \
 -v /var/log/openvpn-status.log:/openvpn-status.log \
 -e OVPN2MQTT_MQTT_HOST="192.168.1.1" 
   ha-ovpn2mqtt
 ```

### Options
The following are available environment options.  

|Parameter|Description|Default|
|-|-|-|
|OVPN2MQTT_NAME|sensor name|"openvpn"|
|OVPN2MQTT_UPDATE_TIME|refresh time in seconds|300|
|OVPN2MQTT_MQTT_HOST|broker host|"127.0.0.1"|
|OVPN2MQTT_MQTT_PORT|broker port|1883|
|OVPN2MQTT_MQTT_USER|broker username|""|
|OVPN2MQTT_MQTT_PASSWORD|broker user password|""|
|OVPN2MQTT_DEBUG|debug loglevel|False|
|OVPN2MQTT_LOGFILE|log file location|"/openvpn-status.log"|
 
_NOTE: Add `-e <parameter>=<value> \` to docker command._

_NOTE: For debugging add `-v ~/ha-ovpn2mqtt/:/app/'_
 

 > #### TODO:
 > - Add telnet management support. _NOTE:  It is possible to retrieve the status log file remotely using telnet, but only one connection session is supported, plus telnet within python is depreciated._
 