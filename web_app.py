#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web-based BMW iD6 UI
Uses Flask and SocketIO to create a web interface mimicking the BMW iD6 system
"""

import os
import logging
import json
import threading
import time
import random
from datetime import datetime
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bmw-id6-secret!'
socketio = SocketIO(app)

# Shared data for vehicle status
vehicle_data = {
    'speed': 45,
    'rpm': 1500,
    'fuel_level': 75,
    'coolant_temp': 90,
    'outside_temp': 22,
    'engine_on': True,
    'time': datetime.now().strftime('%H:%M')
}

# Radio data
radio_data = {
    'mode': 'FM',  # 'FM' or 'DAB'
    'frequency': '98.8 MHz',
    'station_name': 'Simulation Radio 1',
    'rds_text': 'Welcome to Simulation FM Radio',
    'signal_strength': 85,
    'is_playing': False
}

# Available stations
fm_stations = {
    87.9: "ROCK FM",
    88.5: "CLASSIC HITS",
    89.1: "NEWS 24/7",
    91.3: "SMOOTH JAZZ",
    93.5: "TOP 40",
    95.7: "COUNTRY",
    97.9: "TALK RADIO",
    99.1: "HIP HOP",
    101.3: "CLASSICAL",
    103.5: "ALTERNATIVE",
    105.7: "OLDIES",
    107.9: "POP HITS"
}

dab_stations = [
    ("0x1001", "BBC Radio 1"),
    ("0x1002", "BBC Radio 2"),
    ("0x1003", "BBC Radio 3"),
    ("0x1004", "BBC Radio 4"),
    ("0x1005", "Classic FM"),
    ("0x1006", "Heart"),
    ("0x1007", "Capital")
]

# Audio settings
audio_settings = {
    'volume': 50,  # 0-100
    'balance': 50,  # 0-100 (0=left, 50=center, 100=right)
    'muted': False
}

# Display settings
display_settings = {
    'brightness': 80,  # 0-100
    'night_mode': False
}

@app.route('/')
def index():
    """Render the main BMW iD6 interface."""
    return render_template('index.html', 
                           vehicle_data=vehicle_data,
                           radio_data=radio_data,
                           audio_settings=audio_settings,
                           display_settings=display_settings)

@app.route('/dashboard')
def dashboard():
    """Render just the dashboard view."""
    return render_template('dashboard.html', vehicle_data=vehicle_data)

@app.route('/media')
def media():
    """Render just the media player view."""
    return render_template('media.html', 
                          radio_data=radio_data,
                          audio_settings=audio_settings)

@app.route('/navigation')
def navigation():
    """Render just the navigation view."""
    return render_template('navigation.html')

@app.route('/settings')
def settings():
    """Render just the settings view."""
    return render_template('settings.html', 
                          audio_settings=audio_settings,
                          display_settings=display_settings)

@app.route('/api/vehicle-data')
def get_vehicle_data():
    """API endpoint to get current vehicle data."""
    # Update the time
    vehicle_data['time'] = datetime.now().strftime('%H:%M')
    return jsonify(vehicle_data)

@app.route('/api/radio-data')
def get_radio_data():
    """API endpoint to get current radio data."""
    return jsonify(radio_data)

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info('Client connected')
    socketio.emit('vehicle_update', vehicle_data)
    socketio.emit('radio_update', radio_data)

@socketio.on('set_volume')
def handle_volume(data):
    """Handle volume change."""
    volume = data.get('volume', 50)
    audio_settings['volume'] = max(0, min(100, volume))
    logger.info(f"Volume set to {audio_settings['volume']}")
    socketio.emit('audio_update', audio_settings)

@socketio.on('toggle_play_pause')
def handle_play_pause():
    """Handle play/pause toggle."""
    radio_data['is_playing'] = not radio_data['is_playing']
    state = "playing" if radio_data['is_playing'] else "paused"
    logger.info(f"Radio playback {state}")
    socketio.emit('radio_update', radio_data)

@socketio.on('toggle_radio_mode')
def handle_radio_mode():
    """Toggle between FM and DAB radio modes."""
    if radio_data['mode'] == 'FM':
        radio_data['mode'] = 'DAB'
        radio_data['frequency'] = 'DAB'
        radio_data['station_name'] = dab_stations[0][1]
        radio_data['rds_text'] = f"DAB: {dab_stations[0][1]}"
    else:
        radio_data['mode'] = 'FM'
        radio_data['frequency'] = '98.8 MHz'
        radio_data['station_name'] = fm_stations[98.8] if 98.8 in fm_stations else "Simulation Radio 1"
        radio_data['rds_text'] = f"You're listening to {radio_data['station_name']}"
    
    logger.info(f"Radio mode changed to {radio_data['mode']}")
    socketio.emit('radio_update', radio_data)

@socketio.on('seek_next_station')
def handle_next_station():
    """Seek to the next available station."""
    if radio_data['mode'] == 'FM':
        # Get the current frequency
        current_freq = float(radio_data['frequency'].split(' ')[0])
        # Find the next frequency in the list
        frequencies = sorted(fm_stations.keys())
        current_index = -1
        for i, freq in enumerate(frequencies):
            if abs(freq - current_freq) < 0.2:  # Close enough to consider it the current station
                current_index = i
                break
        
        # Move to the next station
        if current_index != -1:
            next_index = (current_index + 1) % len(frequencies)
            next_freq = frequencies[next_index]
            radio_data['frequency'] = f"{next_freq:.1f} MHz"
            radio_data['station_name'] = fm_stations[next_freq]
            radio_data['rds_text'] = f"You're listening to {radio_data['station_name']}"
    else:
        # For DAB, find the next station in the list
        current_station = radio_data['station_name']
        current_index = -1
        for i, (_, station_name) in enumerate(dab_stations):
            if station_name == current_station:
                current_index = i
                break
        
        # Move to the next station
        if current_index != -1:
            next_index = (current_index + 1) % len(dab_stations)
            _, next_station = dab_stations[next_index]
            radio_data['station_name'] = next_station
            radio_data['rds_text'] = f"DAB: {next_station}"
    
    logger.info(f"Tuned to {radio_data['station_name']}")
    socketio.emit('radio_update', radio_data)

@socketio.on('seek_prev_station')
def handle_prev_station():
    """Seek to the previous available station."""
    if radio_data['mode'] == 'FM':
        # Get the current frequency
        current_freq = float(radio_data['frequency'].split(' ')[0])
        # Find the previous frequency in the list
        frequencies = sorted(fm_stations.keys())
        current_index = -1
        for i, freq in enumerate(frequencies):
            if abs(freq - current_freq) < 0.2:  # Close enough to consider it the current station
                current_index = i
                break
        
        # Move to the previous station
        if current_index != -1:
            prev_index = (current_index - 1) % len(frequencies)
            prev_freq = frequencies[prev_index]
            radio_data['frequency'] = f"{prev_freq:.1f} MHz"
            radio_data['station_name'] = fm_stations[prev_freq]
            radio_data['rds_text'] = f"You're listening to {radio_data['station_name']}"
    else:
        # For DAB, find the previous station in the list
        current_station = radio_data['station_name']
        current_index = -1
        for i, (_, station_name) in enumerate(dab_stations):
            if station_name == current_station:
                current_index = i
                break
        
        # Move to the previous station
        if current_index != -1:
            prev_index = (current_index - 1) % len(dab_stations)
            _, prev_station = dab_stations[prev_index]
            radio_data['station_name'] = prev_station
            radio_data['rds_text'] = f"DAB: {prev_station}"
    
    logger.info(f"Tuned to {radio_data['station_name']}")
    socketio.emit('radio_update', radio_data)

@socketio.on('toggle_night_mode')
def handle_night_mode():
    """Toggle between day and night modes."""
    display_settings['night_mode'] = not display_settings['night_mode']
    mode = "Night mode" if display_settings['night_mode'] else "Day mode"
    logger.info(f"{mode} activated")
    socketio.emit('display_update', display_settings)

@socketio.on('adjust_brightness')
def handle_brightness(data):
    """Adjust display brightness."""
    brightness = data.get('brightness', 80)
    display_settings['brightness'] = max(0, min(100, brightness))
    logger.info(f"Brightness set to {display_settings['brightness']}")
    socketio.emit('display_update', display_settings)

@socketio.on('adjust_balance')
def handle_balance(data):
    """Adjust audio balance."""
    balance = data.get('balance', 50)
    audio_settings['balance'] = max(0, min(100, balance))
    logger.info(f"Balance set to {audio_settings['balance']}")
    socketio.emit('audio_update', audio_settings)

def update_vehicle_data():
    """Background thread to simulate vehicle data updates."""
    last_update = time.time()
    
    while True:
        # Only update every 500ms
        current_time = time.time()
        if current_time - last_update >= 0.5:
            try:
                # Simulate speed changes (with some randomness)
                vehicle_data['speed'] += random.randint(-3, 3)
                vehicle_data['speed'] = max(0, min(120, vehicle_data['speed']))
                
                # Simulate RPM changes based on speed
                target_rpm = vehicle_data['speed'] * 30 + 800  # Simplified RPM calculation
                vehicle_data['rpm'] += (target_rpm - vehicle_data['rpm']) // 10
                vehicle_data['rpm'] = max(800, min(6000, vehicle_data['rpm']))
                
                # Gradually decrease fuel level
                if random.random() < 0.01:  # 1% chance per iteration
                    vehicle_data['fuel_level'] -= 0.1
                    vehicle_data['fuel_level'] = max(0, vehicle_data['fuel_level'])
                
                # Simulate coolant temperature fluctuations
                vehicle_data['coolant_temp'] += random.randint(-1, 1)
                vehicle_data['coolant_temp'] = max(80, min(105, vehicle_data['coolant_temp']))
                
                # Simulate outside temperature changes
                if random.random() < 0.05:  # 5% chance per iteration
                    vehicle_data['outside_temp'] += random.uniform(-0.1, 0.1)
                    vehicle_data['outside_temp'] = round(vehicle_data['outside_temp'], 1)
                
                # Update the time
                vehicle_data['time'] = datetime.now().strftime('%H:%M')
                
                # Emit the updated data
                socketio.emit('vehicle_update', vehicle_data)
                
                # Update radio signal strength occasionally
                if random.random() < 0.1:  # 10% chance per iteration
                    radio_data['signal_strength'] += random.randint(-5, 5)
                    radio_data['signal_strength'] = max(0, min(100, radio_data['signal_strength']))
                    socketio.emit('radio_update', radio_data)
                
                # Update RDS text occasionally
                if random.random() < 0.05 and radio_data['mode'] == 'FM':  # 5% chance per iteration
                    rds_texts = [
                        f"You're listening to {radio_data['station_name']}",
                        f"{radio_data['station_name']} - Your Music Station",
                        "Text us at 12345",
                        "Follow us on social media",
                        f"{radio_data['station_name']} - No commercials"
                    ]
                    radio_data['rds_text'] = random.choice(rds_texts)
                    socketio.emit('radio_update', radio_data)
                
                last_update = current_time
                
            except Exception as e:
                logger.error(f"Error updating vehicle data: {e}")
            
        # Sleep to avoid CPU spike
        time.sleep(0.1)

# Flask 2.0+ doesn't have before_first_request anymore
# Use this pattern instead
@app.before_request
def start_background_thread_check():
    """Start the background thread for data updates (if needed)."""
    if not hasattr(app, 'background_started'):
        app.background_started = True
        thread = threading.Thread(target=update_vehicle_data)
        thread.daemon = True
        thread.start()

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Update static files from existing UI design
    # Start the Flask app
    logger.info("Starting BMW iD6 Web Interface")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False, log_output=True)