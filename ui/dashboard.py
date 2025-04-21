# -*- coding: utf-8 -*-

"""
Dashboard Screen - Main driving view showing vehicle data
"""

from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import logging

logger = logging.getLogger(__name__)

class DigitalGauge(BoxLayout):
    """A digital gauge widget for displaying numeric values with a label."""
    value = NumericProperty(0)
    label_text = StringProperty('')
    unit = StringProperty('')
    
    def __init__(self, **kwargs):
        super(DigitalGauge, self).__init__(**kwargs)
        self.orientation = 'vertical'

class DashboardScreen(Screen):
    """
    The main dashboard screen showing vehicle information from CAN bus
    """
    # Vehicle data properties
    speed = NumericProperty(0)
    rpm = NumericProperty(0)
    fuel_level = NumericProperty(0)
    coolant_temp = NumericProperty(0)
    outside_temp = NumericProperty(20)  # Default 20°C
    time = StringProperty('')
    
    # UI elements
    speed_gauge = ObjectProperty(None)
    rpm_gauge = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(DashboardScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self._update_time, 1)  # Update clock every second
    
    def _update_time(self, dt):
        """Update the displayed time."""
        from datetime import datetime
        self.time = datetime.now().strftime('%H:%M')
    
    def update_vehicle_data(self, data):
        """
        Update the dashboard with new vehicle data.
        
        Args:
            data (dict): Dictionary containing vehicle data from CAN bus.
                Expected keys: speed, rpm, fuel_level, coolant_temp, outside_temp
        """
        try:
            # Update the properties with new data
            if 'speed' in data:
                self.speed = data['speed']
            
            if 'rpm' in data:
                self.rpm = data['rpm']
            
            if 'fuel_level' in data:
                self.fuel_level = data['fuel_level']
            
            if 'coolant_temp' in data:
                self.coolant_temp = data['coolant_temp']
            
            if 'outside_temp' in data:
                self.outside_temp = data['outside_temp']
                
            # Additional CAN data can be handled here
                
        except Exception as e:
            logger.error(f"Error updating dashboard data: {e}")
    
    def on_leave(self):
        """Called when leaving this screen."""
        pass
