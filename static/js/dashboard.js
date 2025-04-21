// BMW iD6 Dashboard JavaScript

// Connect to Socket.IO
const socket = io();

// DOM elements
const timeElement = document.querySelector('.time');
const weatherTempElement = document.querySelector('.weather-widget .temperature');
const artistElement = document.querySelector('.artist');
const trackElement = document.querySelector('.track');
const sourceElement = document.querySelector('.source');
const detailsElement = document.querySelector('.details');
const mpgElement = document.querySelector('.vehicle-panel .stat-row:nth-child(1) .stat-value');
const avgSpeedElement = document.querySelector('.vehicle-panel .stat-row:nth-child(2) .stat-value');

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
    if (sourceElement) sourceElement.textContent = `${data.mode} Radio`;
    if (detailsElement) detailsElement.textContent = data.frequency;
});

// Clock update function (as fallback)
function updateClock() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    if (timeElement) timeElement.textContent = `${hours}:${minutes}`;
    setTimeout(updateClock, 60000); // Update every minute
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
                    if (trackElement) trackElement.textContent = data.station_name;
                    if (sourceElement) sourceElement.textContent = `${data.mode} Radio`;
                    if (detailsElement) detailsElement.textContent = data.frequency;
                })
                .catch(error => console.error('Error fetching radio data:', error));
        }
    }, 5000); // Every 5 seconds
});