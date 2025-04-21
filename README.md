# BMW iD6-Style Car Head Unit

A sophisticated Raspberry Pi-powered automotive infotainment system with a BMW iD6-enhanced interface, delivering an immersive in-car digital experience with refined UI interactions and dynamic content rendering.

## Key Features

- BMW iD6-style user interface with accurate panel layout and transitions
- 6 main tiles organized in 2 panel groups of 3 tiles each
- Horizontal scrolling tile navigation with group-based paging
- Detailed vehicle information display
- Media player with album art and playback controls
- Android Auto integration
- ConnectedDrive weather information
- CAN bus vehicle data integration (simulated)
- Bluetooth phone connectivity with call handling

## Technologies Used

- Flask web framework
- Flask-SocketIO for real-time updates
- HTML5, CSS3, and JavaScript
- Python for backend services
- Responsive design for different screen sizes

## Setup and Installation

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

## Project Structure

- `main.py`: Main entry point using Flask with simulated data and Bluetooth routes
- `templates/dashboard.html`: BMW iD6 dashboard template with horizontal scrollable tiles
- `static/js/dashboard.js`: JavaScript for dashboard navigation and tile functionality
- `static/css/id6-dashboard.css`: BMW iD6 dashboard styling
- `services/`: Backend service modules for vehicle data, Bluetooth, etc.

## License

This project is intended for educational and personal use only. BMW and iDrive are trademarks of BMW AG.