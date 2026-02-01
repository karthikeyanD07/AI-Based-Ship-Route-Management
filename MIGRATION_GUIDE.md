# Migration Guide: Old to New Structure

This guide helps you migrate from the old project structure to the new organized structure.

## Key Changes

### Backend Structure

**Old:**
- `main.py` - Single file with all logic
- `ais_api.py` - Duplicate/conflicting API
- `Test.py` - Test route optimization

**New:**
- `backend/app/main.py` - Clean entry point
- `backend/app/routes/` - Organized API endpoints
- `backend/app/services/` - Business logic
- `backend/app/models/` - Data models
- `backend/app/utils/` - Utilities

### API Endpoints

**Old endpoints:**
- `GET /ship-traffic` → **New:** `GET /api/ship-traffic`
- `GET /ship/{mmsi}` → **New:** `GET /api/ship/{mmsi}`
- `POST /get_optimized_route/` → **New:** `POST /api/get_optimized_route/`

### Configuration

**Old:** Hardcoded values in code
**New:** Environment variables via `.env` file

### Frontend

**Old:**
- Hardcoded API URLs
- Hardcoded API keys
- Mixed vanilla Leaflet and React-Leaflet

**New:**
- Environment-based configuration
- Proper React-Leaflet usage
- Error boundaries

## Migration Steps

1. **Backup your data**
   ```bash
   cp trip9.csv trip9.csv.backup
   cp final_ship_routes.csv final_ship_routes.csv.backup
   ```

2. **Update environment variables**
   - Copy `.env.example` to `.env`
   - Add your API keys
   - Configure database if using

3. **Update frontend configuration**
   - Copy `Vite_Frontend/.env.example` to `Vite_Frontend/.env`
   - Set `VITE_API_BASE_URL` to match backend

4. **Test the new structure**
   - Start backend: `uvicorn backend.app.main:app --reload`
   - Start frontend: `cd Vite_Frontend && npm run dev`
   - Verify all features work

5. **Remove old files (after verification)**
   - `main.py` (old)
   - `ais_api.py` (old)
   - `Test.py` (if not needed)

## Breaking Changes

1. **API prefix**: All endpoints now use `/api/` prefix
2. **Response format**: Route optimization now includes `distance_km` and `estimated_time_hours`
3. **Configuration**: Must use environment variables

## Compatibility

The new structure maintains backward compatibility for:
- CSV data file formats
- Port names (Port A-F)
- Basic functionality

## Need Help?

If you encounter issues:
1. Check the README.md for setup instructions
2. Review ARCHITECTURE.md for system design
3. Verify environment variables are set correctly
4. Check backend logs for errors
