# 🚢 NeoECDIS: AI-Based Ship Route Management System

> **A production-ready, physics-aware maritime decision support system.**
>
> *Operational Intelligence for the Next Generation of Fleet Management.*

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [Installation & Setup](#-installation--setup) (start here!)
5. [Usage Guide](#-usage-guide)
6. [Business & Future Roadmap](#-business--future-roadmap)
7. [License](#-license)

---

## 🎯 Project Overview

NeoECDIS is a comprehensive maritime navigation platform designed to bridge the gap between static navigational charts and dynamic, operational decision-making. Unlike traditional ECDIS (Electronic Chart Display and Information Systems), NeoECDIS integrates **live traffic**, **weather intelligence**, and **economics-driven route optimization** into a single glass pane.

**Value Proposition:**
- **For Captains:** Real-time situational awareness with weather overlays and traffic data.
- **For Operators:** Cost-optimized routing that balances fuel consumption (CO₂) against time-to-arrival.
- **For Developers:** A modern, API-first architecture built on Python/FastAPI and React.

---

## 🚀 Key Features

| Module | Feature | Capability |
| :--- | :--- | :--- |
| **Smart Navigator** | **Live Traffic Interaction** | Real-time map with moving ships, popup status (Speed, Course), and traffic density visualization. |
| | **Weather Integration** | Visual overlays for wind, pressure, and wave height (OpenWeather integration). |
| | **Tactical Planning** | "Click-to-Plan" allowing instant route generation from any map location. |
| **Route Optimizer** | **Physics-Based Engine** | Calculates fuel burn using the **Cubic Law of Propulsion** ($v^3$) for accurate emission estimates. |
| | **Multi-Strategy Routing** | Generates 3 comparison routes: **Fastest** (Time priority), **Balanced** (Efficiency), and **Greenest** (Lowest CO₂). |
| | **Real-Time Savings** | Instantly displays projected FO consumption and CO₂ reduction (e.g., "Slowing by 2kts saves 15% fuel"). |
| **Fleet Dashboard** | **Command Center** | Live counters for Active Fleet, Total Emissions, and Average Fleet Speed. |
| | **Global Settings** | Configurable business logic (Fuel Prices per Ton, Default Cruising Speed) that persists across the application. |

---

## 🛠 Technology Stack

### Backend (Python/FastAPI)
- **FastAPI**: High-performance async API framework.
- **Pydantic**: Strict data validation and settings management.
- **Physics Engine**: Custom logic for hydrodynamic resistance and fuel curve modeling.
- **Security**: Robust error handling, rigorous input validation, and secure headers.
- **Testing**: Comprehensive functional tests (`connectivity_check.py`) and unit tests.


### Frontend (React/Vite)
- **Vite**: Next-gen frontend tooling.
- **React 19**: Modern component architecture.
- **Material UI (MUI)**: Professional, responsive design system (Tokyo Night theme).
- **Leaflet/React-Leaflet**: Interactive mapping engine with custom layers.

### System Architecture

```mermaid
graph TD
    Client[Frontend (React/Vite)] -->|HTTP/REST| API[Backend API (FastAPI)]
    Client -->|WebSocket| WS[Real-time Updates]
    API -->|Read/Write| DB[(PostgreSQL + PostGIS)]
    API -->|Fetch| Weather[OpenWeatherMap API]
    API -->|Calc| Physics[Physics Engine (v^3 Law)]
    WS -->|Push| Client
```

### Key Data Flows
1.  **Ship Tracking**: Backend loads CSV -> Service updates positions (in-memory) -> Frontend polls/subscribes -> Map updates.
2.  **Route Optimization**: User Input -> API Request -> Ocean Detection (Land Mask) -> Pathfinding (A*) -> Physics Engine -> Response.


---

## 📦 Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & npm
- **Git**

### 1. Backend Setup
```bash
# Clone the repository
git clone https://github.com/karthikeyanD07/AI-Based-Ship-Route-Management.git
cd AI-Based-Ship-Route-Management

# Create Virtual Environment
# Windows:
python -m venv venv
venv\Scripts\activate
# Mac/Linux:
# python3 -m venv venv && source venv/bin/activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd Vite_Frontend
npm install
cd ..
```

### 3. Environment Configuration
Create a `.env` file in the root directory (optional, defaults provided in safe mode):
```env
OPENWEATHER_API_KEY=your_key_here
```

### 4. Running the Application
**Terminal 1 (Backend):**
```bash
venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd Vite_Frontend
npm run dev
```

> **Access the App:**
> *   Frontend: `http://localhost:5173`
> *   API Docs: `http://localhost:8000/docs`

---

## 🎮 Usage Guide

### The "Captain's Workflow"
1.  **Monitor**: Start at the **Dashboard** to see fleet status.
2.  **Discover**: Switch to **Map** (Navigator) to view live traffic and weather. Click any ship to inspect it.
3.  **Plan**: Click "Plan Route" on the map or go to **Routes**.
4.  **Optimize**: Select *Start Port* (Singapore) and *End Port* (Rotterdam). Click **Compare Routes**.
5.  **Decide**: Review the comparison table. Note how the "Balanced" route creates massive savings vs the "Fastest" route.
6.  **Configure**: Go to **Settings** to update Fuel Prices (HFO/MGO) and see the recalculations update instantly.

---

## 💼 Business & Future Roadmap

**Current Status:** Candidate Release (Stable Prototype)

### Strategic Gaps & Opportunities
While technically robust, the system currently operates as a standalone tool. The roadmap focuses on bridging the gap to commercial viability:

1.  **Monetization Strategy**: Transition to a Freemium SaaS model for SMB maritime operators (yachts, fishing fleets).
2.  **Enterprise Features**: Multi-tenancy, Role-Based Access Control (RBAC), and Audit Logging.
3.  **Regulatory Compliance**: Roadmap to support IHO S-57/S-63 chart standards for official navigation use.

### Upcoming Features
*   **Voyage Simulation**: 1000x speed replay of planned routes.
*   **AI Captain Assistant**: Chat-based interface for route explanation ("Why avoid the Red Sea?").
*   **Offline Mode**: Essential for vessels with intermittent satellite connectivity.

---

## 📄 License

This project is licensed for educational and demonstration purposes.
*   **AIS Data**: Simulated/Demo data (or live via API if configured).
*   **Charts**: OpenSeaMap (OpenStreetMap contributors).

---
*Built with ❤️ by the NeoECDIS Team*
