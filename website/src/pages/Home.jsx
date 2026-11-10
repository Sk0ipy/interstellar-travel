import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import Scene from '../Scene.jsx'
import Nav from '../Nav.jsx'

// Secret route from the design: click the hidden beacon 3 times to reach the admin login.
const HOTSPOT_CLICKS_NEEDED = 3
const HOTSPOT_CLICK_WINDOW_MS = 1500

export default function Home() {
  const [hover, setHover] = useState(false)
  const clicks = useRef({ count: 0, last: 0 })

  useEffect(() => {
    document.body.style.cursor = hover ? 'pointer' : 'default'
    return () => {
      document.body.style.cursor = 'default'
    }
  }, [hover])

  const handleHotspot = () => {
    const now = Date.now()
    const c = clicks.current
    c.count = now - c.last < HOTSPOT_CLICK_WINDOW_MS ? c.count + 1 : 1
    c.last = now
    if (c.count >= HOTSPOT_CLICKS_NEEDED) {
      c.count = 0
      // /admin is a real server page (Flask), so do a full page load.
      window.location.assign('/admin')
    }
  }

  return (
    <div className="app">
      <div className="canvas-wrap">
        <Scene onHotspotClick={handleHotspot} onHotspotHover={setHover} autoRotate />
      </div>
      <Nav />
      <main className="hero">
        <p className="eyebrow">Lanceerbasis · Interstellar Travel</p>
        <h1>Boek je vlucht naar de sterren</h1>
        <p className="lead">
          Draai de planeet, ontdek de steden en kies je volgende lancering. Elke route begint
          op ons lanceerplatform.
        </p>
        <div className="cta-row">
          <Link className="cta" to="/vluchten">Boek je vlucht</Link>
          <span className="hint">Sleep om te draaien · scroll om te zoomen</span>
        </div>
      </main>
    </div>
  )
}
