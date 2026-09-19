import { useCallback, useEffect, useRef, useState } from 'react';
import {
  counterEvery as counterEveryFor,
  counterNames,
  effectLine,
  levelById,
  moveList,
  opponentName,
} from './levels.js';
import { API_BASE_URL } from '../constants/capture.js';

const IDLE_ANIM = 'sb-idle 3.4s ease-in-out infinite';
const RETRY_NOTES = {
  BAD_REQUEST: 'The capture could not be read. Try again.',
  UPLOAD_TOO_LARGE: 'The capture was too large to send. Try again.',
  LEVEL_UNAVAILABLE: 'This level is not available yet.',
  SIGN_UNAVAILABLE: 'This sign is not available yet.',
  MODEL_NOT_READY: 'Recognition is temporarily unavailable.',
  INFERENCE_UNAVAILABLE: 'Recognition is temporarily unavailable.',
  NETWORK_ERROR: 'Could not reach the recognition server.',
};

function initialState(levelId, unlocked) {
  return {
    levelId,
    unlocked,
    phase: 'INTRO',
    playerHP: 100,
    opponentHP: 100,
    slotIds: [null, null, null, null],
    reserve: [],
    used: [],
    successCount: 0,
    selected: null,
    requestId: null,
    typed: '',
    fullMsg: '',
    contKey: '',
    msgDone: false,
    oppAnim: IDLE_ANIM,
    plyAnim: 'none',
    oppFloat: '',
    plyFloat: '',
    flashOn: false,
    refillSlot: -1,
    frames: 0,
    recording: false,
    log: [],
    cmdIndex: 0,
    menuOpen: true,
    entering: 'ball',
    oppEnter: 'ball',
    hintOpen: false,
  };
}

