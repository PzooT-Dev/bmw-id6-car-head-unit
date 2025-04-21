// BMW iD6 Dashboard JavaScript

// Connect to Socket.IO
const socket = io();

// DOM elements
const timeElement = document.querySelector('.time');
const weatherTempElement = document.querySelector('.weather-widget .temperature');
const artistElement = document.querySelector('.artist');
const trackElement = document.querySelector('.track');
const sourceElement = document.querySelector('.source-text');
const mpgElement = document.querySelector('.vehicle-panel .stat-row:nth-child(1) .stat-value');
const avgSpeedElement = document.querySelector('.vehicle-panel .stat-row:nth-child(2) .stat-value');

// Media player elements
const progressBar = document.querySelector('.progress-fill');
const currentTimeEl = document.querySelector('.current-time');
const totalTimeEl = document.querySelector('.total-time');

// Media player state
let currentTrack = 0;
let currentProgress = 35; // Percentage

// Socket.IO event handlers
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('vehicle_update', (data) => {
    // Update vehicle data
    if (mpgElement) mpgElement.textContent = `${data.avg_mpg} mpg`;
    if (avgSpeedElement) avgSpeedElement.textContent = `${data.avg_speed} mph`;
    if (weatherTempElement) weatherTempElement.textContent = `${data.outside_temp}°C`;
    if (timeElement && data.time) timeElement.textContent = data.time;
});

socket.on('radio_update', (data) => {
    // Update radio data
    if (trackElement) trackElement.textContent = data.station_name;
    if (sourceElement) sourceElement.textContent = `Bluetooth Audio`;
});

// Clock update function (as fallback)
function updateClock() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    if (timeElement) timeElement.textContent = `${hours}:${minutes}`;
    setTimeout(updateClock, 60000); // Update every minute
}

// iDrive controller simulation
let currentPanelIndex = 0;
const panels = [];

// Track which set of tiles is visible (0 = first 3 tiles, 1 = next 3 tiles, etc.)
let visibleSetIndex = 0;

function selectPanel(index) {
    // Remove selected class from all panels
    panels.forEach(panel => panel.classList.remove('selected'));
    
    // Ensure index is within bounds (wrap around at edges)
    if (index < 0) index = panels.length - 1;
    if (index >= panels.length) index = 0;
    
    // Select the new panel
    currentPanelIndex = index;
    panels[currentPanelIndex].classList.add('selected');
    
    // Determine which set of 3 tiles should be visible
    const tilesPerSet = 3;
    const newSetIndex = Math.floor(currentPanelIndex / tilesPerSet);
    
    // Only update the visible set if we've moved to a different set of tiles
    if (newSetIndex !== visibleSetIndex) {
        visibleSetIndex = newSetIndex;
    }
    
    // Calculate start and end indexes for the current visible set
    const startIndex = visibleSetIndex * tilesPerSet;
    let endIndex = startIndex + tilesPerSet;
    
    // Handle the case where we're at the end of the list
    if (endIndex > panels.length) {
        endIndex = panels.length;
    }
    
    console.log(`Showing panels ${startIndex} to ${endIndex-1}, selected: ${currentPanelIndex}`);
    
    // Show only the panels in the current visible set
    panels.forEach((panel, i) => {
        // Reset all panels to their natural order
        panel.style.order = i;
        
        // Show only panels in the current set
        if (i >= startIndex && i < endIndex) {
            panel.style.display = 'flex';
        } else {
            panel.style.display = 'none';
        }
    });
    
    // Log panel information for debugging
    console.log("Current panel:", currentPanelIndex, "Last panel:", panels.length - 1);
}

// Handle keyboard navigation to simulate the iDrive controller
function handleKeyNavigation(event) {
    switch(event.key) {
        case 'ArrowRight':
            // Move selection to the right (clockwise on iDrive)
            selectPanel(currentPanelIndex + 1);
            event.preventDefault();
            break;
        case 'ArrowLeft':
            // Move selection to the left (counter-clockwise on iDrive)
            selectPanel(currentPanelIndex - 1);
            event.preventDefault();
            break;
        case 'Enter':
            // Simulate pressing the iDrive controller to select
            console.log('Selected panel:', panels[currentPanelIndex]);
            // Additional action code would go here
            event.preventDefault();
            break;
    }
}

