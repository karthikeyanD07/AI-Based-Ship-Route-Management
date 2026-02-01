# Architecture Documentation

## System Overview

The AI Ship Route Management System is a full-stack application consisting of:

1. **Backend**: FastAPI-based REST API with real-time ship tracking
2. **Frontend**: React SPA with interactive maps and route visualization

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ ShipMap  │  │ Routes   │  │ Weather  │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │             │                      │
│       └─────────────┴─────────────┘                      │
│                    │                                      │
│              HTTP/REST API                                │
└────────────────────┼─────────────────────────────────────┘
                     │
┌────────────────────┼─────────────────────────────────────┐
│              Backend (FastAPI)                           │
│  ┌──────────────────────────────────────────┐           │
│  │           API Routes Layer                │           │
│  │  /api/ship-traffic, /api/routes, etc.    │           │
│  └──────────────┬───────────────────────────┘           │
│                 │                                        │
│  ┌──────────────┴──────────────┐                       │
│  │      Services Layer          │                       │
│  │  - ShipService               │                       │
│  │  - RouteService              │                       │
│  │  - WeatherService           │                       │
│  └──────────────┬──────────────┘                       │
│                 │                                        │
│  ┌──────────────┴──────────────┐                       │
│  │      Utils Layer            │                       │
│  │  - Ocean Detection          │                       │
│  │  - Route Algorithms         │                       │
│  └──────────────┬──────────────┘                       │
│                 │                                        │
│  ┌──────────────┴──────────────┐                       │
│  │      Data Layer            │                       │
│  │  - CSV Files                │                       │
│  │  - Database (Optional)      │                       │
│  └─────────────────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

## Backend Architecture

### Layer Structure

1. **Routes Layer** (`backend/app/routes/`)
   - HTTP endpoint definitions
   - Request/response validation
   - Error handling

2. **Services Layer** (`backend/app/services/`)
   - Business logic
   - Data processing
   - External API integration

3. **Models Layer** (`backend/app/models/`)
   - Pydantic schemas for validation
   - SQLAlchemy models for database

4. **Utils Layer** (`backend/app/utils/`)
   - Reusable algorithms
   - Helper functions
   - GIS operations

### Key Components

#### Ship Service
- Manages ship positions in memory
- Updates positions based on speed and course
- Handles CSV data loading and normalization

#### Route Service
- Optimizes routes using great-circle calculations
- Ensures ocean-safe paths
- Calculates distances and ETAs

#### Ocean Detection
- Determines if coordinates are in ocean/water
- Uses geographic heuristics
- Can be extended with proper GIS data

## Frontend Architecture

### Component Structure

```
App.jsx
├── ErrorBoundary
└── Router
    ├── Home
    ├── ShipMap
    ├── RoutesOptimization
    ├── Weather
    ├── Dashboard
    └── Navigation
```

### State Management

- Local component state with React hooks
- API calls using fetch/axios
- Polling for real-time updates (can be upgraded to WebSockets)

### Map Integration

- React-Leaflet for map components
- Multiple tile layers
- Custom markers and popups
- Interactive route visualization

## Data Flow

### Ship Tracking Flow

1. Backend loads CSV data on startup
2. ShipService initializes ship positions
3. Background task updates positions every 3 seconds
4. Frontend polls `/api/ship-traffic` every 5 seconds
5. Map updates with new positions

### Route Optimization Flow

1. User selects start/end ports in frontend
2. Frontend sends POST to `/api/get_optimized_route/`
3. RouteService calculates optimal path
4. Ocean detection ensures water-only route
5. Response includes route points and metadata
6. Frontend visualizes route on map

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **SQLAlchemy**: ORM (optional)
- **GeoAlchemy2**: Spatial database support
- **Geopy**: Geodesic calculations
- **Shapely**: GIS operations
- **Pandas**: Data processing

### Frontend
- **React 19**: UI framework
- **Vite**: Build tool
- **React Router**: Navigation
- **React-Leaflet**: Map integration
- **Axios**: HTTP client
- **Material-UI**: UI components

## Scalability Considerations

### Current Limitations
- In-memory ship positions (not persistent)
- Polling-based updates (not real-time)
- Single-threaded ship updates

### Future Improvements
- Database persistence for ship positions
- WebSocket support for real-time updates
- Redis for caching and pub/sub
- Horizontal scaling with load balancer
- Message queue for ship updates

## Security Architecture

### Current Implementation
- Environment variables for secrets
- CORS configuration
- Input validation via Pydantic
- Error handling

### Recommended Enhancements
- JWT authentication
- Rate limiting (infrastructure ready)
- API key validation
- HTTPS in production
- Input sanitization

## Deployment Architecture

### Development
- Single server running both frontend and backend
- Local database (optional)

### Production (Recommended)
```
┌─────────────┐
│   Nginx     │  Reverse proxy, static files
└──────┬──────┘
       │
┌──────┴──────┐
│   Backend   │  FastAPI with uvicorn
│   (FastAPI) │
└──────┬──────┘
       │
┌──────┴──────┐
│  PostgreSQL │  Database with PostGIS
│  + PostGIS  │
└─────────────┘
```

## Performance Optimization

### Backend
- LRU caching for routes
- Efficient CSV loading
- Async operations where possible

### Frontend
- Component memoization
- Lazy loading (can be added)
- Code splitting (can be added)

## Monitoring and Logging

### Current
- Basic error logging
- Console output

### Recommended
- Structured logging (structlog)
- Error tracking (Sentry)
- Performance monitoring (Prometheus)
- Health check endpoints
