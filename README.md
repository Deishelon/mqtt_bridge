# MQTT Bridge

Simple implementation of one way MQTT bridge.  
The goal of this project is to provide a simple way to bridge topics from one broker onto another broker.  

I have developed this, as I ran main MQTT server at home, but there are some applications that need to run in own broker, 
however, I wanted to make some parts available on my home main broker.
This script should be fully autonomous, i.e. it will handle reconnections if network goes down.

### Usage
1. Create virtual environment:
```bash
python3 -m venv venv
```
2. Activate it
```bash
source venv/bin/activate
```
3. Install dependencies
```bash
pip install -r requirements.txt
```
4. Run it
```bash
python bridge.py config_file_path.yml
```

### Config file
Config file must be passed as the only argument to the script,  
the content of the file is:

Example file:
```yaml
bridge-from:
   host: source.home
   port: 1883
   user: 'my_user' # Can be removed if no auth is used
   password: 'my_password' # Can be removed if no auth is used
   topic: 'source_topic/#'


bridge-to:
   host: destination.home
   port: 1883
   user: 'my_user' # Can be removed if no auth is used
   password: 'my_password' # Can be removed if no auth is used
   topic: 'destination_topic'
```

| Key      | Meaning (Common)                                    | Meaning for 'bridge-from'                                    | Meaning for 'bridge-to'                                                                                                                                                                      |
|----------|-----------------------------------------------------|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| host     | The IP or DNS name of the broker                    |                                                              |                                                                                                                                                                                              |
| post     | The port of the broker                              |                                                              |                                                                                                                                                                                              |
| user     | Optional key to provide user name if auth is needed |                                                              |                                                                                                                                                                                              |
| password | Optional key to provide password if auth is needed  |                                                              |                                                                                                                                                                                              |
| topic    | x                                                   | Topic to bridge from the source broker<br/> Wildcards are ok | For every incoming message from source broker this topic will be appended<br/> If bridge to root, leave empty string,<br/>if bridge to non-root location make sure to leave out trailing '/' |


# Run script on start up (systemd)

1. Create system service at `/etc/systemd/system/mqtt_bridge.service`
``` 
[Unit]
Description=MQTT Bridge

Wants=network.target
After=syslog.target network-online.target

[Service]
Type=simple
ExecStart=bash -c "cd /home/pi/mqtt_bridge; source venv/bin/activate; python bridge.py /home/pi/mqtt_bridge_config.yml"
Restart=on-failure
RestartSec=10
KillMode=mixed

[Install]
WantedBy=multi-user.target
```

2. Set permissions
```bash 
sudo chmod 640 /etc/systemd/system/mqtt_bridge.service
```

3. Start service
```bash
sudo systemctl daemon-reload
sudo systemctl enable mqtt_bridge.service
sudo systemctl start mqtt_bridge.service
sudo systemctl status mqtt_bridge.service
```