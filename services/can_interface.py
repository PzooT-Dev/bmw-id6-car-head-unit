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
            
        logger.info(f"Starting CAN interface in simulation mode")
        
        try:
            # For testing/simulation, we'll run in simulation mode
            # without actual CAN hardware
            self.running = True
            self.connected = True
            self.last_received = time.time()
            
            # Set initial simulated vehicle data
            self.vehicle_data = {
                'speed': 45,
                'rpm': 1500,
                'fuel_level': 75,
                'coolant_temp': 90,
                'outside_temp': 22,
                'engine_on': True
            }
            
            # Start the simulation thread
            self.thread = threading.Thread(target=self._simulate_can_messages)
            self.thread.daemon = True
            self.thread.start()
            
            logger.info("CAN interface simulation started successfully")
            
        except Exception as e:
            logger.error(f"Error starting CAN interface simulation: {e}")
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
                
    def _simulate_can_messages(self):
        """Thread function to simulate CAN messages for testing."""
        import random
        
        while self.running:
            try:
                # Update the timestamp for connection status
                self.last_received = time.time()
                
                # Simulate speed changes (with some randomness)
                self.vehicle_data['speed'] += random.randint(-3, 3)
                self.vehicle_data['speed'] = max(0, min(120, self.vehicle_data['speed']))
                
                # Simulate RPM changes based on speed
                target_rpm = self.vehicle_data['speed'] * 30 + 800  # Simplified RPM calculation
                self.vehicle_data['rpm'] += (target_rpm - self.vehicle_data['rpm']) // 10
                self.vehicle_data['rpm'] = max(800, min(6000, self.vehicle_data['rpm']))
                
                # Gradually decrease fuel level
                if random.random() < 0.01:  # 1% chance per iteration
                    self.vehicle_data['fuel_level'] -= 0.1
                    self.vehicle_data['fuel_level'] = max(0, self.vehicle_data['fuel_level'])
                
                # Simulate coolant temperature fluctuations
                self.vehicle_data['coolant_temp'] += random.randint(-1, 1)
                self.vehicle_data['coolant_temp'] = max(80, min(105, self.vehicle_data['coolant_temp']))
                
                # Simulate outside temperature changes
                if random.random() < 0.05:  # 5% chance per iteration
                    self.vehicle_data['outside_temp'] += random.uniform(-0.1, 0.1)
                    self.vehicle_data['outside_temp'] = round(self.vehicle_data['outside_temp'], 1)
                
                # Sleep to simulate update rate
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error in CAN simulation: {e}")
                time.sleep(1.0)
    
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
            # In simulation mode, just log the message
            logger.info(f"Simulation: CAN message sent with ID: 0x{arb_id:x}, data: {data.hex() if data else 'None'}")
            
            # In real mode with hardware, this would be:
            # message = can.Message(
            #     arbitration_id=arb_id,
            #     data=data,
            #     is_extended_id=False
            # )
            # self.bus.send(message)
            
            return True
        except Exception as e:
            logger.error(f"Error sending CAN message: {e}")
            return False
