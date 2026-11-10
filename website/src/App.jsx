import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Flights from './pages/Flights.jsx'
import Book from './pages/Book.jsx'
import Destinations from './pages/Destinations.jsx'
import About from './pages/About.jsx'
import Crew from './pages/Crew.jsx'
import Page from './Page.jsx'

function NotFound() {
  return <Page eyebrow="404" title="Geen route gevonden" intro="Deze bestemming staat niet op onze kaart." />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/vluchten" element={<Flights />} />
        <Route path="/boeken" element={<Book />} />
        <Route path="/bestemmingen" element={<Destinations />} />
        <Route path="/over-ons" element={<About />} />
        <Route path="/crew" element={<Crew />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
