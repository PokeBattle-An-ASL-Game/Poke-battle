import { LEVELS, isLevelAvailable, opponentImage, opponentName, palette, spriteScale } from '../../game/levels.js';
import { useBattle } from '../../game/useBattle.js';
import { EntranceEffects, OpponentSprite, PlayerSprite } from './Sprites.jsx';
import { OpponentHPBar, PlayerHPBar } from './HPBars.jsx';
import MessageBox from './MessageBox.jsx';
import CommandMenu from './CommandMenu.jsx';
import MoveGrid from './MoveGrid.jsx';
import CaptureOverlay from './CaptureOverlay.jsx';
import HintModal from './HintModal.jsx';
import EndScreen from './EndScreen.jsx';

export default function BattleScreen({ levelId, unlocked, onUnlock, onNextLevel, onGoSelect }) {
  const battle = useBattle(levelId, unlocked, onUnlock);
  const { state, level, moves, byId } = battle;

  const capturing = state.phase === 'CAPTURE' || state.phase === 'SUBMITTING';
  const ended = state.phase === 'VICTORY' || state.phase === 'DEFEAT';
  const showMessage = state.phase !== 'CHOOSE_MOVE';
  const showCommand = state.phase === 'CHOOSE_MOVE' && state.menuOpen !== false;
  const showGrid = state.phase === 'CHOOSE_MOVE' && state.menuOpen === false;
  const oppLabel = opponentName(level);
  const oppImage = opponentImage(level);
  const oppScale = spriteScale(level);
  const oppOpacity = (state.phase === 'VICTORY' || state.oppEnter === 'ball' || state.oppEnter === 'burst') ? 0 : 1;
  const plyOpacity = (state.phase === 'DEFEAT' || state.entering === 'ball' || state.entering === 'burst') ? 0 : 1;
  const selected = state.selected ? byId[state.selected] : null;
  const nextLevel = LEVELS.find((lvl) => lvl.id === levelId + 1);
  const nextAvailable = Boolean(nextLevel && isLevelAvailable(nextLevel, state.unlocked));

  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      <div style={{ containerType: 'size', position: 'absolute', inset: 0, background: 'repeating-linear-gradient(#eef3f6 0 7px,#e1e9ee 7px 14px)', overflow: 'hidden', fontFamily: "'Silkscreen',monospace" }}>

        <div style={{ position: 'absolute', left: '5%', bottom: '33.5%', width: '30%', height: '8.5%', borderRadius: '50%', background: '#b98a52', boxShadow: 'inset 0 -6px 0 rgba(0,0,0,.14),0 4px 0 rgba(0,0,0,.1)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', left: '8%', bottom: '34.9%', width: '24%', height: '5%', borderRadius: '50%', background: '#cfa06a', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', right: '6%', top: '37%', width: '26%', height: '8%', borderRadius: '50%', background: '#b98a52', boxShadow: 'inset 0 -5px 0 rgba(0,0,0,.14),0 4px 0 rgba(0,0,0,.1)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', right: '9%', top: '38.2%', width: '20%', height: '4.6%', borderRadius: '50%', background: '#cfa06a', pointerEvents: 'none' }} />

        <OpponentSprite label={oppLabel} image={oppImage} scale={oppScale} anim={state.oppAnim} opacity={oppOpacity} />
        <EntranceEffects oppEnter={state.oppEnter} entering={state.entering} />
        <PlayerSprite anim={state.plyAnim} opacity={plyOpacity} />

        <OpponentHPBar name={oppLabel} hp={state.opponentHP} float={state.oppFloat} />
        <PlayerHPBar hp={state.playerHP} float={state.plyFloat} />

        {showMessage && <MessageBox typed={state.typed} msgDone={state.msgDone} onSkip={battle.skipLine} />}
        {showCommand && (
          <CommandMenu
            cmdIndex={state.cmdIndex}
            onFight={battle.chooseFight}
            onRun={battle.chooseRun}
            onHint={battle.openHint}
            onHover={battle.setCmdIndex}
          />
        )}
        {showGrid && (
          <MoveGrid state={state} byId={byId} moves={moves} onPick={battle.pickMove} onBack={battle.backToMenu} />
        )}
        {capturing && (
          <CaptureOverlay
            state={state}
            selectedWord={selected ? selected.word : ''}
            onStartRecording={battle.startRecording}
            onCancel={battle.cancelCapture}
            onSetOutcome={battle.setOutcome}
          />
        )}

        {state.flashOn && (
          <div style={{ position: 'absolute', inset: 0, background: '#fff', animation: 'sb-flash .22s steps(2) 2', pointerEvents: 'none' }} />
        )}

        {state.hintOpen && (
          <HintModal level={level} palette={palette(levelId)} moves={moves} onClose={battle.closeHint} />
        )}

        {ended && (
          <EndScreen
            phase={state.phase}
            level={{ opp: oppLabel }}
            levelId={levelId}
            moveCount={moves.length}
            nextAvailable={nextAvailable}
            onNext={() => onNextLevel(levelId + 1)}
            onRestart={battle.restart}
            onGoSelect={onGoSelect}
          />
        )}
      </div>
    </div>
  );
}
