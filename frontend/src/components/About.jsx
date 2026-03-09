export default function About() {
  return (
    <section className="about-section">
      <h2 className="about-heading">How It Works</h2>
      <ol className="about-steps">
        <li><strong>Photo validation</strong> — Haar Cascade checks for exactly one face. A quality score (0–100) is computed. Severely blurry images are hard-rejected; scores below 60 produce a warning.</li>
        <li><strong>Landmark detection</strong> — MediaPipe Face Mesh places 468 points across eyes, nose, mouth, jaw, brows.</li>
        <li><strong>Ratio calculation</strong> — 18 morphological ratios derived from landmarks, scale-independent.</li>
        <li><strong>Slider mapping</strong> — Each ratio interpolated against a calibration table from real DD2 measurements, clamped to [−100, 100].</li>
      </ol>
      <div className="rune-line" />

      <h2 className="about-heading">The Ideal Portrait</h2>
      <ul className="about-list">
        <li><strong>Sharp focus</strong> — Motion blur or soft focus will be rejected.</li>
        <li><strong>Front-facing</strong> — Look straight into the camera.</li>
        <li><strong>Neutral expression</strong> — Relax your face. Smiling distorts landmark geometry.</li>
        <li><strong>Both eyes fully visible</strong> — No hair, glasses, or shadows obscuring eyes.</li>
        <li><strong>Camera at eye level</strong> — Shooting from above or below changes apparent proportions.</li>
        <li><strong>Even lighting</strong> — Avoid strong shadows or direct flash. Natural light works best.</li>
      </ul>
      <div className="rune-line" />

      <h2 className="about-heading">Common Errors</h2>
      <ul className="about-list">
        <li><strong>"Image too blurry"</strong> — Retake with better lighting or a steady hand.</li>
        <li><strong>"No face detected" / "Multiple faces"</strong> — Ensure one clearly visible face. Busy backgrounds with face-like textures can trigger false positives.</li>
        <li><strong>"Camera angle too high/low"</strong> — Bring the camera to eye level.</li>
        <li><strong>"Landmark extraction failed"</strong> — A clearer, more front-facing photo is needed.</li>
        <li><strong>Low quality warning</strong> — Results are still valid but a better photo may improve accuracy.</li>
      </ul>
      <div className="rune-line" />

      <h2 className="about-heading">Why It Works</h2>
      <p className="about-body">
        MediaPipe Face Mesh reliably places 468 landmarks to sub-pixel accuracy on standard portraits.
        The slider mapping was calibrated directly from Dragon's Dogma II's character editor, measuring
        real slider values against real face proportions. 18 sliders are currently mapped. One slider
        (jaw definition) is intentionally excluded: its effect is three-dimensional and undetectable
        from a single frontal photograph.
      </p>
    </section>
  )
}
