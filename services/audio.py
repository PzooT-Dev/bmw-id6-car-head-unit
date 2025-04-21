# -*- coding: utf-8 -*-

"""
Audio Manager Module
Handles audio playback and volume control
"""

import os
import time
import threading
import logging
import pyaudio
import wave
import subprocess

logger = logging.getLogger(__name__)

class AudioManager:
    """
    Manager for audio playback and volume control.
    """
    
    def __init__(self):
        """Initialize the audio manager."""
        self.volume = 0.5  # 0.0 to 1.0
        self.balance = 0.0  # -1.0 (left) to 1.0 (right)
        self.muted = False
        self.playing = False
        self.current_stream = None
        self.pyaudio_instance = None
        self.simulation_mode = True  # Run in simulation mode without actual audio hardware
        
        try:
            if not self.simulation_mode:
                # Initialize PyAudio only if not in simulation mode
                self.pyaudio_instance = pyaudio.PyAudio()
                logger.info("Audio manager initialized with PyAudio")
            else:
                logger.info("Audio manager initialized in simulation mode")
        except Exception as e:
            logger.error(f"Error initializing audio manager: {e}")
            self.simulation_mode = True  # Fall back to simulation mode on error
    
    def play(self):
        """Play or resume audio."""
        if self.playing:
            return
            
        self.playing = True
        logger.info("Audio playback started/resumed")
    
    def pause(self):
        """Pause audio playback."""
        if not self.playing:
            return
            
        self.playing = False
        logger.info("Audio playback paused")
    
    def stop(self):
        """Stop audio playback."""
        self.playing = False
        
        if self.current_stream:
            try:
                self.current_stream.stop_stream()
                self.current_stream.close()
                self.current_stream = None
            except Exception as e:
                logger.error(f"Error stopping audio stream: {e}")
        
        logger.info("Audio playback stopped")
    
    def set_volume(self, volume):
        """
        Set the audio volume.
        
        Args:
            volume (float): Volume level from 0.0 to 1.0
        """
        self.volume = max(0.0, min(1.0, volume))
        
        # Apply volume using ALSA if on Linux
        try:
            if os.name == 'posix':
                # Convert 0.0-1.0 to 0-100%
                volume_percent = int(self.volume * 100)
                subprocess.run(['amixer', 'sset', 'Master', f'{volume_percent}%'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f"Error setting volume: {e}")
        
        logger.info(f"Volume set to {self.volume:.2f}")
    
    def set_balance(self, balance):
        """
        Set the audio balance.
        
        Args:
            balance (float): Balance from -1.0 (left) to 1.0 (right)
        """
        self.balance = max(-1.0, min(1.0, balance))
        
        # Apply balance using ALSA if on Linux
        try:
            if os.name == 'posix':
                # Calculate left/right volumes based on balance
                if self.balance < 0:
                    left_volume = 100
                    right_volume = int((1.0 + self.balance) * 100)
                else:
                    left_volume = int((1.0 - self.balance) * 100)
                    right_volume = 100
                
                subprocess.run(['amixer', 'sset', 'Master', f'{left_volume}%,{right_volume}%'], 
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f"Error setting balance: {e}")
        
        logger.info(f"Balance set to {self.balance:.2f}")
    
    def toggle_mute(self):
        """Toggle mute state."""
        self.muted = not self.muted
        
        # Apply mute using ALSA if on Linux
        try:
            if os.name == 'posix':
                if self.muted:
                    subprocess.run(['amixer', 'sset', 'Master', 'mute'], 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    subprocess.run(['amixer', 'sset', 'Master', 'unmute'], 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            logger.error(f"Error toggling mute: {e}")
        
        logger.info(f"Mute {'enabled' if self.muted else 'disabled'}")
    
    def play_audio_file(self, file_path):
        """
        Play an audio file.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return False
            
        # Stop any current playback
        self.stop()
        
        try:
            if self.simulation_mode:
                # In simulation mode, just simulate playback
                logger.info(f"Simulation: Playing audio file: {file_path}")
                self.playing = True
                return True
            
            # Real playback for non-simulation mode
            if file_path.endswith('.wav'):
                # Play WAV file using PyAudio
                self._play_wav_file(file_path)
            else:
                # For other formats, use aplay on Linux
                if os.name == 'posix':
                    subprocess.Popen(['aplay', file_path], 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    logger.error("Unsupported audio format on this platform")
                    return False
            
            self.playing = True
            return True
        except Exception as e:
            logger.error(f"Error playing audio file: {e}")
            return False
    
    def _play_wav_file(self, file_path):
        """
        Play a WAV file using PyAudio.
        
        Args:
            file_path (str): Path to the WAV file
        """
        if not self.pyaudio_instance:
            logger.error("PyAudio not initialized")
            return
            
        try:
            wf = wave.open(file_path, 'rb')
            
            def callback(in_data, frame_count, time_info, status):
                data = wf.readframes(frame_count)
                return (data, pyaudio.paContinue if len(data) > 0 else pyaudio.paComplete)
            
            self.current_stream = self.pyaudio_instance.open(
                format=self.pyaudio_instance.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback
            )
            
            self.current_stream.start_stream()
            
        except Exception as e:
            logger.error(f"Error playing WAV file: {e}")
    
    def restart(self):
        """Restart the audio manager."""
        self.shutdown()
        
        try:
            if not self.simulation_mode:
                # Reinitialize PyAudio only if not in simulation mode
                self.pyaudio_instance = pyaudio.PyAudio()
                logger.info("Audio manager restarted with PyAudio")
            else:
                logger.info("Audio manager restarted in simulation mode")
        except Exception as e:
            logger.error(f"Error restarting audio manager: {e}")
            self.simulation_mode = True  # Fall back to simulation mode on error
    
    def shutdown(self):
        """Shutdown the audio manager and clean up resources."""
        self.stop()
        
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
                self.pyaudio_instance = None
            except Exception as e:
                logger.error(f"Error terminating PyAudio: {e}")
                
        logger.info("Audio manager shutdown")
