import { Link, NavLink } from 'react-router-dom'

export default function Nav() {
  return (
    <header className="nav">
      <Link to="/" className="logo">
        <span className="logo-mark" />
        INTERSTELLAR <b>TRAVEL</b>
      </Link>
      <nav>
        <NavLink to="/vluchten">Vluchten</NavLink>
        <NavLink to="/bestemmingen">Bestemmingen</NavLink>
        <NavLink to="/over-ons">Over ons</NavLink>
        <NavLink to="/crew">Crew login</NavLink>
      </nav>
    </header>
  )
}
