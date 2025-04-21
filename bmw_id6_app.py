# -*- coding: utf-8 -*-

"""
BMW iD6-style App - Main Application Class
"""

import os
import logging
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock

# Import our UI screens
from ui.dashboard import DashboardScreen
from ui.media_player import MediaPlayerScreen
from ui.navigation import NavigationScreen
from ui.settings import SettingsScreen

# Import our services
from services.can_interface import CANInterface
from services.radio import RadioService
from services.audio import AudioManager

logger = logging.getLogger(__name__)

class BMWID6App(App):
    """
    Main application class for the BMW iD6-style Raspberry Pi car head unit.
    """
    
    def __init__(self, **kwargs):
        super(BMWID6App, self).__init__(**kwargs)
        
        # Set app title
        self.title = 'BMW iD6 Head Unit'
        
        # Services
        self.can_interface = None
        self.radio_service = None
        self.audio_manager = None
        
        # UI components
        self.screen_manager = None
        
        # Configure window for simulation environment
        Window.size = (800, 480)  # Common Raspberry Pi touchscreen resolution
        Window.clearcolor = (0, 0, 0, 1)  # Black background
        Window.show_cursor = True  # Show cursor for desktop testing
        
    def build(self):
        """Build and return the app's UI root widget."""
        # Load KV file
        Builder.load_file('assets/bmw_id6.kv')
        
        # Initialize screen manager with transition
        self.screen_manager = ScreenManager(transition=FadeTransition())
        
        # Add screens
        self.screen_manager.add_widget(DashboardScreen(name='dashboard'))
        self.screen_manager.add_widget(MediaPlayerScreen(name='media'))
        self.screen_manager.add_widget(NavigationScreen(name='navigation'))
        self.screen_manager.add_widget(SettingsScreen(name='settings'))
        
        # Initialize services with a slight delay to ensure UI is ready
        Clock.schedule_once(self._init_services, 1)
        
        return self.screen_manager
    
    def _init_services(self, dt):
        """Initialize services needed by the app."""
        try:
            # Initialize CAN bus interface
            self.can_interface = CANInterface()
            self.can_interface.start()
            
            # Initialize radio service
            self.radio_service = RadioService()
            
            # Initialize audio manager
            self.audio_manager = AudioManager()
            
            # Start vehicle data updates
            Clock.schedule_interval(self._update_vehicle_data, 0.5)  # Update every 500ms
            
        except Exception as e:
            logger.exception(f"Error initializing services: {e}")
    
    def _update_vehicle_data(self, dt):
        """Update vehicle data from CAN bus."""
        if self.can_interface and self.can_interface.is_connected():
            try:
                # Get vehicle data
                vehicle_data = self.can_interface.get_vehicle_data()
                
                # Update dashboard if it's the current screen
                if self.screen_manager.current == 'dashboard':
                    dashboard = self.screen_manager.get_screen('dashboard')
                    dashboard.update_vehicle_data(vehicle_data)
            except Exception as e:
                logger.error(f"Error updating vehicle data: {e}")
    
    def on_stop(self):
        """Clean up when the app is closing."""
        logger.info("Application stopping, cleaning up resources...")
        
        # Cleanup CAN interface
        if self.can_interface:
            self.can_interface.stop()
        
        # Cleanup radio service
        if self.radio_service:
            self.radio_service.stop()
        
        # Cleanup audio manager
        if self.audio_manager:
            self.audio_manager.shutdown()
