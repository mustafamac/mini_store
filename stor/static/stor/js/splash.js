/* ── Disney orbiting star on canvas ── */
(function () {
  const box    = document.getElementById('logoOrbit');
  const canvas = document.getElementById('starCanvas');
  const ctx    = canvas.getContext('2d');

  let W, H, cx, cy, rx, ry;
  function resize() {
    const r = box.getBoundingClientRect();
    W = canvas.width  = r.width;
    H = canvas.height = r.height;
    cx = W / 2; cy = H / 2;
    rx = W / 2 - 10;
    ry = H / 2 - 8;
  }
  resize();
  window.addEventListener('resize', resize);

  const TRAIL = 28;
  const history = [];
  let angle = -Math.PI / 2;
  const speed = (2 * Math.PI) / (3.0 * 60);

  /* Draw a 4-point Disney sparkle */
  function drawStar(x, y, size, alpha) {
    ctx.save();
    ctx.globalAlpha = alpha;
    ctx.translate(x, y);

    /* outer glow */
    const grd = ctx.createRadialGradient(0, 0, 0, 0, 0, size * 2.2);
    grd.addColorStop(0,   'rgba(28,180,140,0.55)');
    grd.addColorStop(0.4, 'rgba(28,180,140,0.18)');
    grd.addColorStop(1,   'rgba(28,180,140,0)');
    ctx.beginPath();
    ctx.arc(0, 0, size * 2.2, 0, Math.PI * 2);
    ctx.fillStyle = grd;
    ctx.fill();

    /* 4-point star shape */
    ctx.beginPath();
    const o = size, i = size * 0.22;
    ctx.moveTo(0, -o);
    ctx.quadraticCurveTo( i, -i,  o,  0);
    ctx.quadraticCurveTo( i,  i,  0,  o);
    ctx.quadraticCurveTo(-i,  i, -o,  0);
    ctx.quadraticCurveTo(-i, -i,  0, -o);
    ctx.closePath();
    ctx.fillStyle = '#1cb48c';
    ctx.fill();

    /* inner white shine */
    ctx.beginPath();
    const oi = size * 0.45, ii = size * 0.1;
    ctx.moveTo(0, -oi);
    ctx.quadraticCurveTo( ii, -ii,  oi,  0);
    ctx.quadraticCurveTo( ii,  ii,  0,  oi);
    ctx.quadraticCurveTo(-ii,  ii, -oi,  0);
    ctx.quadraticCurveTo(-ii, -ii,  0, -oi);
    ctx.closePath();
    ctx.fillStyle = 'rgba(255,255,255,0.55)';
    ctx.fill();

    ctx.restore();
  }

  /* tiny sparkle pop at trail tip */
  function drawSparkle(x, y, size, alpha) {
    ctx.save();
    ctx.globalAlpha = alpha * 0.7;
    ctx.translate(x, y);
    ctx.beginPath();
    const s = size;
    ctx.moveTo(0, -s); ctx.lineTo(0, s);
    ctx.moveTo(-s, 0); ctx.lineTo(s, 0);
    ctx.strokeStyle = '#1cb48c';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();
  }

  function frame() {
    ctx.clearRect(0, 0, W, H);

    angle += speed;
    const x = cx + rx * Math.cos(angle);
    const y = cy + ry * Math.sin(angle);

    history.unshift({ x, y });
    if (history.length > TRAIL) history.pop();

    /* draw fading trail */
    history.forEach((p, i) => {
      const t    = 1 - i / TRAIL;
      const size = 1.8 * t;
      ctx.beginPath();
      ctx.arc(p.x, p.y, Math.max(size, 0.3), 0, Math.PI * 2);
      ctx.fillStyle = `rgba(28,180,140,${0.55 * t})`;
      ctx.fill();

      /* occasional tiny sparkle along trail */
      if (i % 6 === 0 && i > 0) drawSparkle(p.x, p.y, 3.5 * t, t * 0.5);
    });

    /* draw main star */
    drawStar(x, y, 9, 1);

    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();

/* ── Loading bar ── */
(function () {
  const fill    = document.getElementById('fill');
  const overlay = document.getElementById('fade-overlay');
  const main    = document.getElementById('main-content');
  const dur     = 3000;
  const t0      = performance.now();
  function ease(t) { return t < 0.65 ? t * 1.38 : 0.897 + 0.103 * ((t - 0.65) / 0.35); }
  function tick(now) {
    const raw = Math.min((now - t0) / dur, 1);
    fill.style.width = Math.min(ease(raw) * 100, 100) + '%';
    if (raw < 1) { requestAnimationFrame(tick); return; }
    setTimeout(() => {
      overlay.classList.add('active');
      setTimeout(() => {
        document.getElementById('splash').style.display = 'none';
        main.style.display = 'flex';
        overlay.style.transition = 'opacity 0.45s ease';
        overlay.style.opacity = '0';
        setTimeout(() => { overlay.style.pointerEvents = 'none'; }, 450);
      }, 550);
    }, 150);
  }
  requestAnimationFrame(tick);
})();