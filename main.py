#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Raspberry Pi BMW iD6-style Car Head Unit
Main entry point for the application.
"""

import os
import sys
import logging
from kivy.resources import resource_add_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    # Add the current directory to the path so we can run the app from any location
    current_dir = os.path.dirname(os.path.abspath(__file__))
    resource_add_path(current_dir)
    
    # Some environment setup for Raspberry Pi
    os.environ['KIVY_GL_BACKEND'] = 'gl'
    os.environ['KIVY_WINDOW'] = 'egl_rpi'
    
    try:
        from bmw_id6_app import BMWID6App
        app = BMWID6App()
        app.run()
    except Exception as e:
        logger.exception(f"Failed to start application: {e}")
        sys.exit(1)
