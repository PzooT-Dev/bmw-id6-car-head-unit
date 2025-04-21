# -*- coding: utf-8 -*-

"""
Media Player Screen - For radio and audio playback
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
import logging

logger = logging.getLogger(__name__)

class MediaPlayerScreen(Screen):
    """
    Media player screen for radio and audio functionality.
    """
    # Radio properties
    current_station = StringProperty('No Station')
    current_frequency = StringProperty('---.-- MHz')
    signal_strength = NumericProperty(0)  # 0-100%
    is_dab_mode = BooleanProperty(True)  # DAB mode by default
    rds_text = StringProperty('Radio Data System Information')
    
    # Audio properties
    is_playing = BooleanProperty(False)
    current_volume = NumericProperty(50)  # 0-100%
    
    def __init__(self, **kwargs):
        super(MediaPlayerScreen, self).__init__(**kwargs)
        self._radio_service = None
        self._audio_manager = None
        Clock.schedule_once(self._get_services, 2)
    
    def _get_services(self, dt):
        """Get references to required services."""
        app = self.manager.parent.app if self.manager else None
        if app:
            self._radio_service = app.radio_service
            self._audio_manager = app.audio_manager
            self._update_radio_display()
            Clock.schedule_interval(self._update_radio_display, 1)  # Update radio display every second
    
    def _update_radio_display(self, dt=None):
        """Update radio display with current information."""
        if not self._radio_service:
            return
            
        try:
            # Get current radio information
            radio_info = self._radio_service.get_current_info()
            
            if radio_info:
                self.current_station = radio_info.get('station_name', 'Unknown')
                self.current_frequency = radio_info.get('frequency', '---.-- MHz')
                self.signal_strength = radio_info.get('signal_strength', 0)
                self.rds_text = radio_info.get('rds_text', '')
        except Exception as e:
            logger.error(f"Error updating radio display: {e}")
    
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        if not self._audio_manager:
            return
            
        try:
            if self.is_playing:
                self._audio_manager.pause()
            else:
                self._audio_manager.play()
            
            self.is_playing = not self.is_playing
        except Exception as e:
            logger.error(f"Error toggling play/pause: {e}")
    
    def toggle_radio_mode(self):
        """Switch between DAB and FM radio modes."""
        if not self._radio_service:
            return
            
        try:
            self.is_dab_mode = not self.is_dab_mode
            mode = 'DAB' if self.is_dab_mode else 'FM'
            self._radio_service.set_mode(mode)
            self._update_radio_display()
        except Exception as e:
            logger.error(f"Error toggling radio mode: {e}")
    
    def seek_next_station(self):
        """Seek to the next available station."""
        if not self._radio_service:
            return
            
        try:
            self._radio_service.seek_next()
            self._update_radio_display()
        except Exception as e:
            logger.error(f"Error seeking next station: {e}")
    
    def seek_prev_station(self):
        """Seek to the previous available station."""
        if not self._radio_service:
            return
            
        try:
            self._radio_service.seek_prev()
            self._update_radio_display()
        except Exception as e:
            logger.error(f"Error seeking previous station: {e}")
    
    def adjust_volume(self, value):
        """
        Adjust the volume.
        
        Args:
            value (int): New volume level (0-100)
        """
        if not self._audio_manager:
            return
            
        try:
            self.current_volume = max(0, min(100, value))
            self._audio_manager.set_volume(self.current_volume / 100.0)  # Convert to 0-1 range
        except Exception as e:
            logger.error(f"Error adjusting volume: {e}")
