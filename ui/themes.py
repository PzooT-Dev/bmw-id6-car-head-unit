# -*- coding: utf-8 -*-

"""
Theme definitions for the BMW iD6-style UI
"""

from kivy.utils import get_color_from_hex

# Define the BMW iD6 color scheme
class BMWID6Theme:
    """
    Theme class for BMW iD6-style UI
    Contains color definitions and styling helpers
    """
    
    # Main colors
    PRIMARY = get_color_from_hex('#1c69d4')  # BMW blue
    SECONDARY = get_color_from_hex('#666666')
    BACKGROUND = get_color_from_hex('#000000')
    PANEL_BACKGROUND = get_color_from_hex('#1a1a1a')
    TEXT_PRIMARY = get_color_from_hex('#ffffff')
    TEXT_SECONDARY = get_color_from_hex('#cccccc')
    TEXT_DISABLED = get_color_from_hex('#555555')
    
    # Accent colors
    ACCENT_RED = get_color_from_hex('#ff0000')
    ACCENT_GREEN = get_color_from_hex('#00ff00')
    ACCENT_YELLOW = get_color_from_hex('#ffcc00')
    
    # Night mode colors (slightly dimmer)
    NIGHT_PRIMARY = get_color_from_hex('#0a3b77')
    NIGHT_BACKGROUND = get_color_from_hex('#000000')
    NIGHT_PANEL_BACKGROUND = get_color_from_hex('#0a0a0a')
    NIGHT_TEXT_PRIMARY = get_color_from_hex('#bbbbbb')
    NIGHT_TEXT_SECONDARY = get_color_from_hex('#888888')
    
    # Font sizes
    FONT_SIZE_SMALL = 14
    FONT_SIZE_MEDIUM = 18
    FONT_SIZE_LARGE = 24
    FONT_SIZE_XLARGE = 36
    
    # Spacing
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 20
    
    # Border radius
    BORDER_RADIUS_SMALL = 5
    BORDER_RADIUS_MEDIUM = 10
    BORDER_RADIUS_LARGE = 15
    
    @staticmethod
    def get_theme(night_mode=False):
        """
        Get theme colors based on day/night mode.
        
        Args:
            night_mode (bool): Whether to use night mode colors
            
        Returns:
            dict: Dictionary of theme colors
        """
        if night_mode:
            return {
                'primary': BMWID6Theme.NIGHT_PRIMARY,
                'background': BMWID6Theme.NIGHT_BACKGROUND,
                'panel_background': BMWID6Theme.NIGHT_PANEL_BACKGROUND,
                'text_primary': BMWID6Theme.NIGHT_TEXT_PRIMARY,
                'text_secondary': BMWID6Theme.NIGHT_TEXT_SECONDARY,
            }
        else:
            return {
                'primary': BMWID6Theme.PRIMARY,
                'background': BMWID6Theme.BACKGROUND,
                'panel_background': BMWID6Theme.PANEL_BACKGROUND,
                'text_primary': BMWID6Theme.TEXT_PRIMARY,
                'text_secondary': BMWID6Theme.TEXT_SECONDARY,
            }
