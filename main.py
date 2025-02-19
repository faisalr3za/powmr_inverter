# main.py (MODIFIED - PRINT ITERATION SEPARATOR AT START AND END)
import yaml
import time
import logging
import paho.mqtt.client as mqtt
import serial
import minimalmodbus
import json
import os  # Import for environment variables

# --- Configuration from Environment Variables ---
SERIAL_PORT = os.environ.get("POWMR_SERIAL_PORT", "/dev/ttyUSB0")
BAUD_RATE = int(os.environ.get("POWMR_BAUD_RATE", 9600))
MODBUS_ADDRESS = int(os.environ.get("POWMR_MODBUS_ADDRESS", 1))
MQTT_BROKER = os.environ.get("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", 1883))
MQTT_USER = os.environ.get("MQTT_USER", "your_mqtt_username")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "your_mqtt_password")
MQTT_TOPIC_PREFIX = "homeassistant/powmr"  # Use single prefix
MQTT_DISCOVERY_PREFIX = "homeassistant"
YAML_FILE = "powmr.yaml"

def setup_logging(debug=False):
    """Sets up basic logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

def load_config(config_file):
    """Loads configuration from a YAML file."""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_file}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing configuration file: {e}")
        return None

# --- MQTT Connection Callbacks ---
def on_connect(client, userdata, flags, rc):
    """Callback function for MQTT connection."""
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.publish(f"{MQTT_TOPIC_PREFIX}/status", "online", retain=True)  # Status topic
    else:
        logger.error(f"MQTT connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    """Callback function for MQTT disconnection."""
    if rc != 0:
        logger.warning(f"MQTT disconnected unexpectedly (code {rc}).")

if __name__ == "__main__":
    # Initialize logging
    logger = setup_logging(True)  # Enable debug logging

    # Load YAML configuration
    config = load_config(YAML_FILE)  # Load directly (no separate config.yaml)
    if not config:
        exit(1)

    # --- MinimalModbus Setup ---
    try:
        instrument = minimalmodbus.Instrument(SERIAL_PORT, MODBUS_ADDRESS)
        instrument.serial.baudrate = BAUD_RATE
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 1  # Reduced timeout
        instrument.debug = False  # Disable MinimalModbus debug mode (set to True for debugging)
        logger.info(f"Connected to Modbus at {SERIAL_PORT}, address {MODBUS_ADDRESS}")

    except serial.SerialException as e:
        logger.error(f"Error opening serial port: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"Error initializing MinimalModbus: {e}")
        exit(1)

    # --- MQTT Setup ---
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1) # add mqtt version
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        logger.error(f"Error connecting to MQTT broker: {e}")
        exit(1)

    # --- Helper Functions ---
    def read_modbus_value(item):
        """Reads a Modbus value and applies transformations (if any)."""
        try:
            address = item["address"]
            register_type = item.get("register_type", "holding")

            # Determine read function based on register type
            if register_type == "input":
                read_func = instrument.read_input_register
            else:
                read_func = instrument.read_register

            # Read the value
            value = read_func(address, 0, signed=item.get("value_type", "").startswith("S"))

            # Apply transformations for text sensors
            if "id" in item and item["id"] == "working_mode":
                mapping = {0: "Power On Mode", 1: "Standby mode", 2: "Mains mode", 3: "Off-Grid mode",
                           4: "Bypass mode", 5: "Charging mode", 6: "Fault mode"}
                return mapping.get(value, str(value))

            # Apply multiplication factor
            multiply = item.get("filters", [{}])[0].get("multiply", 1.0)
            return value * multiply

        except (minimalmodbus.ModbusException, KeyError, IndexError) as e:
            logger.error(f"Error reading {item.get('name', 'Unknown')}: {e}")
            return None

    def publish_mqtt(item, value):
        """Publishes data to MQTT and sends Home Assistant discovery message."""
        try:
            sensor_id = item.get("id", item['name'].lower().replace(" ", "_"))
            topic = f"{MQTT_TOPIC_PREFIX}/{sensor_id}/state"
            client.publish(topic, value, retain=False)

            # Home Assistant Discovery
            unique_id = f"powmr_{sensor_id}"
            discovery_topic = f"{MQTT_DISCOVERY_PREFIX}/sensor/{unique_id}/config"
            payload = {
                "name": item.get('name', 'Unknown'),
                "unique_id": unique_id,
                "state_topic": topic,
                "value_template": "{{ value }}",
                "availability_topic": f"{MQTT_TOPIC_PREFIX}/status",
                "payload_available": "online",
                "payload_not_available": "offline",
                "device": {  # Add device information
                    "identifiers": ["powmr_inverter"],
                    "name": "PowMr Inverter",
                    "manufacturer": "PowMr",
                    "model": "POW-HVM6.2M-48V-LIP"
                }
            }
            # Add unit, device class, and state class if available
            payload.update({k: item.get(k) for k in ("unit_of_measurement", "device_class", "state_class") if item.get(k)})
            client.publish(discovery_topic, json.dumps(payload), retain=True)

        except Exception as e:
            logger.error(f"Error publishing to MQTT: {e}")

    # --- Main Loop ---
    try:
        while True:
            print("----- START -----")  # Print separator at the START of each iteration

            # Combine sensors and text sensors
            all_items = config.get("text_sensor", []) + config.get("sensor", []) + config.get("select", []) + config.get("number", []) + config.get("switch", [])

            for item in all_items:
                if item.get("platform") == "modbus_controller":
                    value = read_modbus_value(item)
                    if value is not None:
                        logger.info(f"{item.get('name', 'Unknown')}: {value} {item.get('unit_of_measurement','')}")
                        publish_mqtt(item, value)
            
            print("----- END -----") # Print separator at the END of each iteration

            time.sleep(15)

    except KeyboardInterrupt:
        logger.info("Exiting...")

    finally:
        client.publish(f"{MQTT_TOPIC_PREFIX}/status", "offline", retain=True)
        client.loop_stop()
        client.disconnect()
        logger.info("Disconnected from MQTT broker")
