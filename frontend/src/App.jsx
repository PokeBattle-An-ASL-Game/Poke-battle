import { useCallback, useEffect, useState } from 'react';
import LevelSelect from './components/LevelSelect/LevelSelect.jsx';
import LevelPreviewModal from './components/LevelPreviewModal.jsx';
import BattleScreen from './components/Battle/BattleScreen.jsx';
import { readUnlocked, writeUnlocked } from './game/levels.js';

function routeFromHash() {
  const m = /^#battle-(\d+)$/.exec(location.hash || '');
  return m ? { screen: 'BATTLE', levelId: +m[1] } : { screen: 'SELECT', levelId: null };
}

export default function App() {
  const [route, setRoute] = useState(routeFromHash);
  const [previewId, setPreviewId] = useState(null);
  const [intro, setIntro] = useState(true);
  const [unlocked, setUnlocked] = useState(readUnlocked);

  useEffect(() => {
    const onPopState = () => setRoute(routeFromHash());
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    const t = setTimeout(() => setIntro(false), 2050);
    return () => clearTimeout(t);
  }, []);

  const goBattle = useCallback((id) => {
    try { history.pushState(null, '', '#battle-' + id); } catch (e) { /* ignore */ }
    setRoute({ screen: 'BATTLE', levelId: id });
    setPreviewId(null);
  }, []);

  const goSelect = useCallback(() => {
    try { history.pushState(null, '', '#levels'); } catch (e) { /* ignore */ }
    setRoute({ screen: 'SELECT', levelId: null });
    setPreviewId(null);
  }, []);

  const onUnlock = useCallback((id) => {
    writeUnlocked(id);
    setUnlocked(id);
  }, []);

  const isSelect = route.screen === 'SELECT';
  const isBattle = route.screen === 'BATTLE';

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden', background: '#0c1216' }}>
      <header style={{ position: 'absolute', top: 0, left: 0, right: 0, zIndex: 6, display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: 16, padding: '8px 16px', background: 'linear-gradient(rgba(8,16,20,.78),rgba(8,16,20,0))', pointerEvents: 'none' }}>
        <div />
        <div style={{ display: 'flex', gap: 8, pointerEvents: 'auto' }}>
          <button onClick={goSelect} style={{ fontFamily: "'Silkscreen',monospace", fontSize: 11, padding: '6px 11px', background: 'rgba(22,35,42,.85)', color: '#cfe0e4', border: '1px solid #2f4149', cursor: 'pointer' }}>LEVELS</button>
        </div>
      </header>

      {isSelect && (
        <div style={{ position: 'absolute', left: '50%', top: '50%', zIndex: 8, pointerEvents: 'none', fontFamily: "'Silkscreen',monospace", fontSize: 76, letterSpacing: '.08em', color: '#f4ead6', whiteSpace: 'nowrap', textShadow: '0 5px 0 rgba(0,0,0,.35)', animation: 'sb-title 2s cubic-bezier(.6,0,.2,1) forwards' }}>
          Pookié <span style={{ color: '#e0a13b' }}>BATTLE</span>
        </div>
      )}

      {isSelect && (
        <LevelSelect unlocked={unlocked} intro={intro} onOpenPreview={setPreviewId} />
      )}

      {previewId && isSelect && (
        <LevelPreviewModal levelId={previewId} onClose={() => setPreviewId(null)} onStart={goBattle} />
      )}

      {isBattle && (
        <BattleScreen
          key={route.levelId}
          levelId={route.levelId}
          unlocked={unlocked}
          onUnlock={onUnlock}
          onNextLevel={goBattle}
          onGoSelect={goSelect}
        />
      )}

      {isSelect && (
        <footer style={{ position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 6, padding: '8px 20px', fontSize: 12, color: '#cfe0e4', background: 'rgba(8,16,20,.62)', textShadow: '0 1px 3px rgba(0,0,0,.8)', pointerEvents: 'none' }}>
          Learn one sign, land one hit. Thirty signs is enough to greet someone, ask a question and say thank you — practice them until they are yours.<br />
          <span style={{ color: '#e0a13b' }}>Made for HopHacks 2026 — built by Rohith, Subikisha and Priyanka.</span>
        </footer>
      )}
    </div>
  );
}
