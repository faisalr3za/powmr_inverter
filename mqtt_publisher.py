# mqtt_publisher.py
import paho.mqtt.client as mqtt
import logging

class MQTTPublisher:
    def __init__(self, config):
        """
        Initializes the MQTTPublisher with MQTT broker details.
        """
        self.broker = config['mqtt']['broker']
        self.port = config['mqtt']['port']
        self.username = config['mqtt']['username']
        self.password = config['mqtt']['password']
        self.topic_prefix = config['mqtt']['topic_prefix']
        self.discovery_prefix = config['mqtt']['discovery_prefix']
        self.client = mqtt.Client()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if config['modbus']['debug'] else logging.INFO)  # Use same debug setting

        self.client.username_pw_set(self.username, self.password)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.connect()

    def connect(self):
        """Connects to the MQTT broker."""
        try:
            self.client.connect(self.broker, self.port, 60)  # Keepalive = 60 seconds
            self.client.loop_start()  # Start the MQTT client loop in a background thread
            self.logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")

    def on_connect(self, client, userdata, flags, rc):
        """Callback function for when the MQTT client connects to the broker."""
        if rc == 0:
            self.logger.info("MQTT connection successful")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback function for when the MQTT client disconnects from the broker."""
        if rc != 0:
            self.logger.warning(f"MQTT disconnected unexpectedly (code {rc}).  Attempting to reconnect...")
            # Attempt to reconnect (you might want to add a delay here)
            self.connect()

    def publish(self, topic, payload, retain=False):
        """Publishes a message to the MQTT broker."""
        full_topic = f"{self.topic_prefix}/{topic}"
        try:
            self.client.publish(full_topic, payload, retain=retain)
            self.logger.debug(f"Published to {full_topic}: {payload}")
        except Exception as e:
            self.logger.error(f"Failed to publish to {full_topic}: {e}")

    def disconnect(self):
        """Disconnects from the MQTT broker."""
        self.client.loop_stop()  # Stop the MQTT client loop
        self.client.disconnect()
        self.logger.info("Disconnected from MQTT broker")
