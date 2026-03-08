# Frontend FaceForge

Snapshot: 2026-02-27

## Démarrage
```bash
npm install
npm run dev
```

## Rôle
- Upload/preview image
- Capture webcam
- Appel backend `POST /upload`
- Affichage des sliders dans l'UI

## État réel
- Le frontend appelle bien le backend.
- Il affiche `score` et erreurs backend.
- Les sliders affichés sont encore mockés dans `src/App.jsx`.
- Le slider backend `nose_length` n'est pas rendu dans `SliderResults.jsx`.

## Fichiers clés
- `src/App.jsx`
- `src/components/DropZone.jsx`
- `src/components/CameraCapture.jsx`
- `src/components/SliderResults.jsx`
