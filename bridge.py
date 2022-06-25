#!/usr/bin/env python3
import random
import sys
import time
import yaml
from paho.mqtt import client as mqtt_client


def connect_mqtt(client_id, username, password, host):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker {host}")
        else:
            print(f"Failed to connect {host}, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    return client


def publish(client: mqtt_client, payload, topic: str, is_retained):
    result = client.publish(topic, payload, retain=is_retained)  # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{payload}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def subscribe(client: mqtt_client, topic: str, on_message):
    client.subscribe(topic)
    client.on_message = on_message


def start_bridge(bridge_config):
    from_host = bridge_config['bridge-from']['host']
    from_port = bridge_config['bridge-from']['port']
    from_user = bridge_config['bridge-from'].get("user")
    from_password = bridge_config['bridge-from'].get("password")
    from_client_id = f'python-bridge-mqtt-{random.randint(0, 1000)}'
    from_topic = bridge_config['bridge-from']['topic']

    to_host = bridge_config['bridge-to']['host']
    to_port = bridge_config['bridge-to']['port']
    to_user = bridge_config['bridge-to'].get("user")
    to_password = bridge_config['bridge-to'].get("password")
    to_client_id = f'python-bridge-mqtt-{random.randint(0, 1000)}'
    to_topic = bridge_config['bridge-to']['topic']

    to_connection = None
    from_connection = None

    def on_message_from_source_broker(client, userdata, msg):
        decoded_msg = msg.payload.decode()
        is_retained = msg.retain
        print(f"Received `{decoded_msg}` from `{msg.topic}` topic, retained: {is_retained}")
        if to_connection.is_connected():
            destination_topic = f"{to_topic}/{msg.topic}"
            print(f"Forwarding message to destination broker at {destination_topic}")
            publish(to_connection, decoded_msg, destination_topic, is_retained)
            pass

    while True:
        try:
            if to_connection is None:
                to_connection = connect_mqtt(to_client_id, to_user, to_password, to_host)

            if from_connection is None:
                from_connection = connect_mqtt(from_client_id, from_user, from_password, from_host)

            if not to_connection.is_connected():
                try:
                    to_connection.connect(to_host, to_port)
                except Exception as e:
                    print(f"Error making connection to {to_host}, {e}")
                    time.sleep(1)

            if not from_connection.is_connected():
                try:
                    from_connection.connect(from_host, from_port)
                except Exception as e:
                    print(f"Error making connection to {from_host}, {e}")
                    time.sleep(1)
                subscribe(from_connection, from_topic, on_message_from_source_broker)

            if to_connection is not None:
                to_connection.loop()

            if from_connection is not None:
                from_connection.loop()
        except InterruptedError:
            return
    pass


def main(config_file_location: str):
    with open(config_file_location, "r") as stream:
        try:
            bridge_config = yaml.safe_load(stream)
            print(bridge_config)
            start_bridge(bridge_config)
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Pass config file path as the only parameter to the application")
        print(f"Usage: '{sys.argv[0]} bridge_config.yml'")
        pass
    else:
        print(f"Starting bridge with `{sys.argv[1]}` config file")
        main(sys.argv[1])
