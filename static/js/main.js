// BMW iD6 Interface JavaScript

// Connect to SocketIO
const socket = io();

// Elements
const dashboardScreen = document.getElementById('dashboard-screen');
const mediaScreen = document.getElementById('media-screen');
const navigationScreen = document.getElementById('navigation-screen');
const settingsScreen = document.getElementById('settings-screen');
const screens = [dashboardScreen, mediaScreen, navigationScreen, settingsScreen];

// Navigation buttons
const navButtons = document.querySelectorAll('.nav-button');

// Media control elements
const playPauseButton = document.getElementById('play-pause');
const prevStationButton = document.getElementById('prev-station');
const nextStationButton = document.getElementById('next-station');
const volumeSlider = document.getElementById('volume-slider');
const toggleModeButton = document.getElementById('toggle-mode');

// Settings elements
const brightnessSlider = document.getElementById('brightness-slider');
const balanceSlider = document.getElementById('balance-slider');
const nightModeToggle = document.getElementById('night-mode-toggle');

// Elements for data display
const speedGauge = document.querySelector('.speed-gauge .gauge-value');
const rpmGauge = document.querySelector('.rpm-gauge .gauge-value');
const fuelLevel = document.querySelector('.fuel-level');
const fuelValue = document.querySelector('.data-container:nth-child(1) .data-value');
const coolantTemp = document.querySelector('.data-container:nth-child(2) .data-value');
const timeDisplay = document.querySelector('.time');
const outsideTemp = document.querySelector('.temperature');

const stationName = document.querySelector('.station-name');
const stationFrequency = document.querySelector('.station-frequency');
const rdsText = document.querySelector('.rds-text');
const mediaMode = document.querySelector('.media-mode');
const signalBar = document.querySelector('.signal-bar');
const signalValue = document.querySelector('.signal-value');

// Switch screen when navigation button is clicked
navButtons.forEach(button => {
    button.addEventListener('click', (event) => {
        event.preventDefault(); // Prevent default behavior
        const screenId = button.getAttribute('data-screen');
        console.log('Switching to screen:', screenId);
        
        if (!screenId || !document.getElementById(screenId)) {
            console.error('Invalid screen ID:', screenId);
            return;
        }
        
        // Deactivate all screens and buttons
        screens.forEach(screen => {
            if (screen) screen.classList.remove('active');
        });
        navButtons.forEach(btn => btn.classList.remove('active'));
        
        // Activate the selected screen and button
        document.getElementById(screenId).classList.add('active');
        button.classList.add('active');
    });
});

// Socket.io events
socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('vehicle_update', (data) => {
    // Update dashboard display
    speedGauge.textContent = Math.round(data.speed);
    rpmGauge.textContent = Math.round(data.rpm);
    fuelLevel.style.width = `${data.fuel_level}%`;
    fuelValue.textContent = `${Math.round(data.fuel_level)}%`;
    coolantTemp.textContent = `${Math.round(data.coolant_temp)}°C`;
    timeDisplay.textContent = data.time;
    outsideTemp.textContent = `Outside: ${data.outside_temp}°C`;
});

socket.on('radio_update', (data) => {
    // Update media player display
    stationName.textContent = data.station_name;
    stationFrequency.textContent = data.frequency;
    rdsText.textContent = data.rds_text;
    mediaMode.textContent = data.mode;
    signalBar.style.width = `${data.signal_strength}%`;
    signalValue.textContent = `${data.signal_strength}%`;
    playPauseButton.textContent = data.is_playing ? 'Pause' : 'Play';
    toggleModeButton.textContent = `Switch to ${data.mode === 'FM' ? 'DAB' : 'FM'}`;
});

socket.on('audio_update', (data) => {
    // Update audio settings display
    volumeSlider.value = data.volume;
    balanceSlider.value = data.balance;
    
    // Update balance indicator
    const balanceIndicator = document.querySelector('.balance-indicator');
    if (balanceIndicator) {
        const leftDashes = '-'.repeat(Math.floor(data.balance / 10));
        const rightDashes = '-'.repeat(Math.floor((100 - data.balance) / 10));
        balanceIndicator.textContent = `${leftDashes}|${rightDashes}`;
    }
});

