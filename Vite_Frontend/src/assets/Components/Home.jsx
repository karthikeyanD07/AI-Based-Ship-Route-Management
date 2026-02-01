import React from 'react'
import "../Styles/Home.css"
import Navbar from './Navbar'

const Home = () => {
  return (
    <div>
      <nav>
        <Navbar/>
      </nav>
      <section className='hero'>
        <div className='hero-inner'>
          <h1 className='hero-title'>NeoECDIS</h1>
          <p className='hero-sub'>Precision marine navigation with real‑time AIS, routing, and weather overlays.</p>
          <div className='hero-cta'>
            <a className='cta primary' href='/map'>Open Live Map</a>
            <a className='cta subtle' href='/routes'>Plan a Route</a>
          </div>
        </div>
      </section>
      <section className='kpis'>
        <div className='kpi-card'>
          <div className='kpi-title'>Active Vessels</div>
          <div className='kpi-value'>500</div>
        </div>
        <div className='kpi-card'>
          <div className='kpi-title'>Routes Planned</div>
          <div className='kpi-value'>1,248</div>
        </div>
        <div className='kpi-card'>
          <div className='kpi-title'>Avg. ETA Accuracy</div>
          <div className='kpi-value'>±6 min</div>
        </div>
      </section>
      <section className='quick-grid'>
        <a className='quick-card' href='/map'>
          <div className='qc-title'>Live Traffic</div>
          <div className='qc-sub'>Track global AIS in real time</div>
        </a>
        <a className='quick-card' href='/routes'>
          <div className='qc-title'>Optimize Route</div>
          <div className='qc-sub'>Plan between ports with instant preview</div>
        </a>
        <a className='quick-card' href='/weather'>
          <div className='qc-title'>Sea Conditions</div>
          <div className='qc-sub'>Overlay wind, temperature, and pressure</div>
        </a>
      </section>
    </div>
  )
}

export default Home