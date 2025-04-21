#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple test app to verify Kivy functionality
"""

import os
import kivy
from kivy.app import App
from kivy.uix.label import Label

# Disable multitouch emulation to avoid some issues
os.environ['KIVY_NO_ARGS'] = '1'
# Use SDL2 as the window provider and fallback to software rendering if necessary
os.environ['KIVY_WINDOW'] = 'sdl2'
# Disable high DPI scaling which can cause issues
os.environ['KIVY_DPI'] = '96'
os.environ['KIVY_METRICS_DENSITY'] = '1'

# Force headless rendering mode that works for cloud environment 
os.environ['KIVY_GL_BACKEND'] = 'mock'

class SimpleTestApp(App):
    def build(self):
        return Label(text='Kivy is working!')

if __name__ == '__main__':
    SimpleTestApp().run()