socket.on('display_update', (data) => {
    // Update display settings
    brightnessSlider.value = data.brightness;
    
    // Update night mode
    if (data.night_mode) {
        document.body.classList.add('night-mode');
        nightModeToggle.classList.add('active');
        nightModeToggle.textContent = 'ON';
    } else {
        document.body.classList.remove('night-mode');
        nightModeToggle.classList.remove('active');
        nightModeToggle.textContent = 'OFF';
    }
});

// Event Listeners for UI controls

// Media Controls
playPauseButton.addEventListener('click', () => {
    socket.emit('toggle_play_pause');
});

prevStationButton.addEventListener('click', () => {
    socket.emit('seek_prev_station');
});

nextStationButton.addEventListener('click', () => {
    socket.emit('seek_next_station');
});

volumeSlider.addEventListener('input', () => {
    const volume = parseInt(volumeSlider.value);
    document.querySelector('.volume-value').textContent = `${volume}%`;
});

volumeSlider.addEventListener('change', () => {
    const volume = parseInt(volumeSlider.value);
    socket.emit('set_volume', { volume });
});

toggleModeButton.addEventListener('click', () => {
    socket.emit('toggle_radio_mode');
});

// Settings Controls
brightnessSlider.addEventListener('input', () => {
    const brightness = parseInt(brightnessSlider.value);
    document.querySelector('.setting-control:nth-child(1) .setting-value').textContent = `${brightness}%`;
});

brightnessSlider.addEventListener('change', () => {
    const brightness = parseInt(brightnessSlider.value);
    socket.emit('adjust_brightness', { brightness });
});

balanceSlider.addEventListener('input', () => {
    const balance = parseInt(balanceSlider.value);
    const leftDashes = '-'.repeat(Math.floor(balance / 10));
    const rightDashes = '-'.repeat(Math.floor((100 - balance) / 10));
    document.querySelector('.balance-indicator').textContent = `${leftDashes}|${rightDashes}`;
});

balanceSlider.addEventListener('change', () => {
    const balance = parseInt(balanceSlider.value);
    socket.emit('adjust_balance', { balance });
});

nightModeToggle.addEventListener('click', () => {
    socket.emit('toggle_night_mode');
});

// Make API requests periodically to keep data fresh (if socket fails)
setInterval(() => {
    fetch('/api/vehicle-data')
        .then(response => response.json())
        .then(data => {
            // Fallback update if socket doesn't work
            if (!socket.connected) {
                speedGauge.textContent = Math.round(data.speed);
                rpmGauge.textContent = Math.round(data.rpm);
                fuelLevel.style.width = `${data.fuel_level}%`;
                fuelValue.textContent = `${Math.round(data.fuel_level)}%`;
                coolantTemp.textContent = `${Math.round(data.coolant_temp)}°C`;
                timeDisplay.textContent = data.time;
                outsideTemp.textContent = `Outside: ${data.outside_temp}°C`;
            }
        })
        .catch(error => console.error('Error fetching vehicle data:', error));
    
    fetch('/api/radio-data')
        .then(response => response.json())
        .then(data => {
            // Fallback update if socket doesn't work
            if (!socket.connected) {
                stationName.textContent = data.station_name;
                stationFrequency.textContent = data.frequency;
                rdsText.textContent = data.rds_text;
                mediaMode.textContent = data.mode;
                signalBar.style.width = `${data.signal_strength}%`;
                signalValue.textContent = `${data.signal_strength}%`;
                playPauseButton.textContent = data.is_playing ? 'Pause' : 'Play';
                toggleModeButton.textContent = `Switch to ${data.mode === 'FM' ? 'DAB' : 'FM'}`;
            }
        })
        .catch(error => console.error('Error fetching radio data:', error));
}, 5000); // Every 5 seconds