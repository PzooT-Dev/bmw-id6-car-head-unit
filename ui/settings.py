# -*- coding: utf-8 -*-

"""
Settings Screen - System settings and configuration
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
import logging
import os

logger = logging.getLogger(__name__)

class SettingsScreen(Screen):
    """
    Settings screen for system configuration.
    """
    brightness = NumericProperty(80)  # 0-100%
    audio_balance = NumericProperty(50)  # 0-100% (left to right)
    system_version = StringProperty('1.0.0')
    can_status = StringProperty('Disconnected')
    radio_status = StringProperty('Disconnected')
    night_mode = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._init_settings, 1)
        Clock.schedule_interval(self._update_status, 5)  # Update status every 5 seconds
    
    def _init_settings(self, dt):
        """Initialize settings from storage or defaults."""
        # This would normally load settings from a config file
        # For now, we'll use default values
        self.brightness = 80
        self.audio_balance = 50
        self.system_version = '1.0.0'
        
        # Get app reference for service status
        app = self.manager.parent.app if self.manager else None
        if app:
            # Update status based on services
            if app.can_interface:
                self.can_status = 'Connected' if app.can_interface.is_connected() else 'Disconnected'
            
            if app.radio_service:
                self.radio_status = 'Active' if app.radio_service.is_active() else 'Inactive'
    
    def _update_status(self, dt):
        """Update status information periodically."""
        # Get app reference for service status
        app = self.manager.parent.app if self.manager else None
        if app:
            # Update status based on services
            if app.can_interface:
                self.can_status = 'Connected' if app.can_interface.is_connected() else 'Disconnected'
            
            if app.radio_service:
                self.radio_status = 'Active' if app.radio_service.is_active() else 'Inactive'
    
    def adjust_brightness(self, value):
        """
        Adjust the screen brightness.
        
        Args:
            value (int): New brightness level (0-100)
        """
        self.brightness = max(0, min(100, value))
        
        # On Raspberry Pi, we could set the actual screen brightness
        # This is a simplified version for development
        try:
            # Check if running on Raspberry Pi and brightness control is available
            if os.path.exists('/sys/class/backlight/rpi_backlight/brightness'):
                # Convert 0-100 scale to 0-255 for Raspberry Pi
                rpi_brightness = int(self.brightness * 2.55)
                with open('/sys/class/backlight/rpi_backlight/brightness', 'w') as f:
                    f.write(str(rpi_brightness))
        except Exception as e:
            logger.error(f"Error adjusting brightness: {e}")
    
    def adjust_audio_balance(self, value):
        """
        Adjust the audio balance between left and right channels.
        
        Args:
            value (int): New balance level (0-100, where 0=left, 50=center, 100=right)
        """
        self.audio_balance = max(0, min(100, value))
        
        # Get app reference to adjust audio
        app = self.manager.parent.app if self.manager else None
        if app and app.audio_manager:
            try:
                # Convert 0-100 to -1.0 to 1.0 range for audio balance
                # 0 -> -1.0 (full left), 50 -> 0.0 (center), 100 -> 1.0 (full right)
                balance = (self.audio_balance / 50.0) - 1.0
                app.audio_manager.set_balance(balance)
            except Exception as e:
                logger.error(f"Error adjusting audio balance: {e}")
    
    def toggle_night_mode(self):
        """Toggle between day and night modes."""
        self.night_mode = not self.night_mode
        
        # Apply night mode changes to the app theme
        app = self.manager.parent.app if self.manager else None
        if app:
            # This would apply different theme settings based on night mode
            # For now, we'll just log the change
            logger.info(f"Night mode: {self.night_mode}")
    
    def restart_services(self):
        """Restart all services."""
        app = self.manager.parent.app if self.manager else None
        if app:
            try:
                # Restart CAN interface
                if app.can_interface:
                    app.can_interface.stop()
                    app.can_interface.start()
                
                # Restart radio service
                if app.radio_service:
                    app.radio_service.stop()
                    app.radio_service.start()
                
                # Restart audio manager
                if app.audio_manager:
                    app.audio_manager.restart()
                
                # Update status
                self._update_status(None)
            except Exception as e:
                logger.error(f"Error restarting services: {e}")
