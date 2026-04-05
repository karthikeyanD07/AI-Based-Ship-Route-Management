# AI-Based Ship Route Management (NeoECDIS)

A professional maritime intelligence system for real-time ship tracking, route optimization, and carbon footprint analysis.

## 🚀 Quick Start

Ensure you have Python 3.10+ and Node.js installed.

### 1. Backend Setup
Running the standalone, single-file backend for maximum stability.
```powershell
pip install fastapi uvicorn pydantic pandas numpy searoute geopy httpx
python main.py
```
*Backend runs on: http://127.0.0.1:8000*

### 2. Frontend Setup
```powershell
cd Vite_Frontend
npm install
npm run dev -- --port 5174
```
*Frontend runs on: http://localhost:5174*

## 🚢 Features
- **Command Center (Dashboard):** Live fleet metrics, global CO2 tracking, and voyage history.
- **Voyage Optimizer:** Compare 'Fastest', 'Balanced', and 'Greenest' routes with emissions analysis.
- **Weather Routing:** Tactical weather-aware route planning with segment-by-segment danger analysis.
- **Smart Navigator:** High-fidelity nautical chart with live radar pings and vessel search.

## 📁 Project Structure
- `main.py`: Standalone FastAPI backend server.
- `Vite_Frontend/`: React/Vite web application.
- `voyage_history.json`: Persistent storage for route optimizations.
- `trip9.csv`: Maritime dataset for route analysis.

## 🛠 Tech Stack
- **Frontend:** React, Vite, Leaflet, Material UI.
- **Backend:** FastAPI, Pydantic, Searoute, Geopy.
- **Data:** In-memory state with JSON persistence for history.
