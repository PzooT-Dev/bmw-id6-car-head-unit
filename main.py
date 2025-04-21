#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Raspberry Pi BMW iD6-style Car Head Unit
Main entry point for the application.
"""

import os
import sys
import logging

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
    # Using the web application implementation
    # This approach works better in environments like Replit
    # where graphics support for Kivy can be challenging
    try:
        logger.info("Starting BMW iD6-style Car Head Unit (Web Edition)")
        
        # Create directories if they don't exist
        if not os.path.exists('templates'):
            os.makedirs('templates')
        
        if not os.path.exists('static'):
            os.makedirs('static')
            
        # Import and start the Flask web application
        from web_app import app, socketio
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, log_output=True)
        
    except Exception as e:
        logger.exception(f"Failed to start application: {e}")
        sys.exit(1)
