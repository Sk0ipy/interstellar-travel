import Page from '../Page.jsx'
import useFetch from '../useFetch.js'

export default function About() {
  const { data } = useFetch('/api/about')
  return (
    <Page
      eyebrow="Over ons"
      title="Reizen tussen de sterren"
      intro="Interstellar Travel is sinds 2024 het reisbureau van de planeet voor raketreizen naar steden, kolonies en buitenposten."
    >
      <div className="about-grid">
        <section className="card">
          <h3>Ons verhaal</h3>
          <p>
            Wat begon met één lanceerplatform en één raket is uitgegroeid tot een netwerk van
            steden, een monorail en dagelijkse vluchten. Wij zorgen dat je veilig en comfortabel
            op je bestemming aankomt.
          </p>
          <p>
            Ons team bestaat uit piloten, grondpersoneel, boekingsmedewerkers en
            systeembeheerders die dag en nacht klaarstaan.
          </p>
        </section>
        <section className="card team">
          {data?.team_image && <img src={data.team_image} alt="Het Interstellar Travel-team" />}
          <p className="muted">Het team op het lanceerplatform.</p>
        </section>
      </div>
    </Page>
  )
}
