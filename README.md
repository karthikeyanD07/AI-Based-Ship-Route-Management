# AI Ship Route Management System (NeoECDIS)

A comprehensive maritime navigation system providing real-time ship tracking, route optimization, and weather integration.

## 🚀 Features

- **Real-time Ship Tracking**: Track multiple vessels with live position updates via WebSocket
- **Route Optimization**: AI-powered route planning between ports with ocean-safe paths and caching
- **Weather Integration**: Real-time weather data and overlays for maritime conditions
- **Interactive Maps**: Multiple map layers including nautical charts and weather overlays
- **Modern UI**: Responsive React frontend with dark/light theme support
- **Production-Ready**: Thread-safe, rate-limited, error-handled, with metrics and health checks
- **Database Integration**: Optional PostgreSQL/PostGIS for data persistence
- **WebSocket Support**: Real-time updates without polling overhead
- **Comprehensive Monitoring**: Request tracking, metrics collection, and health checks

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+ (optional, for database features)
- OpenWeatherMap API key (for weather features)

## 🛠️ Installation

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI-SHIP-ROUTE-MANAGEMENT
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy .env.example to .env and fill in your values
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   OPENWEATHER_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://user:password@localhost:5432/ship_route_db
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

5. **Prepare data files**
   - Place your AIS data CSV file in the root directory
   - Default file: `final_ship_routes.csv` or `trip9.csv`
   - Required columns: MMSI, lat (or Latitude), lon (or Longitude), sog (or Speed), cog (or Course), status

6. **Run the backend**
   ```bash
   # Using uvicorn directly
   uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
   
   # Or using FastAPI CLI
   fastapi dev backend/app/main.py
   ```

   The API will be available at `http://127.0.0.1:8000`
   API documentation: `http://127.0.0.1:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd Vite_Frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   ```

   Edit `.env`:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   VITE_OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## 📁 Project Structure

```
AI-SHIP-ROUTE-MANAGEMENT/
├── backend/
│   └── app/
│       ├── config/
│       │   └── settings.py          # Configuration management
│       ├── models/
│       │   ├── schemas.py           # Pydantic models
│       │   └── database.py          # SQLAlchemy models
│       ├── routes/
│       │   ├── ships.py             # Ship tracking endpoints
│       │   ├── routes.py            # Route optimization endpoints
│       │   ├── weather.py           # Weather endpoints
│       │   └── health.py            # Health check endpoints
│       ├── services/
│       │   ├── ship_service.py      # Ship tracking logic
│       │   ├── route_service.py     # Route optimization logic
│       │   └── weather_service.py   # Weather integration
│       ├── utils/
│       │   ├── ocean_detection.py   # Land/water detection
│       │   └── route_algorithms.py  # Route optimization algorithms
│       └── main.py                  # FastAPI application entry
├── Vite_Frontend/
│   └── src/
│       ├── assets/
│       │   └── Components/          # React components
│       ├── components/
│       │   └── ErrorBoundary.jsx    # Error handling
│       └── config.js                # Frontend configuration
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
└── README.md                        # This file
```

## 🔌 API Endpoints

### Ship Tracking

- `GET /api/ship-traffic` - Get all tracked ships with pagination
  - Query params: 
    - `limit` (optional, 1-1000) - Maximum ships to return
    - `offset` (optional, default: 0) - Number of ships to skip
  - Response includes: `ships`, `total`, `limit`, `offset`, `has_more`
- `GET /api/ship/{mmsi}` - Get specific ship by MMSI
- `WS /ws/ship-updates` - WebSocket endpoint for real-time ship position updates

### Route Optimization

- `POST /api/get_optimized_route/` - Optimize route between ports (rate-limited, cached)
  ```json
  {
    "ship_id": "123456789",
    "start": "Port A",
    "end": "Port B"
  }
  ```
  Response includes route points, distance, and estimated time.
  Routes are cached for 1 hour to improve performance.

### Weather

- `GET /api/weather?lat={latitude}&lon={longitude}` - Get weather at location

### Health & Monitoring

- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health check with dependency status
- `GET /metrics` - Application metrics (counters, timers, gauges)
- `GET /` - API information

### Rate Limiting

All endpoints are rate-limited:
- Ship endpoints: 60 requests/minute
- Route optimization: 30 requests/minute
- Weather: 60 requests/minute

## 🔧 Configuration

### Backend Configuration

All configuration is managed through environment variables (see `.env.example`):

