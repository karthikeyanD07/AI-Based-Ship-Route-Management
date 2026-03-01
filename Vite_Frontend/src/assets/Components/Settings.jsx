import React, { useState, useEffect } from 'react';
import Navbar from './Navbar';
import axios from 'axios';
import { API_BASE_URL } from "../../config";
import '../Styles/Dashboard.css'; // Reuse dashboard styles for consistent theme

const Settings = () => {
    const [settings, setSettings] = useState(null);
    const [loading, setLoading] = useState(true);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        try {
            const res = await axios.get(`${API_BASE_URL}/api/settings`);
            setSettings(res.data);
            setLoading(false);
        } catch (err) {
            console.error("Failed to load settings", err);
            setLoading(false);
        }
    };

    const handleFuelChange = (type, value) => {
        setSettings(prev => ({
            ...prev,
            fuel_prices: {
                ...prev.fuel_prices,
                [type]: parseFloat(value)
            }
        }));
    };

    const handleSpeedChange = (value) => {
        setSettings(prev => ({
            ...prev,
            default_speed: parseFloat(value)
        }));
    };

    const saveSettings = async () => {
        try {
            await axios.post(`${API_BASE_URL}/api/settings`, settings);
            setMessage("Settings saved successfully!");
            setTimeout(() => setMessage(null), 3000);
        } catch (err) {
            console.error("Failed to save settings:", err);
            setMessage("Failed to save settings.");
        }
    };

    if (loading) return <div className="dashboard-body" style={{ padding: '100px' }}>Loading...</div>;

    return (
        <div className='dashboard-body'>
            <Navbar />
            <div className="dashboard-container" style={{ display: 'block', maxWidth: '800px' }}>
                <header className="dashboard-header" style={{ marginBottom: '40px' }}>
                    <h1>System Configuration</h1>
                    <span className="last-updated">Global Parameters</span>
                </header>

                {message && (
                    <div style={{
                        padding: '12px',
                        background: message.includes('success') ? 'rgba(158, 206, 106, 0.2)' : 'rgba(247, 118, 142, 0.2)',
                        color: message.includes('success') ? '#9ece6a' : '#f7768e',
                        borderRadius: '8px',
                        marginBottom: '24px',
                        border: '1px solid currentColor'
                    }}>
                        {message}
                    </div>
                )}

                <div className="metric-card" style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#7aa2f7', marginBottom: '20px' }}>⛽ Bunker Fuel Prices (USD/ton)</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                        {Object.entries(settings.fuel_prices).map(([type, price]) => (
                            <div key={type}>
                                <label style={{ display: 'block', marginBottom: '8px', color: '#a9b1d6' }}>{type}</label>
                                <input
                                    type="number"
                                    value={price}
                                    onChange={(e) => handleFuelChange(type, e.target.value)}
                                    style={{
                                        width: '100%',
                                        padding: '10px',
                                        background: '#1a1b26',
                                        border: '1px solid #292e42',
                                        color: '#c0caf5',
                                        borderRadius: '8px'
                                    }}
                                />
                            </div>
                        ))}
                    </div>
                </div>

                <div className="metric-card" style={{ marginBottom: '24px' }}>
                    <h3 style={{ color: '#bb9af7', marginBottom: '20px' }}>⚠️ Operational Defaults</h3>
                    <div>
                        <label style={{ display: 'block', marginBottom: '8px', color: '#a9b1d6' }}>Default Planner Speed (knots)</label>
                        <input
                            type="number"
                            value={settings.default_speed}
                            onChange={(e) => handleSpeedChange(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '10px',
                                background: '#1a1b26',
                                border: '1px solid #292e42',
                                color: '#c0caf5',
                                borderRadius: '8px'
                            }}
                        />
                    </div>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                        onClick={saveSettings}
                        style={{
                            padding: '12px 24px',
                            background: '#7aa2f7',
                            color: '#1a1b26',
                            border: 'none',
                            borderRadius: '8px',
                            fontWeight: '700',
                            cursor: 'pointer',
                            fontSize: '16px'
                        }}
                    >
                        Save Configuration
                    </button>
                </div>

            </div>
        </div>
    );
};

export default Settings;
