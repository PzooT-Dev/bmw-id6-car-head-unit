#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Raspberry Pi BMW iD6-style Car Head Unit
Main entry point for the application.
"""

import os
import sys
import time
import logging
import threading
import random
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Create Flask app and SocketIO instance
app = Flask(__name__)
socketio = SocketIO(app)

# Simulated vehicle data
vehicle_data = {
    'speed': 0,
    'rpm': 0,
    'fuel_level': 75,
    'coolant_temp': 90,
    'outside_temp': 22,
    'avg_mpg': 32.5,
    'avg_speed': 45
}

# Simulated radio data
radio_data = {
    'station_name': 'BMW Radio',
    'frequency': '98.5 MHz',
    'rds_text': 'Now playing: BMW iD6 Demo',
    'mode': 'FM',
    'signal_strength': 85,
    'is_playing': True
}

# Routes
@app.route('/')
def index():
    """Render the BMW iD6 dashboard."""
    return render_template('dashboard.html', 
                          vehicle_data=vehicle_data, 
                          radio_data=radio_data,
                          time=datetime.now().strftime('%H:%M'),
                          outside_temp=vehicle_data['outside_temp'])

@app.route('/api/vehicle-data')
def get_vehicle_data():
    """API endpoint to get current vehicle data."""
    # Add the current time
    vehicle_data['time'] = datetime.now().strftime('%H:%M')
    return jsonify(vehicle_data)

@app.route('/api/radio-data')
def get_radio_data():
    """API endpoint to get current radio data."""
    return jsonify(radio_data)

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")
    # Send initial data on connect
    socketio.emit('vehicle_update', vehicle_data)
    socketio.emit('radio_update', radio_data)

def update_simulated_data():
    """Background thread to simulate vehicle data updates."""
    while True:
        # Update vehicle data with small random changes
        vehicle_data['speed'] = max(0, min(120, vehicle_data['speed'] + random.randint(-5, 5)))
        vehicle_data['rpm'] = max(0, min(5000, vehicle_data['rpm'] + random.randint(-100, 100)))
        vehicle_data['outside_temp'] = round(max(0, min(35, vehicle_data['outside_temp'] + random.random() * 0.2 - 0.1)), 1)
        
        # Simulate slow changes to MPG and average speed
        vehicle_data['avg_mpg'] = round(max(20, min(45, vehicle_data['avg_mpg'] + random.random() * 0.4 - 0.2)), 1)
        vehicle_data['avg_speed'] = round(max(25, min(70, vehicle_data['avg_speed'] + random.random() * 0.6 - 0.3)), 1)
        
        # Emit updates
        socketio.emit('vehicle_update', vehicle_data)
        socketio.emit('radio_update', radio_data)
        
        # Slow down updates to reduce CPU usage
        time.sleep(2)

if __name__ == '__main__':
    try:
        logger.info("Starting BMW iD6-style Car Head Unit")
        
        # Create directories if they don't exist
        if not os.path.exists('templates'):
            os.makedirs('templates')
        
        if not os.path.exists('static'):
            os.makedirs('static')
        
        # Start background thread for simulated data
        threading.Thread(target=update_simulated_data, daemon=True).start()
        
        # Start the Flask web application
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, log_output=True)
        
    except Exception as e:
        logger.exception(f"Failed to start application: {e}")
        sys.exit(1)
