:root {
  --bg: #ead7ac;
  --ink: #25322c;
  --muted: #6b7468;
  --panel: #fff7df;
  --line: #c8a96e;
  --green: #1f6457;
  --green-soft: #e4f0dc;
  --red: #bb4637;
  --red-soft: #fde5dc;
  --gold: #e7af36;
  --sky: #9bd7de;
  --brown: #795233;
  --shadow: 0 22px 55px rgba(75, 50, 21, 0.2);
}

* {
  box-sizing: border-box;
}

html,
body {
  min-height: 100%;
}

body {
  margin: 0;
  background:
    radial-gradient(circle at 12% 16%, rgba(255, 250, 231, 0.9) 0 0.5px, transparent 1px) 0 0 / 24px 24px,
    linear-gradient(135deg, #ead7ac 0%, #f6e9c8 44%, #d9bd86 100%);
  color: var(--ink);
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.page-texture {
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(90deg, rgba(121, 82, 51, 0.07) 1px, transparent 1px) 0 0 / 38px 38px,
    linear-gradient(rgba(121, 82, 51, 0.06) 1px, transparent 1px) 0 0 / 38px 38px;
  mix-blend-mode: multiply;
}

button {
  font: inherit;
}

.app-shell {
  width: min(1180px, calc(100% - 28px));
  margin: 0 auto;
  padding: 18px 0 24px;
  position: relative;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 2px 18px;
}

.eyebrow,
.muted,
.country-kicker {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0;
  text-transform: uppercase;
}

h1 {
  margin: 2px 0 0;
  font-size: clamp(24px, 3vw, 40px);
  line-height: 1.05;
  text-shadow: 0 2px 0 rgba(255, 250, 231, 0.7);
}

.score-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}

.score-pill {
  min-width: 108px;
  border: 2px solid rgba(96, 70, 36, 0.18);
  border-radius: 8px;
  padding: 9px 12px;
  background: rgba(255, 247, 223, 0.86);
  color: var(--muted);
  text-align: center;
  box-shadow: 0 8px 18px rgba(75, 50, 21, 0.1);
}

.score-pill span {
  display: block;
  font-size: 12px;
  font-weight: 800;
}

.score-pill b {
  display: block;
  color: var(--ink);
  font-size: 22px;
  line-height: 1;
  margin-top: 2px;
}

.score-pill.good {
  background: var(--green-soft);
}

.score-pill.bad {
  background: var(--red-soft);
}

.game-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.58fr) minmax(330px, 0.72fr);
  gap: 18px;
  align-items: stretch;
}

.map-panel,
.question-card,
.result-card {
  border: 2px solid rgba(121, 82, 51, 0.22);
  border-radius: 8px;
  background: var(--panel);
  box-shadow: var(--shadow);
}

.map-panel {
  min-width: 0;
  padding: 14px;
  background:
    linear-gradient(180deg, rgba(255, 252, 238, 0.9), rgba(252, 235, 188, 0.92)),
    var(--panel);
  position: relative;
}

.map-panel::before,
.question-card::before,
.result-card::before {
  content: "";
  position: absolute;
  inset: 6px;
  border: 1px solid rgba(121, 82, 51, 0.14);
  border-radius: 6px;
  pointer-events: none;
}

.map-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
  padding: 2px 2px 12px;
  position: relative;
}

.map-head strong {
  display: block;
  margin-top: 3px;
  font-size: 24px;
  color: #1e3f38;
}

.route-hud {
  display: grid;
  gap: 4px;
  justify-items: end;
}

.route-hud-label {
  color: var(--muted);
  font-size: 11px;
  font-weight: 900;
  text-transform: uppercase;
}

.progress-label {
  display: block;
  border-radius: 8px;
  background: #efbd41;
  color: #3b2b10;
  font-weight: 900;
  min-width: 68px;
  padding: 9px 12px;
  text-align: center;
  border: 2px solid rgba(121, 82, 51, 0.22);
  box-shadow: inset 0 -2px 0 rgba(121, 82, 51, 0.12);
}

