import { Link } from 'react-router-dom'
import Page from '../Page.jsx'
import useFetch from '../useFetch.js'

export default function Flights() {
  const { data, error, loading } = useFetch('/api/flights')
  return (
    <Page
      eyebrow="Vertrekoverzicht"
      title="Beschikbare vluchten"
      intro="Elke vlucht vertrekt vanaf ons lanceerplatform. Kies je bestemming en boek je stoel."
    >
      {loading && <p className="muted">Vluchten laden…</p>}
      {error && <p className="error">Kon de vluchten niet laden.</p>}
      <div className="cards">
        {data?.map((f) => (
          <article key={f.code} className={`card flight${f.bookable ? '' : ' locked'}`}>
            <div className="card-head">
              <span className="code">{f.code}</span>
              <span className={`badge ${f.bookable ? 'ok' : 'closed'}`}>
                {f.bookable ? (f.seats > 0 ? `${f.seats} stoelen` : 'Vol') : 'Gesloten vracht'}
              </span>
            </div>
            <h3>{f.destination}</h3>
            <dl>
              <div><dt>Vertrek</dt><dd>{f.departs}</dd></div>
              <div><dt>Reistijd</dt><dd>{f.duration}</dd></div>
              <div><dt>Prijs</dt><dd>{f.bookable ? `€ ${f.price}` : '—'}</dd></div>
            </dl>
            {f.bookable && f.seats > 0 ? (
              <Link className="cta small" to={`/boeken?vlucht=${f.code}`}>Boek deze vlucht</Link>
            ) : (
              <span className="cta small disabled">{f.bookable ? 'Uitverkocht' : 'Niet te boeken'}</span>
            )}
          </article>
        ))}
      </div>
    </Page>
  )
}
