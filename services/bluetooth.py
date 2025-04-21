"""
Bluetooth Service Module
Handles Bluetooth connectivity and phone features
"""

import time
import threading
import logging
import random
from enum import Enum

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BluetoothDeviceType(Enum):
    """Types of Bluetooth devices."""
    PHONE = 1
    AUDIO = 2
    OTHER = 3

class CallStatus(Enum):
    """Call status enumeration."""
    IDLE = 1
    INCOMING = 2
    OUTGOING = 3
    ACTIVE = 4
    HELD = 5
    MISSED = 6

class BluetoothService:
    """
    Service for handling Bluetooth connectivity and phone features.
    Simulates Bluetooth functionality for development.
    """
    
    def __init__(self):
        """Initialize the Bluetooth service."""
        self.connected = False
        self.paired_devices = {}  # device_id -> device_info dictionary
        self.active_device = None
        self.call_status = CallStatus.IDLE
        self.current_call = None
        self.call_history = []
        self.contacts = []
        self.running = False
        self.thread = None
        self._load_sample_data()
        logger.info("Bluetooth service initialized")
    
    def start(self):
        """Start the Bluetooth service."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._bluetooth_thread)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Bluetooth service started")
        return True
    
    def stop(self):
        """Stop the Bluetooth service."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
            self.thread = None
        logger.info("Bluetooth service stopped")
    
    def get_status(self):
        """
        Get the current Bluetooth status.
        
        Returns:
            dict: Dictionary containing Bluetooth status information
        """
        return {
            "connected": self.connected,
            "device_name": self.active_device.get("name") if self.active_device else None,
            "device_type": self.active_device.get("type").name if self.active_device and self.active_device.get("type") else None,
            "battery_level": self.active_device.get("battery") if self.active_device else None,
            "signal_strength": self.active_device.get("signal") if self.active_device else None,
            "call_status": self.call_status.name,
            "current_call": self.current_call
        }
    
    def get_paired_devices(self):
        """
        Get a list of paired devices.
        
        Returns:
            list: List of paired devices
        """
        return list(self.paired_devices.values())
    
    def connect(self, device_id=None):
        """
        Connect to a specific device or the most recently connected device.
        
        Args:
            device_id (str, optional): Device ID to connect to. If None, connects to the most recent device.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if device_id and device_id in self.paired_devices:
            self.active_device = self.paired_devices[device_id]
        elif not device_id and self.paired_devices:
            # Connect to most recently connected device
            recent_devices = sorted(self.paired_devices.values(), key=lambda d: d.get("last_connected", 0), reverse=True)
            self.active_device = recent_devices[0]
        else:
            return False
        
        self.connected = True
        self.active_device["last_connected"] = time.time()
        logger.info(f"Connected to {self.active_device['name']}")
        return True
    
    def disconnect(self):
        """
        Disconnect from the current device.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            return False
        
        # Store name for logging before resetting
        device_name = self.active_device.get("name", "Unknown device")
        self.connected = False
        logger.info(f"Disconnected from {device_name}")
        self.active_device = None
        return True
    
    def get_call_history(self):
        """
        Get call history.
        
        Returns:
            list: List of call history entries
        """
        return self.call_history
    
    def get_contacts(self):
        """
        Get contacts list.
        
        Returns:
            list: List of contacts
        """
        return self.contacts
    
    def make_call(self, number=None, contact_id=None):
        """
        Make a phone call.
        
        Args:
            number (str, optional): Phone number to call
            contact_id (str, optional): Contact ID to call
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected or self.call_status != CallStatus.IDLE:
            return False
        
        self.call_status = CallStatus.OUTGOING
        
        # Find contact name if available
        contact_name = None
        if contact_id:
            for contact in self.contacts:
                if contact["id"] == contact_id:
                    number = contact["number"]
                    contact_name = contact["name"]
                    break
        
        self.current_call = {
            "number": number,
            "name": contact_name,
            "start_time": time.time(),
            "duration": 0
        }
        
        logger.info(f"Making call to {contact_name or number}")
        
        # Simulate call connection
        threading.Timer(2.0, self._connect_call).start()
        return True
    
    def _connect_call(self):
        """Simulate connecting a call."""
        if self.call_status == CallStatus.OUTGOING:
            self.call_status = CallStatus.ACTIVE
            logger.info("Call connected")
    
    def answer_call(self):
        """
        Answer an incoming call.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected or self.call_status != CallStatus.INCOMING or not self.current_call:
            return False
        
        self.call_status = CallStatus.ACTIVE
        self.current_call["start_time"] = time.time()
        caller = self.current_call.get('name') or self.current_call.get('number', 'Unknown')
        logger.info(f"Answered call from {caller}")
        return True
    
    def end_call(self):
        """
        End the current call.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected or (self.call_status != CallStatus.ACTIVE and 
                                 self.call_status != CallStatus.OUTGOING and
                                 self.call_status != CallStatus.INCOMING):
            return False
        
        # Get caller info for logging before we clear current_call
        caller_info = "Unknown caller"
        if self.current_call:
            caller_info = self.current_call.get('name') or self.current_call.get('number', 'Unknown')
            
            # Add to call history
            self.current_call["end_time"] = time.time()
            if self.call_status == CallStatus.ACTIVE:
                self.current_call["duration"] = self.current_call["end_time"] - self.current_call["start_time"]
            
            # Record call type
            if self.call_status == CallStatus.INCOMING:
                call_type = "missed"
            elif self.call_status == CallStatus.OUTGOING:
                call_type = "outgoing"
            else:
                call_type = "incoming"
            
            self.current_call["type"] = call_type
            self.call_history.insert(0, self.current_call)  # Add to beginning of list
            
            # Keep history to a reasonable size
            if len(self.call_history) > 50:
                self.call_history = self.call_history[:50]
        
        logger.info(f"Ended call with {caller_info}")
        self.call_status = CallStatus.IDLE
        self.current_call = None
        return True
    
    def _bluetooth_thread(self):
        """Thread function to handle background Bluetooth tasks."""
        while self.running:
            # Simulate occasional incoming call
            if self.connected and self.call_status == CallStatus.IDLE and random.random() < 0.0005:  # Very low probability
                self._simulate_incoming_call()
            
            # Update battery level and signal strength of connected device
            if self.connected and self.active_device:
                # Slowly drain battery
                if random.random() < 0.1:  # 10% chance each iteration
                    self.active_device["battery"] = max(0, self.active_device["battery"] - 1)
                
                # Fluctuate signal strength
                if random.random() < 0.2:  # 20% chance each iteration
                    delta = random.choice([-1, 1])
                    self.active_device["signal"] = max(0, min(5, self.active_device["signal"] + delta))
            
            time.sleep(5)  # Sleep to prevent CPU usage
    
    def _simulate_incoming_call(self):
        """Simulate an incoming call."""
        if not self.contacts:
            return
        
        # Choose a random contact
        contact = random.choice(self.contacts)
        
        self.call_status = CallStatus.INCOMING
        self.current_call = {
            "number": contact["number"],
            "name": contact["name"],
            "start_time": time.time(),
            "duration": 0
        }
        
        logger.info(f"Incoming call from {contact['name']}")
        
        # Auto-miss the call after 15 seconds if not answered
        threading.Timer(15.0, self._auto_miss_call).start()
    
    def _auto_miss_call(self):
        """Automatically mark a call as missed if not answered."""
        if self.call_status == CallStatus.INCOMING:
            self.call_status = CallStatus.MISSED
            
            # Get caller info for logging before we clear current_call
            caller_info = "Unknown caller"
            
            # Add to call history as missed
            if self.current_call:
                caller_info = self.current_call.get('name') or self.current_call.get('number', 'Unknown')
                self.current_call["type"] = "missed"
                self.current_call["end_time"] = time.time()
                self.call_history.insert(0, self.current_call)
                
                # Keep history to a reasonable size
                if len(self.call_history) > 50:
                    self.call_history = self.call_history[:50]
            
            logger.info(f"Missed call from {caller_info}")
            self.current_call = None
            self.call_status = CallStatus.IDLE
    
    def _load_sample_data(self):
        """Load sample data for development and testing."""
        # Sample paired devices
        self.paired_devices = {
            "device1": {
                "id": "device1",
                "name": "Pixel 7 Pro",
                "type": BluetoothDeviceType.PHONE,
                "battery": 85,
                "signal": 4,
                "last_connected": time.time()
            },
            "device2": {
                "id": "device2",
                "name": "Sony WH-1000XM4",
                "type": BluetoothDeviceType.AUDIO,
                "battery": 60,
                "last_connected": time.time() - 86400  # 1 day ago
            },
            "device3": {
                "id": "device3",
                "name": "iPhone 14",
                "type": BluetoothDeviceType.PHONE,
                "battery": 75,
                "signal": 3,
                "last_connected": time.time() - 172800  # 2 days ago
            }
        }
        
        # Sample contacts
        self.contacts = [
            {"id": "contact1", "name": "John Smith", "number": "+1 (555) 123-4567"},
            {"id": "contact2", "name": "Jane Doe", "number": "+1 (555) 987-6543"},
            {"id": "contact3", "name": "Alice Johnson", "number": "+1 (555) 555-5555"},
            {"id": "contact4", "name": "Bob Williams", "number": "+1 (555) 444-3333"},
            {"id": "contact5", "name": "Chris Taylor", "number": "+1 (555) 222-1111"}
        ]
        
        # Sample call history
        self.call_history = [
            {
                "number": "+1 (555) 123-4567",
                "name": "John Smith",
                "start_time": time.time() - 3600,  # 1 hour ago
                "end_time": time.time() - 3500,
                "duration": 100,
                "type": "outgoing"
            },
            {
                "number": "+1 (555) 987-6543",
                "name": "Jane Doe",
                "start_time": time.time() - 7200,  # 2 hours ago
                "end_time": time.time() - 7170,
                "duration": 30,
                "type": "incoming"
            },
            {
                "number": "+1 (555) 333-2222",
                "name": "Unknown",
                "start_time": time.time() - 43200,  # 12 hours ago
                "end_time": time.time() - 43200,
                "duration": 0,
                "type": "missed"
            }
        ]