import { useState } from 'react'

const toPercent = (val) => Math.max(0, Math.min(100, ((val + 100) / 200) * 100))

export default function SliderResults({ results, filledResults, onReset }) {
  const [openKey, setOpenKey] = useState(null)

  const toggle = (key) => setOpenKey(prev => prev === key ? null : key)

  return (
    <section className="results-section">
      <div className="results-header">
        <p className="results-title">Character Sliders</p>
      </div>
      <div className="results-grid">
        {results.map(({ key, label, description, value }, i) => {
          const pct = filledResults ? toPercent(filledResults[i].value) : 0
          const isOpen = openKey === key
          return (
            <div className="slider-card" key={key} style={{ animationDelay: `${i * 75}ms` }}>
              <div className="slider-row" onClick={() => toggle(key)} style={{ cursor: 'pointer' }}>
                <span className="slider-label">{label}</span>
                <div className="slider-track">
                  <div className="slider-fill" style={{ width: `${pct}%` }} />
                  <div className="slider-thumb" style={{ left: `${pct}%` }} />
                </div>
                <span className="slider-value">
                  {value >= 0 ? '+' : ''}{value}
                </span>
              </div>
              <div className={`slider-desc-wrapper${isOpen ? ' open' : ''}`}>
                <p className="slider-description">{description}</p>
              </div>
            </div>
          )
        })}
      </div>
      <button className="btn-secondary" onClick={onReset}>Nouveau portrait</button>
    </section>
  )
}
