import { useEffect, useState } from 'react';
import { useOutletContext } from 'react-router-dom';
import LevelSelect from '../components/LevelSelect/LevelSelect.jsx';
import LevelPreviewModal from '../components/LevelPreviewModal.jsx';

export default function SelectPage() {
  const { goBattle } = useOutletContext();
  const [previewId, setPreviewId] = useState(null);
  const [intro, setIntro] = useState(true);

  // Replays the title/pokemon reveal animation every time this page mounts,
  // i.e. every time the player returns to the select screen.
  useEffect(() => {
    setIntro(true);
    const t = setTimeout(() => setIntro(false), 2050);
    return () => clearTimeout(t);
  }, []);

  const startBattle = (id) => {
    setPreviewId(null);
    goBattle(id);
  };

  return (
    <>
      <div style={{ position: 'absolute', left: '50%', top: '50%', zIndex: 8, pointerEvents: 'none', display: 'flex', alignItems: 'center', gap: 20, fontFamily: "'Silkscreen',monospace", fontSize: 76, letterSpacing: '.08em', color: '#f4ead6', whiteSpace: 'nowrap', textShadow: '0 5px 0 rgba(0,0,0,.35)', animation: 'sb-title 2s cubic-bezier(.6,0,.2,1) forwards' }}>
        <img src="/assets/pokeball.svg" alt="" style={{ width: 64, height: 64, imageRendering: 'pixelated', filter: 'drop-shadow(0 5px 0 rgba(0,0,0,.35))' }} />
        Poké <span style={{ color: '#e0a13b' }}>BATTLE</span>
      </div>

      <LevelSelect intro={intro} onOpenPreview={setPreviewId} />

      {previewId && (
        <LevelPreviewModal levelId={previewId} onClose={() => setPreviewId(null)} onStart={startBattle} />
      )}

      <footer style={{ position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 6, padding: '8px 20px', fontSize: 12, color: '#cfe0e4', background: 'rgba(8,16,20,.62)', textShadow: '0 1px 3px rgba(0,0,0,.8)', pointerEvents: 'none' }}>
        <span style={{ color: '#e0a13b' }}>Made for HopHacks 2026 — built by Rohith, Subikisha and Priyanka.</span>
      </footer>
    </>
  );
}
