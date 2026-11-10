import Nav from './Nav.jsx'

// Shared shell for the content pages: scrolling starfield background + navigation + footer.
export default function Page({ eyebrow, title, intro, children }) {
  return (
    <div className="page">
      <Nav />
      <main className="page-body">
        <p className="eyebrow">{eyebrow}</p>
        <h1 className="page-title">{title}</h1>
        {intro && <p className="lead">{intro}</p>}
        {children}
      </main>
      <footer className="footer">© 2026 Interstellar Travel · Lanceerbasis Aurora</footer>
    </div>
  )
}
