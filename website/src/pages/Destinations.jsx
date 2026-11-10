import Page from '../Page.jsx'
import useFetch from '../useFetch.js'

export default function Destinations() {
  const { data, error, loading } = useFetch('/api/destinations')
  return (
    <Page
      eyebrow="Reisoverzicht"
      title="Bestemmingen"
      intro="Steden, kolonies en buitenposten over de hele planeet. Draai de planeet op de homepage om ze te zien."
    >
      {loading && <p className="muted">Bestemmingen laden…</p>}
      {error && <p className="error">Kon de bestemmingen niet laden.</p>}
      <div className="cards">
        {data?.map((d) => (
          <article key={d.slug} className={`card dest${d.status === 'open' ? '' : ' locked'}`}>
            <div className="card-head">
              <span className="region">{d.region}</span>
              <span className={`badge ${d.status === 'open' ? 'ok' : 'closed'}`}>
                {d.status === 'open' ? 'Open' : 'Gesloten'}
              </span>
            </div>
            <h3>{d.name}</h3>
            <p>{d.description}</p>
            <p className="muted">Reistijd vanaf de lanceerbasis: {d.distance}</p>
          </article>
        ))}
      </div>
    </Page>
  )
}
