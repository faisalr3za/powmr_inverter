# powmr_reader.py
import minimalmodbus
import serial
import logging
import time

class PowMrReader:
    def __init__(self, config):
        """
        Initializes the PowMrReader with serial and Modbus configurations.
        """
        self.port = config['serial']['port']
        self.baudrate = config['serial']['baudrate']
        self.parity = config['serial']['parity']
        self.bytesize = config['serial']['bytesize']
        self.stopbits = config['serial']['stopbits']
        self.timeout = config['serial']['timeout']
        self.slave_address = config['modbus']['slave_address']
        self.close_port_after_each_call = config['modbus']['close_port_after_each_call']
        self.debug = config['modbus']['debug']
        self.instrument = None
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        self.connect()

    def connect(self):
        """
        Connects to the Modbus device using the configured serial port.
        """
        try:
            self.instrument = minimalmodbus.Instrument(self.port, self.slave_address)
            self.instrument.serial.baudrate = self.baudrate
            self.instrument.serial.parity = self.parity.upper()[0] if self.parity else serial.PARITY_NONE
            self.instrument.serial.bytesize = self.bytesize
            self.instrument.serial.stopbits = self.stopbits
            self.instrument.serial.timeout = self.timeout
            self.instrument.close_port_after_each_call = self.close_port_after_each_call
            self.instrument.debug = self.debug
            self.logger.info(f"Connected to PowMr inverter at {self.port}")
        except Exception as e:
            self.logger.error(f"Failed to connect to PowMr inverter: {e}")
            self.instrument = None

    def read_register(self, address, number_of_decimals=0, signed=False, register_type='holding'):
        """
        Reads a register from the Modbus device.

        Args:
            address (int): The register address.
            number_of_decimals (int): Number of decimals for the value.
            signed (bool): Whether the value is signed.
            register_type (str): 'holding' or 'input'.

        Returns:
            float: The register value, or None if an error occurred.
        """
        if not self.instrument:
            self.logger.error("Not connected to PowMr inverter.")
            return None

        try:
            if register_type == 'holding':
                value = self.instrument.read_register(address, number_of_decimals, signed, minimalmodbus.MODE_RTU)
            elif register_type == 'input':
                value = self.instrument.read_register(address, number_of_decimals, signed, minimalmodbus.MODE_RTU) # Corrected line
            else:
                self.logger.error(f"Invalid register type: {register_type}")
                return None

            self.logger.debug(f"Read register {address}: {value}")
            return value
        except Exception as e:
            self.logger.error(f"Error reading register {address}: {e}")
            return None

    def read_string(self, address, length):
        """Reads a string from consecutive registers."""
        if not self.instrument:
            self.logger.error("Not connected to PowMr inverter.")
            return None

        try:
            value = self.instrument.read_string(registeraddress=address, number_of_registers=length, mode=minimalmodbus.MODE_RTU)
            self.logger.debug(f"Read string from register {address}: {value}")
            return value
        except Exception as e:
            self.logger.error(f"Error reading string from register {address}: {e}")
            return None

    def read_registers(self, start_address, register_count, signed=False):
        """Reads multiple consecutive registers."""
        if not self.instrument:
            self.logger.error("Not connected to PowMr inverter.")
            return None

        try:
            values = self.instrument.read_registers(registeraddress=start_address, number_of_registers=register_count, mode=minimalmodbus.MODE_RTU)
            self.logger.debug(f"Read registers from {start_address} (count: {register_count}): {values}")
            return values
        except Exception as e:
            self.logger.error(f"Error reading registers from {start_address}: {e}")
            return None

    def write_register(self, address, value, number_of_decimals=0, signed=False):
        """Writes a value to a Modbus register."""
        if not self.instrument:
            self.logger.error("Not connected to PowMr inverter.")
            return False

        try:
            self.instrument.write_register(registeraddress=address, value=value, number_of_decimals=number_of_decimals, signed=signed, mode=minimalmodbus.MODE_RTU)
            self.logger.debug(f"Wrote {value} to register {address}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing to register {address}: {e}")
            return False
