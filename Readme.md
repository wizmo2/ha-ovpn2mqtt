# OpenVPN 2 MQTT

Dockerizable script to monitor OpenVPN server status in Home-Assistant

The script monitors the status log file utilizes MQTT Discovery 

# OpenVpn log file
The default log file is stored in `/etc/openvpn/' server folder

You can specify the location within the openvpn configuration file
```
state /var/logs/openvpn-status.log
```

# Docker

```
sudo docker build -f ~/ha-ovpn2mqtt/ -t ha-ovpn2mqtt .
sudo docker run -itd \
 -v /var/log/openvpn-status.log:/openvpn-status.log \ # openvpn log file lovation
 -v ~/ha-ovpn2mqtt/:/app/ \ # debug
 -e OVPN2MQTT_NAME=<sensor name:openvpn> \ 
 -e OVPN2MQTT_UPDATE_TIME=<host:127.0.0.1> \
 -e OVPN2MQTT_MQTT=<brocker host:127.0.0.1> \
 -e OVPN2MQTT_MQTT_PORT=<brocker port:1883> \
 -e OVPN2MQTT_MQTT_USER=<brocker username:> \
 -e OVPN2MQTT_MQTT_PASSWORD=<broker user password:> \
   ovpn2mqtt
 ```

 > #### TODO:
 > - Add telnet management support. _NOTE:  It is possible to retrieve the status log file remotely using telnet, but onlt one connection session is supported and telnet within python is depreciated._
 