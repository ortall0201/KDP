# AI Ghostwriter Mobile App

React Native mobile app for the CrewAI Multi-Agent Ghostwriter System. Upload manuscripts and get ghostwritten books directly on your iOS or Android device.

## Architecture

- **Frontend**: React Native (Expo) for iOS and Android
- **Backend**: FastAPI server (Python) running the CrewAI orchestrator
- **Communication**: REST API + WebSocket for real-time updates

## Features

- 📤 Upload .txt manuscript files
- 📊 Real-time progress tracking
- 🔄 Live updates via WebSocket
- 📥 Download completed manuscripts
- ✅ System health monitoring
- 🎨 Clean, professional UI

## Prerequisites

### Backend Server
1. Python 3.10+
2. Redis (running on localhost:6379)
3. ChromaDB (running on localhost:8000)
4. OpenAI API key
5. Anthropic API key

### Mobile Development
1. Node.js 18+
2. npm or yarn
3. Expo CLI
4. iOS Simulator (Mac) or Android Emulator

## Setup

### 1. Start Backend Server

```bash
# Navigate to CrewAI ghostwriter directory
cd ../crewai_ghostwriter

# Install Python dependencies
pip install -r requirements.txt

# Start infrastructure (Redis + ChromaDB)
cd ../docker
docker-compose up -d

# Start API server
cd ../crewai_ghostwriter
python api_server.py
```

The API server will run on `http://localhost:8080`

### 2. Setup Mobile App

```bash
# Navigate to mobile app directory
cd mobile_app

# Install dependencies
npm install

# Start Expo development server
npm start
```

### 3. Run on Device/Simulator

After `npm start`:
- Press `i` for iOS simulator (Mac only)
- Press `a` for Android emulator
- Scan QR code with Expo Go app on physical device

## Configuration

### Backend URL

Edit `src/services/api.js` to configure backend URL:

```javascript
// For local development
const API_BASE_URL = 'http://localhost:8080';

// For production (your deployed server)
const API_BASE_URL = 'https://your-api-server.com';
```

**Note for iOS Simulator**: Use `http://localhost:8080`
**Note for Android Emulator**: Use `http://10.0.2.2:8080`
**Note for Physical Device**: Use your computer's local IP (e.g., `http://192.168.1.100:8080`)

## Building for App Stores

### iOS (App Store)

1. **Configure app.json**:
```json
{
  "ios": {
    "bundleIdentifier": "com.yourcompany.aiGhostwriter",
    "buildNumber": "1.0.0"
  }
}
```

2. **Create Apple Developer Account** ($99/year)

3. **Build with EAS**:
```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Configure build
eas build:configure

# Build for iOS
eas build --platform ios
```

4. **Submit to App Store**:
```bash
eas submit --platform ios
```

### Android (Google Play Store)

1. **Configure app.json**:
```json
{
  "android": {
    "package": "com.yourcompany.aiGhostwriter",
    "versionCode": 1
  }
}
```

2. **Create Google Play Developer Account** ($25 one-time)

3. **Build APK/AAB**:
```bash
# Build for Android
eas build --platform android

# Or build locally
npm run android -- --variant=release
```

4. **Submit to Google Play**:
```bash
eas submit --platform android
```

## Screenshots

### Home Screen
- System health check
- File upload interface
- Processing phases overview

### Processing Screen
- Real-time progress bar
- Phase status indicators
- Chapter-by-chapter progress
- Activity log with timestamps

### Completed Screen
- Success confirmation
- Final word count
- Download button
- Process another manuscript

## API Endpoints

### REST API
- `GET /health` - System health check
- `POST /upload` - Upload manuscript (returns job_id)
- `GET /status/{job_id}` - Get job status
- `GET /download/{job_id}` - Download completed manuscript

### WebSocket
- `ws://localhost:8080/ws/{job_id}` - Real-time job updates

## Deployment

### Backend Server Options

1. **AWS EC2**: Run FastAPI on EC2 instance
2. **Google Cloud Run**: Containerized FastAPI deployment
3. **DigitalOcean Droplet**: Simple VPS hosting
4. **Railway/Render**: Easy Python deployment

### Requirements
- Server with GPU for faster processing (optional but recommended)
- Redis and ChromaDB running
- Environment variables configured (.env file)
- SSL certificate for production (HTTPS)

## Troubleshooting

### "Backend not responding"
- Check if API server is running: `curl http://localhost:8080/health`
- Verify Redis is running: `redis-cli ping`
- Verify ChromaDB is running: `curl http://localhost:8000/api/v1/heartbeat`

### "WebSocket connection failed"
- Fallback to polling is automatic
- Check firewall allows WebSocket connections

### "Upload fails"
- Verify file is .txt format
- Check file size (large files may timeout)
- Ensure backend has write permissions for uploads/

## Development

### File Structure
```
mobile_app/
├── src/
│   ├── screens/
│   │   ├── HomeScreen.js          # Upload & health check
│   │   ├── ProcessingScreen.js    # Real-time progress
│   │   └── CompletedScreen.js     # Download results
│   ├── services/
│   │   └── api.js                 # API client
│   └── components/                # Reusable components
├── App.js                         # Main app & navigation
├── app.json                       # Expo configuration
├── package.json                   # Dependencies
└── README.md                      # This file
```

### Adding Features

**New Screen**:
1. Create screen in `src/screens/`
2. Add to navigation in `App.js`

**API Changes**:
1. Update backend `api_server.py`
2. Update frontend `src/services/api.js`

## License

Proprietary - All rights reserved

## Support

For issues or questions, check:
- Backend logs: `api_server.py` console
- Mobile logs: Expo console or device logs
- System health: Visit `http://localhost:8080/health`

---

**Version**: 1.0.0
**Last Updated**: 2026-01-07
