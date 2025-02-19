# hass_discovery.py
import json
import logging

class HassDiscovery:
    def __init__(self, config):
        """
        Initializes HassDiscovery with MQTT topic prefix.
        """
        self.discovery_prefix = config['mqtt']['discovery_prefix']
        self.device_name = "PowMr Inverter"  # Customize as needed
        self.device_identifier = "powmr_inverter_1"  # Unique ID
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if config['modbus']['debug'] else logging.INFO)

    def create_sensor_discovery_config(self, sensor, component="sensor"):
        """
        Creates a Home Assistant MQTT discovery configuration for a sensor.
        """
        object_id = sensor['id']
        config_topic = f"{self.discovery_prefix}/{component}/{self.device_identifier}/{object_id}/config"

        device_config = {
            "name": sensor['name'],
            "state_topic": f"{self.discovery_prefix}/sensor/{self.device_identifier}/{object_id}/state",
            "unique_id": f"{self.device_identifier}_{object_id}",
            "device": {
                "identifiers": [self.device_identifier],
                "name": self.device_name,
                "manufacturer": "PowMr",  # Or the correct manufacturer
                "model": "POW-HVM6.2M-48V-LIP",
            },
        }

        # Add optional attributes
        if 'unit_of_measurement' in sensor:
            device_config["unit_of_measurement"] = sensor['unit_of_measurement']
        if 'device_class' in sensor:
            device_config["device_class"] = sensor['device_class']
        if 'state_class' in sensor:
            device_config["state_class"] = sensor['state_class']
        if 'entity_category' in sensor:
            device_config["entity_category"] = sensor['entity_category']
        if 'icon' in sensor:
            device_config["icon"] = sensor['icon']
        if 'optionsmap' in sensor:
            device_config["options"] = list(sensor["optionsmap"].keys())
        if 'min_value' in sensor:
            device_config["min"] = sensor['min_value']
        if 'max_value' in sensor:
            device_config["max"] = sensor['max_value']
        if 'step' in sensor:
            device_config["step"] = sensor['step']

        try:
            payload = json.dumps(device_config)
            self.logger.debug(f"Discovery topic: {config_topic}, payload: {payload}")
            return config_topic, payload
        except Exception as e:
            self.logger.error(f"Error creating discovery config for {sensor['name']}: {e}")
            return None

    def create_text_sensor_discovery_config(self, sensor):
      """
      Creates a Home Assistant MQTT discovery configuration for a text sensor.
      Args:
          sensor (dict): Sensor definition from the YAML file.
      Returns:
          tuple: (discovery_topic, discovery_payload) or None if there's an error.
      """
      object_id = sensor['id']
      config_topic = f"{self.discovery_prefix}/text/{self.device_identifier}/{object_id}/config"
      device_config = {
          "name": sensor['name'],
          "state_topic": f"{self.discovery_prefix}/sensor/{self.device_identifier}/{object_id}/state",
          "unique_id": f"{self.device_identifier}_{object_id}",
          "device": {
              "identifiers": [self.device_identifier],
              "name": self.device_name,
              "manufacturer": "PowMr",  # Or the correct manufacturer
              "model": "POW-HVM6.2M-48V-LIP",
          },
      }
      if 'entity_category' in sensor:
            device_config["entity_category"] = sensor['entity_category']
      try:
          payload = json.dumps(device_config)
          self.logger.debug(f"Discovery topic: {config_topic}, payload: {payload}")
          return config_topic, payload
      except Exception as e:
          self.logger.error(f"Error creating discovery config for {sensor['name']}: {e}")
          return None

    def create_select_discovery_config(self, select):
        """
        Creates a Home Assistant MQTT discovery configuration for a select entity.
        """
        object_id = select.get('id', select['name'].lower().replace(" ", "_")) # added default value
        config_topic = f"{self.discovery_prefix}/select/{self.device_identifier}/{object_id}/config"

        device_config = {
            "name": select['name'],
            "state_topic": f"{self.discovery_prefix}/select/{self.device_identifier}/{object_id}/state",
            "command_topic": f"{self.discovery_prefix}/select/{self.device_identifier}/{object_id}/set",
            "unique_id": f"{self.device_identifier}_{object_id}",
            "options": list(select['optionsmap'].keys()),
            "device": {
                "identifiers": [self.device_identifier],
                "name": self.device_name,
                "manufacturer": "PowMr",  # Or the correct manufacturer
                "model": "POW-HVM6.2M-48V-LIP",
            },
        }
        if 'entity_category' in select:
            device_config["entity_category"] = select['entity_category']

        try:
            payload = json.dumps(device_config)
            self.logger.debug(f"Discovery topic: {config_topic}, payload: {payload}")
            return config_topic, payload
        except Exception as e:
            self.logger.error(f"Error creating discovery config for {select['name']}: {e}")
            return None

    def create_number_discovery_config(self, number):
        """
        Creates a Home Assistant MQTT discovery configuration for a number entity.
        """
        object_id = number.get('id', number['name'].lower().replace(" ", "_")) # added default value
        config_topic = f"{self.discovery_prefix}/number/{self.device_identifier}/{object_id}/config"

        device_config = {
            "name": number['name'],
            "state_topic": f"{self.discovery_prefix}/number/{self.device_identifier}/{object_id}/state",
            "command_topic": f"{self.discovery_prefix}/number/{self.device_identifier}/{object_id}/set",
            "unique_id": f"{self.device_identifier}_{object_id}",
            "min": number['min_value'],
            "max": number['max_value'],
            "step": number['step'],
            "device": {
                "identifiers": [self.device_identifier],
                "name": self.device_name,
                "manufacturer": "PowMr",  # Or the correct manufacturer
                "model": "POW-HVM6.2M-48V-LIP",
            },
        }
        if 'entity_category' in number:
            device_config["entity_category"] = number['entity_category']

        try:
            payload = json.dumps(device_config)
            self.logger.debug(f"Discovery topic: {config_topic}, payload: {payload}")
            return config_topic, payload
        except Exception as e:
            self.logger.error(f"Error creating discovery config for {number['name']}: {e}")
            return None

    def create_switch_discovery_config(self, switch):
        """
        Creates a Home Assistant MQTT discovery configuration for a switch entity.
        """
        object_id = switch.get('id', switch['name'].lower().replace(" ", "_")) # added default value
        config_topic = f"{self.discovery_prefix}/switch/{self.device_identifier}/{object_id}/config"

        device_config = {
            "name": switch['name'],
            "state_topic": f"{self.discovery_prefix}/switch/{self.device_identifier}/{object_id}/state",
            "command_topic": f"{self.discovery_prefix}/switch/{self.device_identifier}/{object_id}/set",
            "unique_id": f"{self.device_identifier}_{object_id}",
            "payload_on": "1",
            "payload_off": "0",
            "state_on": "1",
            "state_off": "0",
            "device": {
                "identifiers": [self.device_identifier],
                "name": self.device_name,
                "manufacturer": "PowMr",  # Or the correct manufacturer
                "model": "POW-HVM6.2M-48V-LIP",
            },
            "icon": switch.get('icon', "mdi:toggle-switch"),  # Use default icon if not specified
        }
        if 'entity_category' in switch:
            device_config["entity_category"] = switch['entity_category']

        try:
            payload = json.dumps(device_config)
            self.logger.debug(f"Discovery topic: {config_topic}, payload: {payload}")
            return config_topic, payload
        except Exception as e:
            self.logger.error(f"Error creating discovery config for {switch['name']}: {e}")
            return None