export function useBattle(levelId, unlocked, onUnlock) {
  const [state, setState] = useState(() => initialState(levelId, unlocked));
  const stateRef = useRef(state);
  stateRef.current = state;

  const timers = useRef([]);
  const typer = useRef(null);

  const level = levelById(levelId);
  const moves = moveList(level);
  const byId = Object.fromEntries(moves.map((m) => [m.id, m]));

  const patch = useCallback((updater) => {
    setState((s) => ({ ...s, ...(typeof updater === 'function' ? updater(s) : updater) }));
  }, []);

  const wait = useCallback((ms, fn) => {
    const id = setTimeout(fn, ms);
    timers.current.push(id);
    return id;
  }, []);

  const clearTimers = useCallback(() => {
    timers.current.forEach(clearTimeout);
    timers.current = [];
    if (typer.current) { clearInterval(typer.current); typer.current = null; }
  }, []);

  const push = useCallback((line) => {
    patch((s) => ({ log: [line, ...s.log].slice(0, 8) }));
  }, [patch]);

  const finishLine = useCallback(() => {
    if (typer.current) { clearInterval(typer.current); typer.current = null; }
    const s = stateRef.current;
    patch({ typed: s.fullMsg, msgDone: true });
    const key = s.contKey;
    if (key) wait(1900, () => runCont(key));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patch, wait]);

  const runTyper = useCallback((force) => {
    const full = force || stateRef.current.fullMsg || '';
    if (typer.current || !full) return;
    if ((stateRef.current.typed || '').length >= full.length) {
      if (!stateRef.current.msgDone) finishLine();
      return;
    }
    typer.current = setInterval(() => {
      const cur = stateRef.current.typed || '';
      if (cur.length >= full.length) {
        clearInterval(typer.current); typer.current = null;
        finishLine();
        return;
      }
      patch({ typed: full.slice(0, cur.length + 1) });
    }, 22);
  }, [finishLine, patch]);

  const say = useCallback((text, contKey) => {
    if (typer.current) { clearInterval(typer.current); typer.current = null; }
    patch({ fullMsg: text, typed: '', msgDone: false, contKey: contKey || '' });
    runTyper(text);
  }, [patch, runTyper]);

  const skipLine = useCallback(() => {
    const s = stateRef.current;
    if (!s.fullMsg) return;
    if ((s.typed || '').length < s.fullMsg.length) { finishLine(); return; }
    if (s.contKey) runCont(s.contKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finishLine]);

  const prompt = useCallback(() => {
    patch({ phase: 'CHOOSE_MOVE', selected: null, menuOpen: true, cmdIndex: 0 });
  }, [patch]);

  const counterHit = useCallback(() => {
    patch({ oppAnim: 'sb-lunge-r .45s ease-in-out' });
    wait(430, () => {
      patch({ oppAnim: IDLE_ANIM, plyAnim: 'sb-shake .4s ease-in-out', plyFloat: '-10', flashOn: true });
    });
    wait(700, () => {
      const hp = Math.max(0, stateRef.current.playerHP - 10);
      patch({ playerHP: hp, plyAnim: 'none', flashOn: false });
      wait(1400, () => patch({ plyFloat: '' }));
      if (hp <= 0) {
        wait(500, () => defeat());
      } else {
        wait(500, () => say(hp <= 30 ? 'That one stung — keep your hands steady.' : "It's not very effective…", 'prompt'));
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patch, wait, say]);

  const counterAttack = useCallback((forced) => {
    const names = counterNames(level);
    const name = names[Math.floor(Math.random() * names.length)];
    push((forced ? 'counter (incorrect) — ' : 'counter (scheduled) — ') + name + ' 10 HP');
    patch({ phase: 'OPPONENT_TURN' });
    say(opponentName(level) + ' used ' + name + '!', 'counterHit');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level, push, patch, say]);

  const victory = useCallback(() => {
    const s = stateRef.current;
    const nextUnlocked = Math.max(s.unlocked, Math.min(7, s.levelId + 1));
    if (nextUnlocked !== s.unlocked) onUnlock(nextUnlocked);
    patch({ phase: 'VICTORY', oppAnim: 'sb-faint .7s ease-in forwards', unlocked: nextUnlocked });
    push('victory — all unique signs completed');
    say(opponentName(level) + ' was defeated!');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [level, onUnlock, patch, push, say]);

  const defeat = useCallback(() => {
    patch({ phase: 'DEFEAT', plyAnim: 'sb-faint .7s ease-in forwards' });
    push('defeat — progress and history kept');
    say('You are out of HP.');
  }, [patch, push, say]);

  const afterCorrect = useCallback(() => {
    const s = stateRef.current;
    if (s.opponentHP <= 0) { victory(); return; }
    const due = s.successCount % counterEveryFor(moves.length) === 0;
    if (due) counterAttack(false); else prompt();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [moves.length, victory, counterAttack, prompt]);

  const runCont = useCallback((key) => {
    if (stateRef.current.contKey !== key) return;
    patch({ contKey: '' });
    if (key === 'prompt') return prompt();
    if (key === 'counterForced') return counterAttack(true);
    if (key === 'counterHit') return counterHit();
    if (key === 'afterCorrect') return afterCorrect();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patch, prompt, counterAttack, counterHit, afterCorrect]);

  const resolve = useCallback((result, note) => {
    const s = stateRef.current;
    const mv = byId[s.selected];
    if (result === 'retry') {
      patch({ phase: 'RESULT' });
      push('retry — no damage, no PP, no counterattack');
      say(note || 'Signal unclear. Free retry — nothing was spent.', 'prompt');
      return;
    }
    if (result === 'incorrect') {
      patch({ phase: 'RESULT' });
      push('incorrect — ' + mv.word + ' stays visible at PP 1');
      say('That did not match ' + mv.word + '.', 'counterForced');
      return;
    }
    const idx = s.slotIds.indexOf(mv.id);
    const nextOpp = Math.max(0, s.opponentHP - mv.damage);
    const reserve = s.reserve.slice();
    const head = reserve.shift() || null;
    const slots = s.slotIds.slice();
    slots[idx] = head;

    patch({ phase: 'RESULT', plyAnim: 'sb-lunge-l .45s ease-in-out', flashOn: true });
    wait(430, () => patch({ plyAnim: 'none', flashOn: false, oppAnim: 'sb-shake .4s ease-in-out', oppFloat: '-' + mv.damage }));
    wait(900, () => patch({ opponentHP: nextOpp, oppAnim: IDLE_ANIM }));
    wait(1900, () => patch({ oppFloat: '' }));
    patch((prev) => ({
      slotIds: slots,
      reserve,
      used: prev.used.concat(mv.id),
      successCount: prev.successCount + 1,
    }));
    if (head !== null) {
      wait(950, () => {
        patch({ refillSlot: idx });
        push('slot ' + (idx + 1) + ' refilled from queue');
      });
    }
    push('correct — ' + mv.word + ' hits for ' + mv.damage + ' · PP 1→0');
    say('It worked! ' + mv.word + ' hit for ' + mv.damage + '.' + effectLine(mv.damage), 'afterCorrect');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [byId, patch, push, say, wait]);

  const startLevel = useCallback((id) => {
    clearTimers();
    const mv = moveList(levelById(id));
    const ids = mv.map((m) => m.id);
    patch((s) => ({
      levelId: id, phase: 'INTRO',
      playerHP: 100, opponentHP: 100,
      slotIds: [ids[0] || null, ids[1] || null, ids[2] || null, ids[3] || null],
      reserve: ids.slice(4), used: [], successCount: 0, selected: null,
      requestId: null, oppFloat: '', plyFloat: '', plyAnim: 'none', refillSlot: -1,
      menuOpen: true, entering: 'ball', oppAnim: IDLE_ANIM,
      log: ['battle start'], oppEnter: 'ball', hintOpen: false,
    }));
    say('A wild ' + opponentName(levelById(id)) + ' appeared!', 'prompt');
    patch({ entering: 'ball', oppEnter: 'ball', oppAnim: 'none' });
    wait(520, () => patch({ oppEnter: 'burst' }));
    wait(640, () => patch({ oppEnter: 'emerge', oppAnim: 'sb-emerge .55s cubic-bezier(.3,1.4,.5,1)' }));
    wait(1250, () => patch({ oppEnter: null, oppAnim: IDLE_ANIM }));
    wait(700, () => patch({ entering: 'burst' }));
    wait(820, () => patch({ entering: 'emerge', plyAnim: 'sb-emerge .55s cubic-bezier(.3,1.4,.5,1)' }));
    wait(1450, () => patch({ entering: null, plyAnim: 'none' }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clearTimers, patch, say, wait]);

  useEffect(() => {
    startLevel(levelId);
    runTyper();
    return () => clearTimers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    runTyper();
  });

  const setCmdIndex = useCallback((i) => patch({ cmdIndex: i }), [patch]);
  const chooseFight = useCallback(() => patch({ menuOpen: false }), [patch]);
  const backToMenu = useCallback(() => patch({ menuOpen: true, selected: null }), [patch]);
  const openHint = useCallback(() => patch({ hintOpen: true }), [patch]);
  const closeHint = useCallback(() => patch({ hintOpen: false }), [patch]);
  const chooseRun = useCallback(() => {
    push('run refused — battle continues');
    patch({ phase: 'RESULT' });
    say("You can't run from learning!", 'prompt');
  }, [patch, push, say]);

  const pickMove = useCallback((moveId) => {
    if (stateRef.current.phase !== 'CHOOSE_MOVE') return;
    patch({ selected: moveId, phase: 'CAPTURE', frames: 0, recording: false, requestId: crypto.randomUUID() });
  }, [patch]);

  const cancelCapture = useCallback(() => {
    clearTimers();
    patch({ phase: 'CHOOSE_MOVE', selected: null, frames: 0, recording: false, requestId: null });
    push('capture cancelled — request discarded');
  }, [clearTimers, patch, push]);

  const setRecording = useCallback((recording) => patch({ recording, frames: 0 }), [patch]);
  const setFrameProgress = useCallback((n) => patch({ frames: n }), [patch]);

  const submitFrames = useCallback(async (frameBlobs, timestampsMs) => {
    const s = stateRef.current;
    patch({ recording: false, phase: 'SUBMITTING' });
    push('POST /api/validate-sign · ' + frameBlobs.length + ' frames · ' + s.requestId);

    const form = new FormData();
    form.append('requestId', s.requestId);
    form.append('levelId', String(levelId));
    form.append('moveId', s.selected);
    form.append('timestampsMs', JSON.stringify(timestampsMs));
    frameBlobs.forEach((blob, i) => form.append('frames', blob, `frame-${i}.jpg`));

    try {
      const res = await fetch(`${API_BASE_URL}/api/validate-sign`, { method: 'POST', body: form });
      const body = await res.json().catch(() => null);
      if (res.ok && body?.status) {
        push('response ' + res.status + ' · ' + body.status);
        resolve(body.status);
      } else {
        const code = body?.error?.code || 'BAD_REQUEST';
        push('response ' + res.status + ' · ' + code);
        resolve('retry', RETRY_NOTES[code]);
      }
    } catch {
      push('network error — request failed');
      resolve('retry', RETRY_NOTES.NETWORK_ERROR);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [patch, push, resolve, levelId]);

  const restart = useCallback(() => startLevel(stateRef.current.levelId), [startLevel]);

  const onKey = useCallback((e) => {
    const s = stateRef.current;
    if (s.phase !== 'CHOOSE_MOVE' || s.menuOpen === false) return;
    if (s.hintOpen) {
      if (e.key === 'Escape') { e.preventDefault(); closeHint(); }
      return;
    }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
      e.preventDefault();
      patch({ cmdIndex: s.cmdIndex === 0 ? 1 : 0 });
    } else if (e.key === 'ArrowDown') {
      e.preventDefault();
      patch({ cmdIndex: (s.cmdIndex + 1) % 3 });
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      patch({ cmdIndex: (s.cmdIndex + 2) % 3 });
    } else if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      [chooseFight, chooseRun, openHint][s.cmdIndex]();
    }
  }, [patch, closeHint, chooseFight, chooseRun, openHint]);

  useEffect(() => {
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onKey]);

  return {
    state, level, moves, byId,
    chooseFight, chooseRun, backToMenu, openHint, closeHint, setCmdIndex,
    pickMove, cancelCapture, setRecording, setFrameProgress, submitFrames,
    skipLine, restart, startLevel,
  };
}
