import { useEffect, useState } from 'react'

// Small helper: GET a JSON endpoint and track loading / error state.
export default function useFetch(url) {
  const [state, setState] = useState({ data: null, error: null, loading: true })
  useEffect(() => {
    let alive = true
    fetch(url)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(`Fout ${r.status}`))))
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((error) => alive && setState({ data: null, error, loading: false }))
    return () => {
      alive = false
    }
  }, [url])
  return state
}
