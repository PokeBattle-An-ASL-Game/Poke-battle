import { Navigate, useOutletContext, useParams } from 'react-router-dom';
import BattleScreen from '../components/Battle/BattleScreen.jsx';
import { isLevelAvailable, levelById } from '../game/levels.js';

export default function BattlePage() {
  const { levelId } = useParams();
  const { onUnlock, goSelect, goBattle, setBattleReset } = useOutletContext();

  const match = /^level-(\d+)$/.exec(levelId || '');
  const id = match ? Number(match[1]) : NaN;
  const level = levelById(id);

  if (!level || !isLevelAvailable(level)) {
    return <Navigate to="/" replace />;
  }

  return (
    <BattleScreen
      key={id}
      levelId={id}
      onUnlock={onUnlock}
      onNextLevel={goBattle}
      onGoSelect={goSelect}
      setBattleReset={setBattleReset}
    />
  );
}
