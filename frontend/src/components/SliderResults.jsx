const SLIDERS = [
  { key: 'eye_spacing',  label: 'Eye Spacing'  },
  { key: 'nose_width',   label: 'Nose Width'   },
  { key: 'mouth_width',  label: 'Mouth Width'  },
  { key: 'jaw_width',    label: 'Jaw Width'    },
  { key: 'face_length',  label: 'Face Length'  },
]

const toPercent = (val) => Math.max(0, Math.min(100, ((val + 2) / 4) * 100))

export default function SliderResults({ results, filledResults, onReset }) {
  return (
    <section className="results-section">
      <div className="results-header">
        <p className="results-title">Character Sliders</p>
      </div>
      <div className="results-grid">
        {SLIDERS.map(({ key, label }, i) => {
          const val = results[key]
          const pct = filledResults ? toPercent(filledResults[key]) : 0
          return (
            <div className="slider-card" key={key} style={{ animationDelay: `${i * 75}ms` }}>
              <span className="slider-label">{label}</span>
              <div className="slider-track">
                <div className="slider-fill" style={{ width: `${pct}%` }} />
                <div className="slider-thumb" style={{ left: `${pct}%` }} />
              </div>
              <span className="slider-value">
                {val >= 0 ? '+' : ''}{val.toFixed(1)}
              </span>
            </div>
          )
        })}
      </div>
      <button className="btn-secondary" onClick={onReset}>New Portrait</button>
    </section>
  )
}
