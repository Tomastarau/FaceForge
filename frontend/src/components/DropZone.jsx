import { useRef, useState, useCallback } from 'react'

export default function DropZone({ preview, onFile, onCameraClick, onAnalyze, onReset }) {
  const inputRef = useRef(null)
  const [dragging, setDragging] = useState(false)

  const handleFile = useCallback((f) => {
    if (!f || !f.type.startsWith('image/')) return
    onFile(f)
  }, [onFile])

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    handleFile(e.dataTransfer.files[0])
  }, [handleFile])

  const handleDragOver = (e) => { e.preventDefault(); setDragging(true) }
  const handleDragLeave = () => setDragging(false)

  return (
    <section className="upload-section">
      <div
        className={`drop-zone${dragging ? ' dragging' : ''}${preview ? ' has-image' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !preview && inputRef.current.click()}
      >
        {preview ? (
          <img src={preview} alt="Portrait preview" className="preview-img" />
        ) : (
          <div className="drop-prompt">
            <div className="drop-icon">⬡</div>
            <p className="drop-text">Drop a portrait here</p>
            <p className="drop-hint">Frontal · High quality · Single face</p>
          </div>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        style={{ display: 'none' }}
        onChange={(e) => handleFile(e.target.files[0])}
      />

      {!preview && (
        <div className="camera-input-row">
          <button className="camera-link" onClick={onCameraClick}>
            Use camera instead
          </button>
        </div>
      )}

      {preview && (
        <div className="action-row">
          <button className="btn-secondary" onClick={onReset}>Change</button>
          <button className="btn-primary" onClick={onAnalyze}>Forge Character</button>
        </div>
      )}
    </section>
  )
}
