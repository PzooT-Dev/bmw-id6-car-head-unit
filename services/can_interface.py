# -*- coding: utf-8 -*-

"""
CAN Bus Interface Module
Handles communication with the vehicle's CAN bus
"""

import os
import time
import threading
import logging
import can
from can.interfaces.socketcan import SocketcanBus

logger = logging.getLogger(__name__)

class CANInterface:
    """
    Interface for communicating with the vehicle's CAN bus.
    Uses python-can library to interface with SocketCAN.
    """
    
    def __init__(self, channel='can0', bitrate=500000):
        """
        Initialize the CAN interface.
        
        Args:
            channel (str): CAN interface channel (default: 'can0')
            bitrate (int): CAN bitrate in bps (default: 500000)
        """
        self.channel = channel
        self.bitrate = bitrate
        self.bus = None
        self.running = False
        self.connected = False
        self.thread = None
        self.vehicle_data = {
            'speed': 0,
            'rpm': 0,
            'fuel_level': 0,
            'coolant_temp': 0,
            'outside_temp': 20,
            'engine_on': False
        }
        self.last_received = 0
        
    def start(self):
        """Start the CAN interface and begin reading data."""
        if self.running:
            logger.warning("CAN interface already running")
            return
            
        logger.info(f"Starting CAN interface on channel {self.channel}")
        
        try:
            # Try to set up the interface if on Linux
            if os.name == 'posix':
                os.system(f"sudo ip link set {self.channel} type can bitrate {self.bitrate}")
                os.system(f"sudo ifconfig {self.channel} up")
                
            # Initialize the CAN bus
            self.bus = can.interface.Bus(
                channel=self.channel,
                bustype='socketcan',
                bitrate=self.bitrate
            )
            
            self.running = True
            self.connected = True
            self.last_received = time.time()
            
            # Start the CAN reading thread
            self.thread = threading.Thread(target=self._read_can_messages)
            self.thread.daemon = True
            self.thread.start()
            
            logger.info("CAN interface started successfully")
            
        except Exception as e:
            logger.error(f"Error starting CAN interface: {e}")
            self.connected = False
    
    def stop(self):
        """Stop the CAN interface."""
        if not self.running:
            return
            
        logger.info("Stopping CAN interface")
        
        self.running = False
        
        if self.thread:
            self.thread.join(timeout=1.0)
            
        if self.bus:
            try:
                self.bus.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down CAN bus: {e}")
                
        self.connected = False
        logger.info("CAN interface stopped")
    
    def is_connected(self):
        """
        Check if the CAN interface is connected.
        
        Returns:
            bool: True if connected, False otherwise
        """
        # Check if we've received any messages recently (within 5 seconds)
        if self.connected and time.time() - self.last_received > 5:
            self.connected = False
            
        return self.connected
    
    def get_vehicle_data(self):
        """
        Get the latest vehicle data.
        
        Returns:
            dict: Dictionary containing vehicle data
        """
        return self.vehicle_data.copy()
    
    def _read_can_messages(self):
        """Thread function to continuously read CAN messages."""
        while self.running:
            try:
                # Read a message with timeout
                message = self.bus.recv(timeout=0.5)
                
                if message:
                    self.last_received = time.time()
                    self._process_can_message(message)
                    
            except Exception as e:
                logger.error(f"Error reading CAN message: {e}")
                self.connected = False
                time.sleep(1.0)  # Wait before retrying
    
    def _process_can_message(self, message):
        """
        Process a CAN message and update vehicle data.
        
        Args:
            message: CAN message object
        """
        try:
            # Here we would have actual CAN ID mapping for the specific vehicle
            # This is a simplified example - real implementation would depend on
            # the specific vehicle's CAN protocol
            
            # Example: Speed data on ID 0x316 (BMW)
            if message.arbitration_id == 0x316:
                # Convert data to speed value (BMW specific)
                speed_raw = (message.data[1] << 8) | message.data[0]
                speed_kph = speed_raw * 0.01  # Scale factor depends on vehicle
                self.vehicle_data['speed'] = int(speed_kph)
            
            # Example: RPM data on ID 0x329 (BMW)
            elif message.arbitration_id == 0x329:
                # Convert data to RPM value
                rpm_raw = (message.data[1] << 8) | message.data[0]
                rpm = rpm_raw * 0.25  # Scale factor depends on vehicle
                self.vehicle_data['rpm'] = int(rpm)
            
            # Example: Engine temperature on ID 0x329 (BMW)
            elif message.arbitration_id == 0x329:
                temp_raw = message.data[2]
                temp_c = temp_raw - 40  # Offset depends on vehicle
                self.vehicle_data['coolant_temp'] = temp_c
            
            # Example: Fuel level on ID 0x349 (BMW)
            elif message.arbitration_id == 0x349:
                fuel_raw = message.data[0]
                fuel_percent = fuel_raw * 0.392  # Scale factor depends on vehicle
                self.vehicle_data['fuel_level'] = int(fuel_percent)
            
            # Example: Outside temperature on ID 0x410 (BMW)
            elif message.arbitration_id == 0x410:
                temp_raw = message.data[3]
                temp_c = (temp_raw - 128) * 0.5  # Conversion depends on vehicle
                self.vehicle_data['outside_temp'] = temp_c
            
        except Exception as e:
            logger.error(f"Error processing CAN message: {e}")
    
    def send_message(self, arb_id, data):
        """
        Send a CAN message.
        
        Args:
            arb_id (int): Arbitration ID
            data (bytes): Message data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Cannot send message: CAN interface not connected")
            return False
            
        try:
            message = can.Message(
                arbitration_id=arb_id,
                data=data,
                is_extended_id=False
            )
            self.bus.send(message)
            return True
        except Exception as e:
            logger.error(f"Error sending CAN message: {e}")
            return False
