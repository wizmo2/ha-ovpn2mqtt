# OpenVPN 2 MQTT

Dockerizable script to monitor OpenVPN server status in Home-Assistant

The script monitors the status log file utilizes MQTT Discovery 

# Log file
The default OpenVPN log file is stored in `/etc/openvpn/<server>` folder. _NOTE:  default refresh time is 60s_

You can specify the location within the openvpn configuration file
```
state /var/logs/openvpn-status.log
```

# Docker
Build the docker
```
cd ~/ha-ovpn2mqtt
sudo docker build -t ha-ovpn2mqtt .
```

Run the docker
```
sudo docker run -it &1 \
 --name ovpn2mqtt \
 --restart=always \
 -v /var/log/openvpn-status.log:/openvpn-status.log \
 -v ~/ha-ovpn2mqtt/:/app/ \
 -e OVPN2MQTT_NAME=<sensor name:openvpn> \
 -e OVPN2MQTT_UPDATE_TIME=<refresh seconds:300(5min)> \
 -e OVPN2MQTT_MQTT_HOST=<broker host:127.0.0.1> \
 -e OVPN2MQTT_MQTT_PORT=<broker port:1883> \
 -e OVPN2MQTT_MQTT_USER=<broker username:> \
 -e OVPN2MQTT_MQTT_PASSWORD=<broker user password:> \
 -e OVPN2MQTT_DEBUG=<debug loglevel:False> \
   ha-ovpn2mqtt
 ```

 > #### TODO:
 > - Add telnet management support. _NOTE:  It is possible to retrieve the status log file remotely using telnet, but onlt one connection session is supported and telnet within python is depreciated._
 