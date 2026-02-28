import { useState, useEffect } from 'react'
import './App.css'
import DropZone from './components/DropZone'
import CameraCapture from './components/CameraCapture'
import SliderResults from './components/SliderResults'

export default function App() {
  const [phase, setPhase] = useState('idle')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [results, setResults] = useState(null)
  const [filledResults, setFilledResults] = useState(null)
  const [error, setError] = useState(null)
  const [score, setScore] = useState(null)

  useEffect(() => {
    if (results) {
      const t = setTimeout(() => setFilledResults(results), 80)
      return () => clearTimeout(t)
    } else {
      setFilledResults(null)
    }
  }, [results])

  const handleFile = (f) => {
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setPhase('preview')
    setError(null)
    setResults(null)
  }

  const handleCapture = (blob) => {
    setFile(blob)
    setPreview(URL.createObjectURL(blob))
    setPhase('preview')
  }

  const handleAnalyze = async () => {
    if (!file) return
    setPhase('loading')
    const form = new FormData()
    form.append('file', file, file.name ?? 'capture.jpg')
    try {
      const res = await fetch('http://localhost:8000/upload', { method: 'POST', body: form })
      const data = await res.json()
      setScore(data.score ?? null)
      if (!res.ok || data.status === 'rejected') {
        throw new Error(data.message ?? 'Analysis failed')
      }
      setResults({
        eye_spacing:  1.2,
        nose_width:  -0.4,
        mouth_width:  0.7,
        jaw_width:    0.3,
        face_length: -0.2,
      })
      setPhase('results')
    } catch (err) {
      setError(err.message)
      setPhase('error')
    }
  }

  const handleReset = () => {
    if (preview) URL.revokeObjectURL(preview)
    setPhase('idle')
    setFile(null)
    setPreview(null)
    setResults(null)
    setError(null)
    setScore(null)
  }

  const handleCameraError = (msg) => {
    setError(msg)
    setPhase('error')
  }

  return (
    <div className="forge">
      <header className="forge-header">
        <div className="rune-line" />
        <h1 className="forge-title">FACEFORGE</h1>
        <p className="forge-subtitle">Dragon's Dogma II — Character Imprinter</p>
        <div className="rune-line" />
      </header>

      <main className="forge-main">

        {(phase === 'idle' || phase === 'preview') && (
          <DropZone
            preview={preview}
            onFile={handleFile}
            onCameraClick={() => setPhase('camera')}
            onAnalyze={handleAnalyze}
            onReset={handleReset}
          />
        )}

        {phase === 'camera' && (
          <CameraCapture
            onCapture={handleCapture}
            onCancel={handleReset}
            onError={handleCameraError}
          />
        )}

        {phase === 'loading' && (
          <div className="loading-state">
            <div className="forge-spinner" />
            <p className="loading-text">Reading the face…</p>
          </div>
        )}

        {phase === 'results' && results && (
          <>
            {score !== null && <p className="score-text">Image quality score: {score}/100</p>}
            <SliderResults
              results={results}
              filledResults={filledResults}
              onReset={handleReset}
            />
          </>
        )}

        {phase === 'error' && (
          <div className="error-state">
            {score !== null && <p className="score-text">Image quality score: {score}/100</p>}
            <p className="error-text">⚠ {error}</p>
            <button className="btn-secondary" onClick={handleReset}>Retry</button>
          </div>
        )}

      </main>

      <footer className="forge-footer">
        <p>No data is stored — faces are processed in memory only</p>
      </footer>
    </div>
  )
}
