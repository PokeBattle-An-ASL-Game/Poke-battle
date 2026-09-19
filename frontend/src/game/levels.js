import level1 from '../constants/levels/level-1.json';
import level2 from '../constants/levels/level-2.json';
import level3 from '../constants/levels/level-3.json';
import level4 from '../constants/levels/level-4.json';
import level5 from '../constants/levels/level-5.json';
import level6 from '../constants/levels/level-6.json';
import level7 from '../constants/levels/level-7.json';
import signRegistry from '../../../shared/signs.json';

export const LEVELS = [level1, level2, level3, level4, level5, level6, level7];

export const SIGNS_BY_ID = Object.fromEntries(
  signRegistry.signs.map((sign) => [sign.id, sign])
);

const PALETTES = [
  ['#e4643a', '#b8451f'],
  ['#3f8fd0', '#2a6aa3'],
  ['#6fae4a', '#4c8330'],
  ['#c9a33b', '#9a7a1e'],
  ['#8e6ad0', '#6a48a8'],
  ['#d05a90', '#a33a6b'],
  ['#3fa9a0', '#287a74'],
];

const BLURBS = {
  1: 'Two signs, fifty damage each. The opening bout — learn the greeting and the yes.',
  2: 'Three signs of basic courtesy. The counterattack arrives on every second success.',
  3: 'Four signs for asking and stopping. A full grid with no reserve queue behind it.',
  4: 'Four signs around food and water. Damage climbs with difficulty, from 15 up to 40.',
  5: 'Five school signs. One waits in the reserve queue until a slot clears.',
  6: 'Six family and question signs. Two sit in reserve; counters come every second hit.',
  7: 'Six feeling signs. The longest level — the queue stays full most of the battle.',
};

export function palette(levelId) {
  return PALETTES[levelId - 1] || PALETTES[0];
}

export function blurb(levelId) {
  return BLURBS[levelId] || '';
}

export function levelById(id) {
  return LEVELS.find((lvl) => lvl.id === id);
}

export function opponentName(level) {
  return level.opponentPokemon.species.toUpperCase();
}

export function moveList(level) {
  return level.moves.map((m) => ({
    id: m.id,
    word: (SIGNS_BY_ID[m.signId] && SIGNS_BY_ID[m.signId].displayText) || m.signId.replace(/_/g, ' '),
    difficulty: m.difficulty,
    damage: m.damage,
  }));
}

export function counterNames(level) {
  return level.opponentPokemon.attacks.map((a) => a.name);
}

export function counterEvery(moveCount) {
  return Math.max(1, Math.ceil((moveCount - 1) / 4));
}

export function effectLine(damage) {
  if (damage >= 40) return " It's super effective!";
  if (damage <= 20) return " It's not very effective…";
  return '';
}

export function hpColor(pct) {
  if (pct > 50) return '#63c98a';
  if (pct > 20) return '#f2c14e';
  return '#e35d4f';
}

export const UNLOCK_KEY = 'pookie.unlocked';

export function readUnlocked() {
  try {
    return Math.max(4, Math.min(7, parseInt(localStorage.getItem(UNLOCK_KEY), 10) || 4));
  } catch (e) {
    return 4;
  }
}

export function writeUnlocked(id) {
  try {
    localStorage.setItem(UNLOCK_KEY, String(id));
  } catch (e) {
    /* localStorage unavailable (private mode, etc.) — unlock stays session-only */
  }
}