- `HOST`, `PORT`: Server binding
- `CORS_ORIGINS`: Allowed frontend origins
- `DATABASE_URL`: PostgreSQL connection string
- `OPENWEATHER_API_KEY`: Weather API key
- `MAX_SHIPS_DISPLAY`: Maximum ships to track
- `SHIP_UPDATE_INTERVAL`: Ship position update interval (seconds)

### Frontend Configuration

- `VITE_API_BASE_URL`: Backend API URL
- `VITE_OPENWEATHER_API_KEY`: Weather API key (for map overlays)

## 🗄️ Database (Optional)

The system includes database models for persistence. To use:

1. **Install PostgreSQL with PostGIS**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgis
   
   # macOS
   brew install postgresql postgis
   ```

2. **Create database**
   ```sql
   CREATE DATABASE ship_route_db;
   \c ship_route_db
   CREATE EXTENSION postgis;
   ```

3. **Initialize tables**
   ```python
   from backend.app.models.database import init_db
   init_db()
   ```

## 🧪 Development

### Running in Development Mode

Backend:
```bash
# Using uvicorn directly
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

# Or using the provided script
# Windows:
run_backend.bat
# Linux/Mac:
./run_backend.sh
```

Frontend:
```bash
cd Vite_Frontend
npm run dev
```

### Key Improvements Implemented

**Critical Fixes:**
- ✅ Thread-safe ship position updates (no race conditions)
- ✅ Memory-efficient CSV loading with size limits and chunking
- ✅ Database integration for data persistence
- ✅ Production-safe error handling (no stack trace leaks)
- ✅ Rate limiting on all endpoints

**High Priority:**
- ✅ WebSocket support for real-time updates (replaces polling)
- ✅ Improved ocean detection with better heuristics
- ✅ Async optimization using thread pools
- ✅ HTTP connection pooling for external APIs
- ✅ Pagination support for ship list endpoint

**Medium Priority:**
- ✅ Request ID tracking for correlation
- ✅ Comprehensive health checks
- ✅ Exponential backoff retry logic in frontend
- ✅ Response compression (gzip)
- ✅ Route calculation caching

**Nice to Have:**
- ✅ Metrics collection endpoint
- ✅ Magic numbers documented
- ✅ Request size validation
- ✅ Backpressure handling for background tasks

### Code Structure

- **Backend**: Follows FastAPI best practices with separation of concerns
  - Routes: API endpoints
  - Services: Business logic
  - Models: Data validation and database models
  - Utils: Reusable utilities

- **Frontend**: React with functional components
  - Components: Reusable UI components
  - Error boundaries: Graceful error handling
  - Configuration: Environment-based config

## 🔒 Security

- **API keys**: Stored in environment variables (never commit to git)
- **CORS**: Configured for specific origins (not wildcard in production)
- **Input validation**: Pydantic models with coordinate range validation
- **Rate limiting**: Implemented on all endpoints (configurable per endpoint)
- **Error handling**: No stack traces leaked in production mode
- **Request size limits**: 10MB maximum request body size
- **Request ID tracking**: All requests have correlation IDs for tracing

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify CSV data file exists (app will start with empty ship list if missing)
- Check environment variables are set
- Check logs for initialization errors
- Review `/health/detailed` endpoint for dependency status

### Frontend can't connect to backend
- Verify `VITE_API_BASE_URL` matches backend URL
- Check CORS settings in backend
- Ensure backend is running
- Check browser console for WebSocket connection errors (falls back to polling)

### Ships not appearing
- Verify CSV file has correct column names
- Check ship positions are in valid ocean coordinates
- Review backend logs for initialization errors
- Check that CSV file is in the root directory
- Verify MAX_SHIPS_DISPLAY setting in .env
- Check WebSocket connection status (should see "WebSocket connected" in console)

### Weather not working
- Verify OpenWeatherMap API key is set in `.env`
- Check API key has sufficient quota
- Review backend logs for API errors
- Check `/health/detailed` for weather service status

### Performance Issues
- Check `/metrics` endpoint for request timings
- Verify rate limits aren't being hit (check response headers)
- Review database connection if using persistence
- Check CSV file size (large files use chunked loading)

### Rate Limiting
- If getting 429 errors, reduce request frequency
- Check rate limit headers in responses: `X-RateLimit-Limit`, `X-RateLimit-Remaining`
- Adjust `RATE_LIMIT_PER_MINUTE` in `.env` if needed

## 📝 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Contact

[Add contact information here]
