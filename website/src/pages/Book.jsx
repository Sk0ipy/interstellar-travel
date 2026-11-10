import { useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import Page from '../Page.jsx'
import useFetch from '../useFetch.js'

export default function Book() {
  const [params] = useSearchParams()
  const { data: flights } = useFetch('/api/flights')
  const [form, setForm] = useState({ name: '', email: '', flight: params.get('vlucht') || '' })
  const [status, setStatus] = useState({ kind: 'idle' })

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setStatus({ kind: 'busy' })
    const res = await fetch('/api/book', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    const body = await res.json().catch(() => ({}))
    setStatus(res.ok ? { kind: 'done', ...body } : { kind: 'error', message: body.error || 'Boeken mislukt.' })
  }

  return (
    <Page eyebrow="Reservering" title="Boek je vlucht" intro="Vul je gegevens in. Je ontvangt direct een boekingsreferentie.">
      {status.kind === 'done' ? (
        <div className="card narrow-card">
          <h3>Boeking bevestigd</h3>
          <p>Je referentie voor {status.flight}:</p>
          <p className="ref">{status.reference}</p>
          <div className="cta-row">
            <a className="cta small" href={`/api/bookings/manifest?file=${status.reference}.txt`} target="_blank" rel="noreferrer">
              Download boekingsbestand
            </a>
            <Link className="cta small" to="/vluchten">Terug naar de vluchten</Link>
          </div>
        </div>
      ) : (
        <form className="card narrow-card form" onSubmit={submit}>
          <label>Naam
            <input value={form.name} onChange={set('name')} required />
          </label>
          <label>E-mailadres
            <input type="email" value={form.email} onChange={set('email')} required />
          </label>
          <label>Vlucht
            <select value={form.flight} onChange={set('flight')} required>
              <option value="">Kies een vlucht…</option>
              {flights?.filter((f) => f.bookable).map((f) => (
                <option key={f.code} value={f.code}>{f.code} · {f.destination}</option>
              ))}
            </select>
          </label>
          {status.kind === 'error' && <p className="error">{status.message}</p>}
          <button className="cta" type="submit" disabled={status.kind === 'busy'}>
            {status.kind === 'busy' ? 'Bezig…' : 'Bevestig boeking'}
          </button>
        </form>
      )}
    </Page>
  )
}