// Date formatting function
function updateDate() {
    const now = new Date();
    const day = now.getDate();
    
    // Get month name
    const monthNames = ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"];
    const month = monthNames[now.getMonth()];
    const year = now.getFullYear();
    
    // Update date display elements
    const dayElement = document.getElementById('date-day');
    const monthElement = document.getElementById('date-month');
    const yearElement = document.getElementById('date-year');
    
    if (dayElement) dayElement.textContent = day;
    if (monthElement) monthElement.textContent = month;
    if (yearElement) yearElement.textContent = year;
}

// Media player functions for automatic playback simulation
function nextTrack() {
    currentTrack = (currentTrack + 1) % tracks.length;
    updateTrackInfo();
    
    // Reset progress
    currentProgress = 0;
    updateProgressBar();
    
    // Send to server (in real implementation)
    socket.emit('media_control', { action: 'next' });
}

// Sample tracks data (would come from server in real implementation)
const tracks = [
    { artist: 'Lola Young', title: 'Messy', duration: '3:45' },
    { artist: 'Lola Young', title: 'Woman', duration: '4:22' },
    { artist: 'Lola Young', title: 'Pick Me Up', duration: '3:18' }
];

function updateTrackInfo() {
    const track = tracks[currentTrack];
    artistElement.textContent = track.artist;
    trackElement.textContent = track.title;
    totalTimeEl.textContent = track.duration;
}

// Progress bar simulation
let progressTimer;

function updateProgressBar() {
    if (progressBar) {
        progressBar.style.width = `${currentProgress}%`;
    }
    
    // Update time display (simulate based on percentage)
    if (currentTimeEl && totalTimeEl) {
        const track = tracks[currentTrack];
        const totalSecs = convertTimeToSeconds(track.duration);
        const currentSecs = Math.floor(totalSecs * (currentProgress / 100));
        currentTimeEl.textContent = convertSecondsToTime(currentSecs);
    }
}

function startProgressSimulation() {
    // Clear any existing timer
    stopProgressSimulation();
    
    // Update progress every second (simulates playback)
    progressTimer = setInterval(() => {
        currentProgress += 1;
        if (currentProgress >= 100) {
            // Reached end of track, go to next
            nextTrack();
        } else {
            updateProgressBar();
        }
    }, 1000);
}

function stopProgressSimulation() {
    if (progressTimer) {
        clearInterval(progressTimer);
    }
}

// Utility functions for time conversion
function convertTimeToSeconds(timeStr) {
    const [mins, secs] = timeStr.split(':').map(Number);
    return (mins * 60) + secs;
}

function convertSecondsToTime(totalSeconds) {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Only start clock if no server connection after 2 seconds
    const clockTimer = setTimeout(() => {
        if (!socket.connected) {
            updateClock();
        }
    }, 2000);
    
    // If we connect, clear the timer
    socket.on('connect', () => {
        clearTimeout(clockTimer);
    });
    
    // Initialize the panels array
    document.querySelectorAll('.panel').forEach(panel => {
        panels.push(panel);
    });
    
    // Set the first panel as selected by default
    if (panels.length > 0) {
        currentPanelIndex = 0; // Start with the first panel
        selectPanel(currentPanelIndex);
    }
    
    // Add keyboard event listener for iDrive controller simulation
    document.addEventListener('keydown', handleKeyNavigation);
    
    // Update date for the Communication panel
    updateDate();
    
    // Initialize the track info
    updateTrackInfo();
    updateProgressBar();
    
    // Start progress simulation
    startProgressSimulation();
    
    // Make API requests periodically to keep data fresh (if socket fails)
    setInterval(() => {
        if (!socket.connected) {
            // Fetch vehicle data
            fetch('/api/vehicle-data')
                .then(response => response.json())
                .then(data => {
                    if (mpgElement) mpgElement.textContent = `${data.avg_mpg} mpg`;
                    if (avgSpeedElement) avgSpeedElement.textContent = `${data.avg_speed} mph`;
                    if (weatherTempElement) weatherTempElement.textContent = `${data.outside_temp}°C`;
                    if (timeElement && data.time) timeElement.textContent = data.time;
                })
                .catch(error => console.error('Error fetching vehicle data:', error));
            
            // Fetch radio data
            fetch('/api/radio-data')
                .then(response => response.json())
                .then(data => {
                    if (trackElement) trackElement.textContent = 'Messy';
                    if (artistElement) artistElement.textContent = data.artist || 'Lola Young';
                })
                .catch(error => console.error('Error fetching radio data:', error));
        }
    }, 5000); // Every 5 seconds
});