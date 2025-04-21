# -*- coding: utf-8 -*-

"""
Radio Service Module
Handles DAB and FM radio reception with RDS
"""

import os
import time
import threading
import logging
import subprocess
from enum import Enum

logger = logging.getLogger(__name__)

class RadioMode(Enum):
    """Radio mode enumeration."""
    FM = 1
    DAB = 2

class RadioService:
    """
    Service for handling DAB and FM radio reception with RDS.
    Uses RTL-SDR for radio reception.
    """
    
    def __init__(self):
        """Initialize the radio service."""
        self.mode = RadioMode.DAB
        self.frequency = 95.5  # Default FM frequency (MHz)
        self.current_station = "No Station"
        self.rds_text = ""
        self.signal_strength = 0
        self.running = False
        self.active = False
        self.thread = None
        self.process = None
        self.station_list = []
        self.current_station_index = 0
        
    def start(self):
        """Start the radio service."""
        if self.running:
            logger.warning("Radio service already running")
            return
            
        logger.info("Starting radio service in simulation mode")
        
        try:
            self.running = True
            self.active = True
            
            # For simulation mode, set up some initial values
            if self.mode == RadioMode.FM:
                self.current_station = "Simulation Radio 1"
                self.frequency = 98.8
                self.rds_text = "Welcome to Simulation FM Radio"
            else:
                self.current_station = "DAB Simulation 1"
                self.rds_text = "Digital Radio Simulation"
                
            self.signal_strength = 85  # Simulate good signal
            
            # Start the radio simulation thread
            self.thread = threading.Thread(target=self._radio_thread)
            self.thread.daemon = True
            self.thread.start()
            
            logger.info("Radio service simulation started successfully")
            
        except Exception as e:
            logger.error(f"Error starting radio service: {e}")
            self.active = False
    
    def stop(self):
        """Stop the radio service."""
        if not self.running:
            return
            
        logger.info("Stopping radio service")
        
        self.running = False
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2.0)
            except Exception as e:
                logger.error(f"Error terminating radio process: {e}")
                
        if self.thread:
            self.thread.join(timeout=1.0)
                
        self.active = False
        logger.info("Radio service stopped")
    
    def is_active(self):
        """
        Check if the radio service is active.
        
        Returns:
            bool: True if active, False otherwise
        """
        return self.active
    
    def set_mode(self, mode):
        """
        Set the radio mode (FM or DAB).
        
        Args:
            mode (str): 'FM' or 'DAB'
        """
        if mode == 'FM':
            self.mode = RadioMode.FM
        elif mode == 'DAB':
            self.mode = RadioMode.DAB
        else:
            logger.error(f"Invalid radio mode: {mode}")
            return
            
        # Restart radio process with new mode
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2.0)
                self.process = None
            except Exception as e:
                logger.error(f"Error terminating radio process: {e}")
        
        # Scan for stations in the new mode
        self._scan_stations()
    
    def set_frequency(self, frequency):
        """
        Set the FM frequency.
        
        Args:
            frequency (float): FM frequency in MHz (87.5-108.0)
        """
        if self.mode != RadioMode.FM:
            logger.warning("Cannot set frequency in DAB mode")
            return
            
        # Validate frequency range
        if frequency < 87.5 or frequency > 108.0:
            logger.error(f"Invalid FM frequency: {frequency}")
            return
            
        self.frequency = frequency
        
        # Restart radio process with new frequency
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2.0)
                self.process = None
            except Exception as e:
                logger.error(f"Error terminating radio process: {e}")
    
    def seek_next(self):
        """Seek to the next available station."""
        if len(self.station_list) == 0:
            logger.warning("No stations available")
            return
            
        self.current_station_index = (self.current_station_index + 1) % len(self.station_list)
        
        if self.mode == RadioMode.FM:
            self.frequency = self.station_list[self.current_station_index]
            self._start_fm_radio()
        else:
            # For DAB, station_list contains (station_id, station_name) tuples
            station_id, station_name = self.station_list[self.current_station_index]
            self.current_station = station_name
            self._start_dab_radio(station_id)
    
    def seek_prev(self):
        """Seek to the previous available station."""
        if len(self.station_list) == 0:
            logger.warning("No stations available")
            return
            
        self.current_station_index = (self.current_station_index - 1) % len(self.station_list)
        
        if self.mode == RadioMode.FM:
            self.frequency = self.station_list[self.current_station_index]
            self._start_fm_radio()
        else:
            # For DAB, station_list contains (station_id, station_name) tuples
            station_id, station_name = self.station_list[self.current_station_index]
            self.current_station = station_name
            self._start_dab_radio(station_id)
    
    def get_current_info(self):
        """
        Get the current radio information.
        
        Returns:
            dict: Dictionary containing radio information
        """
        mode_str = 'FM' if self.mode == RadioMode.FM else 'DAB'
        
        if self.mode == RadioMode.FM:
            frequency_str = f"{self.frequency:.2f} MHz"
        else:
            frequency_str = "DAB"
            
        return {
            'mode': mode_str,
            'frequency': frequency_str,
            'station_name': self.current_station,
            'rds_text': self.rds_text,
            'signal_strength': self.signal_strength
        }
    
    def _radio_thread(self):
        """Thread function to manage radio processes."""
        try:
            # Initial scan for stations
            self._scan_stations()
            
            # Start radio reception
            if self.mode == RadioMode.FM:
                self._start_fm_radio()
            else:
                if len(self.station_list) > 0:
                    station_id, station_name = self.station_list[0]
                    self._start_dab_radio(station_id)
            
            # Monitor radio process and update info
            while self.running:
                if self.process and self.process.poll() is not None:
                    # Process has exited
                    logger.warning("Radio process has exited unexpectedly")
                    self.process = None
                    
                    # Restart after a delay
                    time.sleep(1.0)
                    if self.mode == RadioMode.FM:
                        self._start_fm_radio()
                    else:
                        if len(self.station_list) > 0:
                            station_id, station_name = self.station_list[self.current_station_index]
                            self._start_dab_radio(station_id)
                
                # Read process output for RDS updates
                if self.process:
                    self._update_radio_info()
                
                time.sleep(0.2)
                
        except Exception as e:
            logger.error(f"Error in radio thread: {e}")
            self.active = False
    
    def _scan_stations(self):
        """Scan for available radio stations."""
        try:
            logger.info(f"Scanning for {'FM' if self.mode == RadioMode.FM else 'DAB'} stations")
            self.station_list = []
            
            if self.mode == RadioMode.FM:
                # Use rtl_fm to scan for FM stations
                # This is a simplified example - real implementation would be more complex
                # Simulated FM stations for demonstration
                self.station_list = [
                    87.9, 88.5, 89.1, 91.3, 93.5, 95.7, 97.9, 99.1, 101.3, 103.5, 105.7, 107.9
                ]
            else:
                # Use rtl_dab to scan for DAB stations
                # This is a simplified example - real implementation would require actual DAB scanning
                # Simulated DAB stations for demonstration
                self.station_list = [
                    ("0x1001", "BBC Radio 1"),
                    ("0x1002", "BBC Radio 2"),
                    ("0x1003", "BBC Radio 3"),
                    ("0x1004", "BBC Radio 4"),
                    ("0x1005", "Classic FM"),
                    ("0x1006", "Heart"),
                    ("0x1007", "Capital")
                ]
            
            logger.info(f"Found {len(self.station_list)} stations")
            
        except Exception as e:
            logger.error(f"Error scanning for stations: {e}")
    
    def _start_fm_radio(self):
        """Start FM radio reception."""
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=2.0)
                self.process = None
            
            # Use rtl_fm to receive FM radio
            # This is a simplified example - real implementation would use actual rtl_fm command
            # For demonstration, we'll simulate the process
            logger.info(f"Starting FM radio at {self.frequency:.2f} MHz")
            
            # In a real implementation, this would be:
            # self.process = subprocess.Popen([
            #     'rtl_fm', '-f', f'{self.frequency}e6', '-M', 'fm', '-s', '200000',
            #     '-r', '48000', '-A', 'fast', '-l', '0', '-E', 'deemp', '|',
            #     'aplay', '-r', '48000', '-f', 'S16_LE', '-t', 'raw', '-c', '1'
            # ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # For demonstration, we'll just update the station info based on frequency
            # In real implementation, this would come from RDS data
            station_names = {
                87.9: "ROCK FM",
                88.5: "CLASSIC HITS",
                89.1: "NEWS 24/7",
                91.3: "SMOOTH JAZZ",
                93.5: "TOP 40",
                95.7: "COUNTRY",
                97.9: "TALK RADIO",
                99.1: "HIP HOP",
                101.3: "CLASSICAL",
                103.5: "ALTERNATIVE",
                105.7: "OLDIES",
                107.9: "POP HITS"
            }
            
            # Find closest frequency in our dictionary
            closest_freq = min(station_names.keys(), key=lambda x: abs(x - self.frequency))
            self.current_station = station_names.get(closest_freq, "Unknown Station")
            self.rds_text = f"You're listening to {self.current_station}"
            
        except Exception as e:
            logger.error(f"Error starting FM radio: {e}")
    
    def _start_dab_radio(self, station_id):
        """
        Start DAB radio reception for a specific station.
        
        Args:
            station_id (str): DAB station ID
        """
        try:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=2.0)
                self.process = None
            
            # Use rtl_dab to receive DAB radio
            # This is a simplified example - real implementation would use actual rtl_dab command
            # For demonstration, we'll simulate the process
            logger.info(f"Starting DAB radio for station ID {station_id}")
            
            # In a real implementation, this would be:
            # self.process = subprocess.Popen([
            #     'rtl_dab', '-c', station_id, '|',
            #     'aplay', '-r', '48000', '-f', 'S16_LE', '-t', 'raw', '-c', '2'
            # ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # For demonstration, find the station name from station_id
            station_name = next((name for sid, name in self.station_list if sid == station_id), "Unknown Station")
            self.current_station = station_name
            self.rds_text = f"DAB: {station_name}"
            
        except Exception as e:
            logger.error(f"Error starting DAB radio: {e}")
    
    def _update_radio_info(self):
        """Update radio information (RDS text, signal strength, etc.)."""
        # In a real implementation, this would parse output from rtl_fm/rtl_dab
        # For demonstration, we'll simulate RDS text updates
        
        # Simulate changing RDS text occasionally
        if self.mode == RadioMode.FM and time.time() % 10 < 0.2:  # Change every ~10 seconds
            rds_texts = [
                f"You're listening to {self.current_station}",
                f"{self.current_station} - Your Music Station",
                "Text us at 12345",
                "Follow us on social media",
                f"{self.current_station} - No commercials"
            ]
            import random
            self.rds_text = random.choice(rds_texts)
        
        # Simulate signal strength fluctuations
        import random
        self.signal_strength = min(100, max(0, self.signal_strength + random.randint(-5, 5)))