.map-viewport {
  position: relative;
  overflow: hidden;
  aspect-ratio: 1000 / 560;
  border-radius: 8px;
  background: var(--sky);
  border: 3px solid #f2dfaf;
  box-shadow:
    inset 0 0 0 2px rgba(84, 119, 114, 0.08),
    inset 0 18px 45px rgba(255, 255, 255, 0.2);
}

.world-art {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.label-line {
  stroke: rgba(59, 77, 70, 0.32);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-dasharray: 2 4;
}

.route-point {
  position: absolute;
  width: 17px;
  height: 17px;
  transform: translate(-50%, -50%);
  border: 3px solid #fffaf0;
  border-radius: 50%;
  background: #7d8b83;
  box-shadow:
    0 4px 10px rgba(0, 0, 0, 0.24),
    inset 0 -2px 0 rgba(0, 0, 0, 0.15);
  z-index: 3;
}

.route-point::after {
  content: "";
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  border: 1px solid rgba(255, 247, 223, 0.35);
}

.route-point.done {
  background: var(--green);
}

.route-point.current {
  width: 24px;
  height: 24px;
  background: var(--gold);
  border-color: var(--ink);
  box-shadow:
    0 0 0 6px rgba(231, 175, 54, 0.24),
    0 8px 16px rgba(50, 40, 22, 0.28);
}

.route-label {
  position: absolute;
  min-width: 0;
  max-width: 118px;
  transform: translate(-50%, -50%);
  color: #1f3933;
  font-size: 10.5px;
  font-weight: 900;
  line-height: 1.1;
  text-align: center;
  background: rgba(255, 247, 223, 0.88);
  border: 1px solid rgba(91, 69, 35, 0.18);
  border-radius: 999px;
  box-shadow: 0 3px 9px rgba(45, 70, 66, 0.13);
  padding: 4px 7px;
  white-space: nowrap;
  z-index: 4;
}

.balloon {
  position: absolute;
  width: 52px;
  height: 72px;
  transform: translate(-50%, -92%);
  transition: left 0.45s ease, top 0.45s ease;
  z-index: 5;
  animation: balloonFloat 2.8s ease-in-out infinite;
}

.balloon-top {
  position: absolute;
  top: 0;
  left: 50%;
  width: 48px;
  height: 55px;
  transform: translateX(-50%);
  border: 3px solid #7a2d23;
  border-radius: 50% 50% 46% 46%;
  background:
    linear-gradient(90deg, transparent 47%, rgba(122, 45, 35, 0.45) 48% 52%, transparent 53%),
    radial-gradient(circle at 35% 28%, #ffd46a 0 18%, transparent 19%),
    linear-gradient(135deg, #e94f3d 0 48%, #f4b83e 49% 100%);
  box-shadow: 0 10px 18px rgba(39, 45, 42, 0.25);
}

.balloon-basket {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 20px;
  height: 15px;
  transform: translateX(-50%);
  border: 2px solid #74432d;
  border-radius: 3px;
  background: #a9683d;
}

.balloon-basket::before,
.balloon-basket::after {
  content: "";
  position: absolute;
  bottom: 14px;
  width: 2px;
  height: 12px;
  background: #74432d;
}

.balloon-basket::before {
  left: 1px;
  transform: rotate(-16deg);
}

.balloon-basket::after {
  right: 1px;
  transform: rotate(16deg);
}

@keyframes balloonFloat {
  0%,
  100% {
    margin-top: 0;
  }
  50% {
    margin-top: -5px;
  }
}

.question-panel {
  min-width: 0;
}

.question-card,
.result-card {
  padding: 22px;
  position: relative;
  background:
    linear-gradient(180deg, rgba(255, 252, 239, 0.95), rgba(255, 244, 212, 0.95)),
    var(--panel);
}

.question-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.step-chip {
  flex: none;
  border: 1px solid rgba(121, 82, 51, 0.22);
  border-radius: 999px;
  background: #f3dfaa;
  color: #5b4523;
  font-size: 12px;
  font-weight: 900;
  padding: 6px 10px;
}

.question-card h2,
.result-card h2 {
  margin: 8px 0 18px;
  font-size: clamp(21px, 2.4vw, 30px);
  line-height: 1.17;
}

.answers {
  display: grid;
  gap: 11px;
}

.answer-button,
.primary-button {
  width: 100%;
  min-height: 52px;
  border: 2px solid #b9a06d;
  border-radius: 8px;
  background: #fff6dc;
  color: var(--ink);
  cursor: pointer;
  font-weight: 800;
  line-height: 1.2;
  padding: 10px 12px;
  text-align: left;
  transition: transform 0.15s ease, box-shadow 0.15s ease, background 0.15s ease;
  box-shadow: inset 0 -3px 0 rgba(121, 82, 51, 0.08);
}

.answer-button {
  display: grid;
  grid-template-columns: 34px 1fr;
  align-items: center;
  gap: 10px;
}

.answer-letter {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #2c685b;
  color: #fff7df;
  font-weight: 900;
  box-shadow: inset 0 -2px 0 rgba(0, 0, 0, 0.18);
}

.answer-button:hover,
.primary-button:hover {
  transform: translateY(-1px);
  box-shadow:
    inset 0 -3px 0 rgba(121, 82, 51, 0.08),
    0 8px 16px rgba(50, 46, 30, 0.13);
}

.answer-button.correct {
  background: #d6edc3;
  border-color: #5f9a4f;
}

.answer-button.debug-correct {
  border-color: #348b44;
  box-shadow:
    inset 0 -3px 0 rgba(52, 139, 68, 0.14),
    0 0 0 3px rgba(52, 139, 68, 0.2);
}

.answer-button.wrong {
  background: #f5c5b7;
  border-color: #bd5c49;
}

.answer-button.correct .answer-letter {
  background: #477f38;
}

.answer-button.debug-correct .answer-letter {
  background: #348b44;
}

.answer-button.wrong .answer-letter {
  background: #a53e32;
}

.answer-button:disabled {
  cursor: default;
}

.primary-button {
  background: var(--green);
  border-color: var(--green);
  color: #fffaf0;
  text-align: center;
  min-height: 54px;
}

.final-stats {
  display: grid;
  gap: 10px;
  margin-bottom: 18px;
}

.final-stats span {
  display: flex;
  justify-content: space-between;
  border: 2px solid rgba(121, 82, 51, 0.18);
  border-radius: 8px;
  padding: 13px 14px;
  background: #fff7df;
  font-weight: 800;
}

.hidden {
  display: none;
}

@media (max-width: 920px) {
  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .score-row {
    width: 100%;
    justify-content: stretch;
  }

  .score-pill {
    flex: 1;
  }

  .game-layout {
    grid-template-columns: 1fr;
  }

  .map-viewport {
    aspect-ratio: 1000 / 610;
  }
}

@media (max-width: 560px) {
  .app-shell {
    width: min(100% - 18px, 1180px);
    padding-top: 8px;
  }

  .map-panel,
  .question-card,
  .result-card {
    padding: 12px;
  }

  .question-meta {
    align-items: flex-start;
    flex-direction: column;
  }

  .route-label {
    display: block;
    max-width: 82px;
    font-size: 9px;
    padding: 3px 5px;
  }

  .route-point {
    width: 12px;
    height: 12px;
    border-width: 2px;
  }

  .route-point.current {
    width: 17px;
    height: 17px;
  }

  .balloon {
    width: 38px;
    height: 54px;
  }

  .balloon-top {
    width: 34px;
    height: 40px;
  }

  .answer-button {
    grid-template-columns: 30px 1fr;
    gap: 9px;
  }

  .answer-letter {
    width: 30px;
    height: 30px;
  }
}
