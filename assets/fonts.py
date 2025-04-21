# -*- coding: utf-8 -*-

"""
Font definitions for the BMW iD6-style UI
Uses Kivy's default fonts as fallbacks
"""

from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
import os
import logging

logger = logging.getLogger(__name__)

# Default fonts to use
DEFAULT_FONT = 'Roboto'
LIGHT_FONT = 'Roboto-Light'
BOLD_FONT = 'Roboto-Bold'

# BMW uses a font similar to 'BMW Type Global Pro'
# We'll use system fonts that are similar in style

def register_fonts():
    """
    Register custom fonts for the application.
    Falls back to default Kivy fonts if custom fonts are not available.
    """
    try:
        # Check for system fonts that resemble BMW's font
        system_font_dirs = [
            '/usr/share/fonts',
            '/usr/local/share/fonts',
            os.path.expanduser('~/.fonts')
        ]
        
        fonts = {
            'normal': {
                'name': 'BMWFont',
                'alternatives': ['Helvetica', 'Arial', 'Liberation Sans', 'DejaVu Sans']
            },
            'light': {
                'name': 'BMWFontLight',
                'alternatives': ['Helvetica Light', 'Arial Light', 'Liberation Sans Light', 'DejaVu Sans Light']
            },
            'bold': {
                'name': 'BMWFontBold',
                'alternatives': ['Helvetica Bold', 'Arial Bold', 'Liberation Sans Bold', 'DejaVu Sans Bold']
            }
        }
        
        fonts_registered = False
        
        # Try to find and register the fonts
        for font_type, font_info in fonts.items():
            for alt_font in font_info['alternatives']:
                found = False
                
                for font_dir in system_font_dirs:
                    # Look for TTF files matching the font name
                    if os.path.exists(font_dir):
                        for root, dirs, files in os.walk(font_dir):
                            for file in files:
                                if file.lower().startswith(alt_font.lower().replace(' ', '')) and file.lower().endswith('.ttf'):
                                    font_path = os.path.join(root, file)
                                    try:
                                        LabelBase.register(font_info['name'], font_path)
                                        found = True
                                        fonts_registered = True
                                        logger.info(f"Registered font {font_info['name']} using {font_path}")
                                        break
                                    except Exception as e:
                                        logger.warning(f"Failed to register font {font_path}: {e}")
                            if found:
                                break
                    if found:
                        break
                if found:
                    break
        
        # If no fonts were registered, log a warning
        if not fonts_registered:
            logger.warning("Could not register custom fonts, using Kivy defaults")
        
        return True
    except Exception as e:
        logger.error(f"Error registering fonts: {e}")
        return False

# Call this function when initializing the app
# register_fonts()
