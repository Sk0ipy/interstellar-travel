import { useState } from 'react'
import Page from '../Page.jsx'

// Dwaalspoor: a crew login that looks promising but only leads to old, irrelevant data.
export default function Crew() {
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [bookings, setBookings] = useState(null)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    const res = await fetch('/api/crew-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    if (!res.ok) {
      setError((await res.json().catch(() => ({}))).error || 'Inloggen mislukt.')
      return
    }
    const list = await fetch('/api/crew/bookings').then((r) => r.json())
    setBookings(list)
  }

  if (bookings) {
    return (
      <Page eyebrow="Crew" title="Boekingenbeheer" intro="Archief van afgehandelde boekingen. Alleen-lezen.">
        <div className="card">
          <div className="scroll">
            <table>
              <thead><tr><th>Referentie</th><th>Passagier</th><th>Vlucht</th><th>Status</th></tr></thead>
              <tbody>
                {bookings.map((b) => (
                  <tr key={b.reference}>
                    <td>{b.reference}</td><td>{b.passenger}</td><td>{b.flight_code}</td><td>{b.status}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="muted">Geen beheerrechten. Voor systeembeheer neem je contact op met de administrator.</p>
        </div>
      </Page>
    )
  }

  return (
    <Page eyebrow="Crew" title="Crew login" intro="Alleen voor medewerkers van Interstellar Travel.">
      <form className="card narrow-card form" onSubmit={submit}>
        <label>Gebruikersnaam
          <input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} required />
        </label>
        <label>Wachtwoord
          <input type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="cta" type="submit">Inloggen</button>
        <p className="muted small">Nieuw? Gebruik je crew-account met het standaardwachtwoord (Welkom + oprichtingsjaar).</p>
      </form>
    </Page>
  )
}
