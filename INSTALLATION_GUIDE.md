# 🚀 Complete Installation Guide - AI Ship Route Management System

## Prerequisites

Before starting, ensure you have:
- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **Git** (optional, for cloning)

---

## 📦 Backend Installation (Python)

### Step 1: Navigate to Project Directory
```bash
cd "C:\Users\KARTHIKEYAN D\Desktop\AI-SHIP-ROUTE-RECOVERY"
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Upgrade pip
```bash
python -m pip install --upgrade pip
```

### Step 4: Install All Backend Dependencies
```bash
pip install fastapi==0.119.0 uvicorn[standard]==0.37.0 python-multipart==0.0.12 sqlalchemy==2.0.36 alembic==1.14.0 psycopg2-binary==2.9.10 geoalchemy2==0.15.0 pandas==2.2.3 numpy==2.1.3 shapely==2.0.5 geopandas==1.1.2 geopy==2.4.1 pyproj==3.7.0 python-jose[cryptography]==3.3.0 passlib[bcrypt]==1.7.4 python-dotenv==1.0.1 slowapi==0.1.9 httpx==0.27.2 aiohttp==3.11.3 pydantic==2.9.2 pydantic-settings==2.6.1 python-dateutil==2.9.0.post0 redis==5.0.1 pytest==8.3.3 pytest-asyncio==0.24.0 pytest-cov==5.0.0 pytest-mock==3.14.0 faker==28.0.0 locust==2.24.1 bleach==6.1.0 cryptography==43.0.1 structlog==24.2.0 python-json-logger==2.0.7 prometheus-client==0.20.0
```

**OR use requirements.txt (Easier):**
```bash
pip install -r requirements.txt
```

---

## 🎨 Frontend Installation (Node.js/React)

### Step 1: Navigate to Frontend Directory
```bash
cd Vite_Frontend
```

### Step 2: Install All Frontend Dependencies
```bash
npm install
```

**OR install manually:**
```bash
npm install react@19.0.0 react-dom@19.0.0 @emotion/react@11.14.0 @emotion/styled@11.14.0 @mui/icons-material@6.4.8 @mui/material@6.4.8 axios@1.8.4 leaflet@1.9.4 react-leaflet@5.0.0 react-router-dom@7.4.0 vite@6.2.0 @vitejs/plugin-react-swc@3.8.0
```

### Step 3: Return to Project Root
```bash
cd ..
```

---

## ✅ Verification Commands

### Verify Backend Setup
```bash
# Activate venv first (if not already activated)
venv\Scripts\activate

# Check Python version
python --version

# Check installed packages
pip list

# Test backend import
python -c "from backend.app.services.route_service import route_service; print('✓ Backend imports work')"
```

### Verify Frontend Setup
```bash
cd Vite_Frontend
npm list
cd ..
```

---

## 🚀 Running the Application

### Terminal 1: Start Backend
```bash
# Activate virtual environment
venv\Scripts\activate

# Run backend server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:** `http://localhost:8000`

### Terminal 2: Start Frontend
```bash
cd Vite_Frontend
npm run dev
```

**Frontend will be available at:** `http://localhost:5173`

---

## 📋 Copy-Paste Installation Script (Windows)

**Complete one-liner for backend:**
```powershell
cd "C:\Users\KARTHIKEYAN D\Desktop\AI-SHIP-ROUTE-RECOVERY" ; python -m venv venv ; venv\Scripts\activate ; python -m pip install --upgrade pip ; pip install -r requirements.txt
```

**Complete one-liner for frontend:**
```powershell
cd "C:\Users\KARTHIKEYAN D\Desktop\AI-SHIP-ROUTE-RECOVERY\Vite_Frontend" ; npm install ; cd ..
```

---

## 🐧 Copy-Paste Installation Script (Linux/Mac)

**Complete one-liner for backend:**
```bash
cd ~/Desktop/AI-SHIP-ROUTE-RECOVERY && python3 -m venv venv && source venv/bin/activate && python -m pip install --upgrade pip && pip install -r requirements.txt
```

**Complete one-liner for frontend:**
```bash
cd ~/Desktop/AI-SHIP-ROUTE-RECOVERY/Vite_Frontend && npm install && cd ..
```

---

## 🔧 Troubleshooting

### Issue: Python not found
**Solution:**
```bash
# Windows: Install Python from python.org
# Or use Microsoft Store version
```

### Issue: npm not found
**Solution:**
```bash
# Download Node.js from nodejs.org
# Includes npm automatically
```

### Issue: Permission errors on Windows
**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: geopandas installation fails
**Solution:**
```bash
# Install GDAL first (Windows)
pip install pipwin
pipwin install gdal
pipwin install fiona
pip install geopandas
```

---

## 📦 Additional Optional Dependencies

### For Production Deployment:
```bash
pip install gunicorn supervisor nginx-config-generator
```

### For Advanced GIS Features:
```bash
pip install fiona rtree pyogrio
```

### For Database Management:
```bash
pip install pgcli psycopg2-binary
```

---

## 🧪 Test Backend Installation
```bash
# Activate venv
venv\Scripts\activate

# Run tests
pytest tests/ -v

# Test specific modules
python -c "from backend.app.data.ports_database import port_db; print(f'✓ {len(port_db.get_all_ports())} ports loaded')"

python -c "from backend.app.utils.emissions import emissions_calc; result = emissions_calc.calculate_co2_emissions(1000, 12.0); print(f'✓ Emissions: {result[\"total_co2_tonnes\"]} tonnes CO2')"
```

---

## 📝 Environment Variables Setup

Create `.env` file in project root:
```bash
# Copy from example
cp .env.example .env

# OR create manually with:
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/dbname
OPENWEATHER_API_KEY=your-api-key
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🎯 Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Virtual environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Environment variables configured
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Can access http://localhost:8000/docs (FastAPI docs)
- [ ] Can access http://localhost:5173 (React app)

---

## 🔗 Useful Links

- **Backend API Docs:** http://localhost:8000/docs
- **Backend Metrics:** http://localhost:8000/metrics
- **Backend Health:** http://localhost:8000/health
- **Frontend:** http://localhost:5173

---

## 👥 For Your Teammate

**Send them this file (`INSTALLATION_GUIDE.md`) plus:**
1. `requirements.txt`
2. `package.json`
3. Any `.env.example` file

**They can run:**
```bash
# Backend
cd AI-SHIP-ROUTE-RECOVERY
python -m venv venv
venv\Scripts\activate  # Windows
# OR: source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Frontend
cd Vite_Frontend
npm install

# Run
# Terminal 1: uvicorn main:app --reload
# Terminal 2: cd Vite_Frontend && npm run dev
```

Done! 🎉
