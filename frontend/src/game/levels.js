import levelsIndex from '../constants/levels.json';
import level1 from '../constants/levels/level-1.json';
import level2 from '../constants/levels/level-2.json';
import level3 from '../constants/levels/level-3.json';
import level4 from '../constants/levels/level-4.json';
import level5 from '../constants/levels/level-5.json';
import level6 from '../constants/levels/level-6.json';
import level7 from '../constants/levels/level-7.json';
import signRegistry from '../../../shared/signs.json';

const RAW_LEVELS_BY_ID = { 1: level1, 2: level2, 3: level3, 4: level4, 5: level5, 6: level6, 7: level7 };

export const LEVELS_KEY = 'pookie.levels';

// First load: seed localStorage from levels.json, but only level 1 starts
// available — levels.json's own `available` flags are just the design
// defaults and are ignored here. Every later load reads the player's
// actual progress back out of localStorage instead.
function seedLevelsIndex() {
  return levelsIndex.levels.map((entry) => ({ ...entry, available: entry.id === 1 }));
}

function loadLevelsIndex() {
  try {
    const raw = localStorage.getItem(LEVELS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch (e) { /* localStorage unavailable or corrupt — reseed below */ }
  const seeded = seedLevelsIndex();
  try { localStorage.setItem(LEVELS_KEY, JSON.stringify(seeded)); } catch (e) { /* localStorage unavailable — progress stays session-only */ }
  return seeded;
}

const storedIndex = loadLevelsIndex();

// levels.json is the source of truth for name/image — it can be edited
// without touching each level's move/opponent data in level-N.json.
// `available` comes from the stored index above and is mutated in place
// by unlockLevel() as the player progresses.
export const LEVELS = storedIndex.map((entry) => {
  const raw = RAW_LEVELS_BY_ID[entry.id];
  return {
    ...raw,
    name: entry.name,
    available: entry.available,
    opponentPokemon: { ...raw.opponentPokemon, image: entry.image || raw.opponentPokemon.image },
  };
});

// Marks a level unlocked and persists it straight back to localStorage.
export function unlockLevel(id) {
  const level = LEVELS.find((lvl) => lvl.id === id);
  const entry = storedIndex.find((e) => e.id === id);
  if (!level || !entry || level.available) return;
  level.available = true;
  entry.available = true;
  try { localStorage.setItem(LEVELS_KEY, JSON.stringify(storedIndex)); } catch (e) { /* localStorage unavailable — progress stays session-only */ }
}

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

const POKEMON_PALETTES = {
  magikarp: ['#e58a86', '#b85652'],
  psyduck: ['#e8c14a', '#b8941f'],
  "farfetch'd": ['#c9a33b', '#9a7a1e'],
  onix: ['#8a97a1', '#5f6b74'],
  venusaur: ['#6fae4a', '#4c8330'],
  gyarados: ['#3f8fd0', '#2a6aa3'],
  charizard: ['#e4643a', '#b8451f'],
  snorlax: ['#3fa9a0', '#287a74'],
  mewtwo: ['#9b7fc9', '#6a4fa3'],
};

export function palette(levelId) {
  return PALETTES[levelId - 1] || PALETTES[0];
}

export function pokemonPalette(level) {
  const key = level.opponentPokemon.species.toLowerCase();
  return POKEMON_PALETTES[key] || palette(level.id);
}

const SMALL_SPRITE_SCALE = {
  magikarp: 0.55,
  psyduck: 0.55,
  venusaur: 0.8,
};

export function spriteScale(level) {
  const key = level.opponentPokemon.species.toLowerCase();
  return SMALL_SPRITE_SCALE[key] || 1;
}

export function levelById(id) {
  return LEVELS.find((lvl) => lvl.id === id);
}

export function isLevelAvailable(level) {
  return level.available;
}

export function opponentName(level) {
  return level.opponentPokemon.species.toUpperCase();
}

export function opponentImage(level) {
  return level.opponentPokemon.image;
}

export function moveList(level) {
  return level.moves.map((m) => ({
    id: m.id,
    word: (SIGNS_BY_ID[m.signId] && SIGNS_BY_ID[m.signId].displayText) || m.signId.replace(/_/g, ' '),
    difficulty: m.difficulty,
    damage: m.damage,
    hintImage: m.hintImage || null,
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

