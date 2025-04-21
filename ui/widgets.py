# -*- coding: utf-8 -*-

"""
Custom widgets used throughout the BMW iD6 UI
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.uix.slider import Slider
import math

class BMWID6Button(Button):
    """
    Custom button styled after BMW iD6 interface buttons.
    """
    background_color_normal = ListProperty([0.2, 0.2, 0.2, 1])
    background_color_down = ListProperty([0.4, 0.4, 0.4, 1])
    border_radius = NumericProperty(10)
    
    def __init__(self, **kwargs):
        super(BMWID6Button, self).__init__(**kwargs)
        self.background_color = [0, 0, 0, 0]  # Make the standard background transparent
        
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color_normal if not self.state == 'down' else self.background_color_down)
            Rectangle(pos=self.pos, size=self.size, radius=[self.border_radius])

class BMWID6Gauge(BoxLayout):
    """
    Circular gauge widget styled after BMW iD6 gauges.
    Used for RPM, Speed, etc.
    """
    value = NumericProperty(0)
    min_value = NumericProperty(0)
    max_value = NumericProperty(100)
    title = StringProperty('')
    unit = StringProperty('')
    gauge_color = ListProperty([0.8, 0.8, 0.8, 1])
    
    def __init__(self, **kwargs):
        super(BMWID6Gauge, self).__init__(**kwargs)
        self.bind(value=self.update_gauge,
                 size=self.update_gauge,
                 pos=self.update_gauge)
    
    def update_gauge(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Draw background circle
            Color(0.2, 0.2, 0.2, 1)
            Ellipse(pos=(self.pos[0] + dp(10), self.pos[1] + dp(10)), 
                   size=(self.width - dp(20), self.height - dp(20)))
            
            # Draw gauge arc
            Color(*self.gauge_color)
            percentage = (self.value - self.min_value) / (self.max_value - self.min_value)
            angle = 240 * percentage  # Gauge spans 240 degrees
            Line(circle=(self.center_x, self.center_y, min(self.width, self.height) / 2 - dp(15), 
                        150, 150 + angle), width=dp(5))

class BMWID6Slider(Slider):
    """
    Custom slider styled after BMW iD6 interface.
    """
    track_color = ListProperty([0.2, 0.2, 0.2, 1])
    progress_color = ListProperty([0.4, 0.6, 0.8, 1])
    
    def __init__(self, **kwargs):
        super(BMWID6Slider, self).__init__(**kwargs)
        self.cursor_size = (dp(20), dp(20))
        
    def on_size(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Draw track
            Color(*self.track_color)
            Rectangle(pos=(self.x, self.center_y - dp(2)), 
                     size=(self.width, dp(4)))
            
            # Draw progress
            Color(*self.progress_color)
            # Calculate progress width
            progress_width = self.width * (self.value - self.min) / (self.max - self.min)
            Rectangle(pos=(self.x, self.center_y - dp(2)), 
                     size=(progress_width, dp(4)))

class StatusBar(BoxLayout):
    """
    Status bar widget for the top of the screen.
    Shows time, connectivity status, etc.
    """
    time = StringProperty('')
    
    def __init__(self, **kwargs):
        super(StatusBar, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        
        # Time label
        self.time_label = Label(text=self.time, size_hint_x=None, width=dp(100))
        self.add_widget(self.time_label)
        
        # Bind properties
        self.bind(time=self._update_time)
    
    def _update_time(self, instance, value):
        self.time_label.text = value

class MainMenuBar(BoxLayout):
    """
    Main menu bar for navigation between screens.
    """
    active_screen = StringProperty('dashboard')
    
    def __init__(self, **kwargs):
        super(MainMenuBar, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(80)
        
        # Create menu buttons
        self.dashboard_btn = BMWID6Button(text='Dashboard', on_press=self.switch_screen)
        self.dashboard_btn.screen = 'dashboard'
        
        self.media_btn = BMWID6Button(text='Media', on_press=self.switch_screen)
        self.media_btn.screen = 'media'
        
        self.nav_btn = BMWID6Button(text='Navigation', on_press=self.switch_screen)
        self.nav_btn.screen = 'navigation'
        
        self.settings_btn = BMWID6Button(text='Settings', on_press=self.switch_screen)
        self.settings_btn.screen = 'settings'
        
        # Add buttons to layout
        self.add_widget(self.dashboard_btn)
        self.add_widget(self.media_btn)
        self.add_widget(self.nav_btn)
        self.add_widget(self.settings_btn)
        
        # Bind properties
        self.bind(active_screen=self._update_buttons)
    
    def switch_screen(self, button):
        """Switch to the selected screen."""
        app = self.parent.parent.app if self.parent else None
        if app and app.screen_manager:
            app.screen_manager.current = button.screen
            self.active_screen = button.screen
    
    def _update_buttons(self, instance, value):
        """Update button states based on active screen."""
        for child in self.children:
            if hasattr(child, 'screen'):
                child.state = 'down' if child.screen == value else 'normal'

class VehicleDataWidget(BoxLayout):
    """
    Widget to display vehicle data values.
    """
    label = StringProperty('')
    value = StringProperty('')
    unit = StringProperty('')
    
    def __init__(self, **kwargs):
        super(VehicleDataWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create labels
        self.label_widget = Label(text=self.label, font_size=dp(14))
        self.value_widget = Label(text=self.value, font_size=dp(24))
        self.unit_widget = Label(text=self.unit, font_size=dp(12))
        
        # Add to layout
        self.add_widget(self.label_widget)
        self.add_widget(self.value_widget)
        self.add_widget(self.unit_widget)
        
        # Bind properties
        self.bind(label=self._update_label,
                 value=self._update_value,
                 unit=self._update_unit)
    
    def _update_label(self, instance, value):
        self.label_widget.text = value
    
    def _update_value(self, instance, value):
        self.value_widget.text = value
    
    def _update_unit(self, instance, value):
        self.unit_widget.text = value
