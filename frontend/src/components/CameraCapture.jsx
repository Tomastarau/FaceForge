import { useRef, useEffect } from 'react'

export default function CameraCapture({ onCapture, onCancel, onError }) {
  const videoRef = useRef(null)
  const streamRef = useRef(null)
  const onErrorRef = useRef(onError)
  onErrorRef.current = onError

  useEffect(() => {
    let cancelled = false

    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: 'user' } })
      .then((stream) => {
        if (cancelled) {
          stream.getTracks().forEach((t) => t.stop())
          return
        }
        streamRef.current = stream
        videoRef.current.srcObject = stream
      })
      .catch(() => onErrorRef.current?.('Camera access denied or unavailable.'))

    return () => {
      cancelled = true
      streamRef.current?.getTracks().forEach((t) => t.stop())
      streamRef.current = null
    }
  }, [])

  const capture = () => {
    const video = videoRef.current
    const canvas = document.createElement('canvas')
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    canvas.getContext('2d').drawImage(video, 0, 0)
    canvas.toBlob((blob) => onCapture(blob), 'image/jpeg')
  }

  return (
    <section className="camera-section">
      <div className="camera-portal">
        <video ref={videoRef} autoPlay playsInline className="camera-video" />
        <button className="camera-capture-btn" onClick={capture} aria-label="Capture" />
      </div>
      <button className="btn-secondary" onClick={onCancel}>Cancel</button>
    </section>
  )
}
