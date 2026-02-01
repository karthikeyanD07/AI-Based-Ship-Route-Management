import React, { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, Marker, Polyline, ZoomControl } from "react-leaflet";
import axios from "axios";
import L from "leaflet";
import "../Styles/Routes.css";
import SP from "../Img/ship.png";
import Navbar from "./Navbar";
import { API_BASE_URL } from "../../config";

const shipIcon = new L.Icon({
  iconUrl: SP,
  iconSize: [40, 40],
});

const portLocations = {
  "Port A": [33.7405, -118.2519],
  "Port B": [40.6728, -74.1536],
  "Port C": [29.7305, -95.0892],
  "Port D": [25.7785, -80.1826],
  "Port E": [32.0835, -81.0998],
  "Port F": [47.6019, -122.3381],
};

const Routess = () => {
  const [shipId, setShipId] = useState("");
  const [startPort, setStartPort] = useState("");
  const [endPort, setEndPort] = useState("");
  const [route, setRoute] = useState([]);
  const [summary, setSummary] = useState(null);
  const [shipPosition, setShipPosition] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState(null);
  const animationIntervalRef = useRef(null);

  // Cleanup animation interval on unmount
  useEffect(() => {
    return () => {
      if (animationIntervalRef.current) {
        clearInterval(animationIntervalRef.current);
      }
    };
  }, []);

  const getOptimizedRoute = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/get_optimized_route/`, {
        ship_id: shipId,
        start: startPort,
        end: endPort,
      });

      const optimizedRoute = response.data.optimized_route;
      if (optimizedRoute && Array.isArray(optimizedRoute) && optimizedRoute.length > 0) {
        // Validate route points
        const validRoute = optimizedRoute.filter(
          point => Array.isArray(point) && point.length === 2 && 
          typeof point[0] === 'number' && typeof point[1] === 'number' &&
          point[0] >= -90 && point[0] <= 90 && point[1] >= -180 && point[1] <= 180
        );
        
        if (validRoute.length === 0) {
          throw new Error("Invalid route data received from server");
        }
        
        setRoute(validRoute);
        setShipPosition(validRoute[0]);
        animateShip(validRoute);
        // Use backend-provided distance and ETA if available
        const distanceKm = response.data.distance_km || totalDistanceKm(validRoute);
        const etaHours = response.data.estimated_time_hours || 
          ((distanceKm / 1.852) / 12).toFixed(1); // 12 knots average
        setSummary({ 
          distanceKm: distanceKm.toFixed(1), 
          etaHours: typeof etaHours === 'number' ? etaHours.toFixed(1) : etaHours 
        });
      } else {
        throw new Error("Empty or invalid route received");
      }
    } catch (error) {
      console.error("Error fetching route:", error);
      setError(error.response?.data?.detail || error.message || "Failed to fetch route");
    } finally {
      setLoading(false);
      setShowForm(false);
    }
  };

  function haversineKm(a, b){
    const toRad = (x) => (x * Math.PI) / 180;
    const R = 6371;
    const dLat = toRad(b[0]-a[0]);
    const dLon = toRad(b[1]-a[1]);
    const lat1 = toRad(a[0]);
    const lat2 = toRad(b[0]);
    const h = Math.sin(dLat/2)**2 + Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2;
    return 2*R*Math.asin(Math.sqrt(h));
  }
  function totalDistanceKm(points){
    let d = 0;
    for(let i=1;i<points.length;i++) d += haversineKm(points[i-1], points[i]);
    return d;
  }

  const animateShip = (optimizedRoute) => {
    // Clear any existing animation
    if (animationIntervalRef.current) {
      clearInterval(animationIntervalRef.current);
    }
    
    let index = 0;
    animationIntervalRef.current = setInterval(() => {
      if (index < optimizedRoute.length) {
        setShipPosition([...optimizedRoute[index]]);
        index++;
      } else {
        if (animationIntervalRef.current) {
          clearInterval(animationIntervalRef.current);
          animationIntervalRef.current = null;
        }
      }
    }, 2000);
  };

  return (
    <div>
      <Navbar />
      <div className="Route-Map">
        <h2 className="route-title">Ship Route Optimization & Simulation</h2>
        {error && (
          <div className="error" style={{color: "red", padding: "10px", margin: "10px"}}>
            {error}
          </div>
        )}
        {summary && (
          <div className="route-summary">Distance: {summary.distanceKm} km · ETA: {summary.etaHours} h</div>
        )}

        {/* Button to show the overlay form */}
        <button className="open-form-btn" onClick={() => setShowForm(true)}>Open Form</button>

        {/* Overlay Form */}
        {showForm && (
          <div className="overlay">
            <div className="form-container">
              <button className="close-form-btn" onClick={() => setShowForm(false)}>Close</button>
              <form className="route-form" onSubmit={(e) => { e.preventDefault(); getOptimizedRoute(); }}>
                <input
                  type="text"
                  className="route-input"
                  placeholder="Ship ID (MMSI)"
                  value={shipId}
                  onChange={(e) => setShipId(e.target.value)}
                  required
                />
                <select className="route-select" value={startPort} onChange={(e) => setStartPort(e.target.value)} required>
                  <option value="">Select Start Port</option>
                  {Object.keys(portLocations).map((port) => (
                    <option key={port} value={port}>{port}</option>
                  ))}
                </select>
                <select className="route-select" value={endPort} onChange={(e) => setEndPort(e.target.value)} required>
                  <option value="">Select End Port</option>
                  {Object.keys(portLocations).map((port) => (
                    <option key={port} value={port}>{port}</option>
                  ))}
                </select>
                <button type="submit" className="route-submit-btn" disabled={loading}>
                  {loading ? "Calculating…" : "Get Optimized Route"}
                </button>
              </form>
            </div>
          </div>
        )}

        {/* Map */}
        <MapContainer center={[30, -95]} zoom={4} style={{ height: "80vh", width: "80vw" }} zoomControl={false}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {Object.entries(portLocations).map(([port, coords]) => (
            <Marker key={port} position={coords} />
          ))}
          {shipPosition && Array.isArray(shipPosition) && shipPosition.length === 2 && (
            <Marker position={shipPosition} icon={shipIcon} />
          )}
          {route.length > 1 && Array.isArray(route[0]) && (
            <Polyline positions={route} color="blue" />
          )}
          <ZoomControl position="bottomright" />
        </MapContainer>
        
      </div>
    </div>
  );
};

export default Routess;
