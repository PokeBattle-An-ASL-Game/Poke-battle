import { LEVELS, isLevelAvailable, palette, spriteScale } from '../../game/levels.js';
import LevelTile from './LevelTile.jsx';

export default function LevelSelect({ intro, unlocked, onOpenPreview }) {
  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', background: '#35b6f2' }}>
      <div style={{ position: 'absolute', top: 126, left: 0, width: '200%', height: 70, animation: 'sb-drift 90s steps(90) infinite', pointerEvents: 'none' }}>
        <div style={{ position: 'absolute', left: '4%', top: 34, width: 144, height: 16, background: '#fff', boxShadow: '16px -16px 0 0 #fff, 48px -32px 0 0 #fff, 64px -16px 0 0 #fff, 96px -16px 0 0 #fff, 0 16px 0 0 #dff2fb' }} />
        <div style={{ position: 'absolute', left: '30%', top: 18, width: 192, height: 16, background: '#fff', boxShadow: '32px -16px 0 0 #fff, 80px -32px 0 0 #fff, 112px -16px 0 0 #fff, 0 16px 0 0 #fff, 16px 32px 0 0 #dff2fb' }} />
        <div style={{ position: 'absolute', left: '56%', top: 34, width: 144, height: 16, background: '#fff', boxShadow: '16px -16px 0 0 #fff, 48px -32px 0 0 #fff, 64px -16px 0 0 #fff, 96px -16px 0 0 #fff, 0 16px 0 0 #dff2fb' }} />
        <div style={{ position: 'absolute', left: '80%', top: 22, width: 112, height: 16, background: '#fff', boxShadow: '32px -16px 0 0 #fff, 64px -16px 0 0 #fff, 0 16px 0 0 #dff2fb' }} />
      </div>
      <div style={{ position: 'absolute', top: 176, left: 0, width: '200%', height: 44, opacity: .7, animation: 'sb-drift 150s steps(150) infinite', pointerEvents: 'none' }}>
        <div style={{ position: 'absolute', left: '16%', top: 10, width: 96, height: 12, background: '#fff', boxShadow: '24px -12px 0 0 #fff, 48px -12px 0 0 #fff, 0 12px 0 0 #e8f6fd' }} />
        <div style={{ position: 'absolute', left: '68%', top: 10, width: 96, height: 12, background: '#fff', boxShadow: '24px -12px 0 0 #fff, 48px -12px 0 0 #fff, 0 12px 0 0 #e8f6fd' }} />
      </div>

      <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 72, background: 'linear-gradient(#3fa63f 0 18px,#37963a 18px 30px,#2f8a33 30px 38px,#c98b2e 38px 52px,#a96f22 52px 58px,#7a4a1e 58px 72px)', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', left: -8, right: -8, bottom: 72, height: 8, background: 'repeating-linear-gradient(90deg,#3fa63f 0 8px,rgba(0,0,0,0) 8px 12px,#3fa63f 12px 16px,rgba(0,0,0,0) 16px 28px)', animation: 'sb-sway 2.4s steps(1) infinite', pointerEvents: 'none' }} />
      <div style={{ position: 'absolute', left: -8, right: -8, bottom: 72, height: 16, background: 'repeating-linear-gradient(90deg,#2f8f3a 0 4px,rgba(0,0,0,0) 4px 16px,#2f8f3a 16px 20px,rgba(0,0,0,0) 20px 40px)', animation: 'sb-sway2 3.2s steps(1) infinite', pointerEvents: 'none' }} />

      {!intro && (
        <div style={{ position: 'absolute', left: 0, right: 0, top: 214, bottom: 92, overflow: 'visible', padding: '0 20px', zIndex: 2 }}>
          <div style={{ position: 'relative', height: '100%', animation: 'sb-rise .5s ease-out both', display: 'grid', gridTemplateColumns: 'repeat(5,minmax(0,1fr))', gridTemplateRows: 'repeat(2,minmax(0,1fr))', justifyItems: 'center', gap: '10px 20px' }}>
            {LEVELS.map((lvl) => (
              <LevelTile key={lvl.id} level={lvl} locked={!isLevelAvailable(lvl, unlocked)} palette={palette(lvl.id)} scale={spriteScale(lvl)} onOpen={onOpenPreview} />
            ))}
            <div style={{ width: '100%', height: '100%', minHeight: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end', gap: 8, opacity: .8 }}>
              <div style={{ position: 'relative', flex: 1, minHeight: 0, aspectRatio: '1/1', maxWidth: 104, maxHeight: 104, alignSelf: 'center', border: '3px dashed rgba(255,255,255,.65)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Silkscreen',monospace", fontSize: 34, color: 'rgba(255,255,255,.8)' }}>?</div>
              <span style={{ fontFamily: "'Silkscreen',monospace", fontSize: 13, letterSpacing: '.05em', textShadow: '0 1px 0 rgba(255,255,255,.35)', color: '#123a49', textAlign: 'center' }}>
                LEVEL 8<br /><span style={{ fontSize: 10, color: '#1d4d5e' }}>COMING SOON</span>
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
