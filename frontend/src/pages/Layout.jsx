import { useCallback, useEffect, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { resetLevels, unlockLevel } from '../game/levels.js';
import { playMusic } from '../game/audioManager.js';
import { THEME_TRACK, WILD_BATTLE_TRACK } from '../constants/audio.js';

const buttonStyle = {
  display: 'flex', alignItems: 'center', gap: 6,
  fontFamily: "'Silkscreen',monospace", fontSize: 12, letterSpacing: '.06em',
  padding: '9px 16px', background: '#f4ead6', color: '#2b3a3f',
  border: '2px solid #2b3a3f', boxShadow: '3px 3px 0 0 #2b3a3f',
  cursor: 'pointer', transition: 'transform .05s ease-out, box-shadow .05s ease-out',
};

function pressHandlers() {
  return {
    onMouseDown: (e) => { e.currentTarget.style.transform = 'translate(3px,3px)'; e.currentTarget.style.boxShadow = '0 0 0 0 #2b3a3f'; },
    onMouseUp: (e) => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = '3px 3px 0 0 #2b3a3f'; },
    onMouseLeave: (e) => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.boxShadow = '3px 3px 0 0 #2b3a3f'; },
  };
}

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  // Bumped after unlockLevel()/resetLevels() mutate LEVELS in place, so routed pages re-render.
  const [, bumpLevels] = useState(0);
  // Registered by BattleScreen (via BattlePage) so its reset button can live in the header, next to BACK.
  const [battleReset, setBattleReset] = useState(null);

  const isSelect = location.pathname === '/';
  const isBattle = location.pathname.startsWith('/pokemon/level-');

  useEffect(() => {
    if (isSelect) playMusic(THEME_TRACK);
  }, [isSelect]);

  const onUnlock = useCallback((id) => {
    unlockLevel(id);
    bumpLevels((v) => v + 1);
  }, []);

  const onResetLevels = useCallback(() => {
    if (!window.confirm('Reset all level progress? Only Level 1 will stay unlocked.')) return;
    resetLevels();
    bumpLevels((v) => v + 1);
  }, []);

  const goSelect = useCallback(() => {
    playMusic(THEME_TRACK);
    navigate('/');
  }, [navigate]);

  const goBattle = useCallback((id) => {
    playMusic(WILD_BATTLE_TRACK);
    navigate(`/pokemon/level-${id}`);
  }, [navigate]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '100vh', overflow: 'hidden', background: '#0c1216' }}>
      <header style={{ position: 'absolute', top: 0, left: 0, right: 0, zIndex: 6, display: 'flex', flexWrap: 'wrap', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, padding: '22px 24px 8px', background: 'linear-gradient(rgba(8,16,20,.55),rgba(8,16,20,0))', pointerEvents: 'none' }}>
        <div />
        <div style={{ display: 'flex', gap: 8, pointerEvents: 'auto' }}>
          {isBattle && (
            <button onClick={goSelect} {...pressHandlers()} style={buttonStyle}>
              <span aria-hidden="true">◀</span> BACK
            </button>
          )}
          {isBattle && battleReset && (
            <button onClick={battleReset} {...pressHandlers()} style={buttonStyle}>
              RESET
            </button>
          )}
          {isSelect && (
            <button onClick={onResetLevels} {...pressHandlers()} style={buttonStyle}>
              RESET
            </button>
          )}
        </div>
      </header>

      <Outlet context={{ onUnlock, goSelect, goBattle, setBattleReset }} />
    </div>
  );
}
