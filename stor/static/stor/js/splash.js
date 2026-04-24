(function () {

  /* ── لو المستخدم شاف الـ splash قبل كده — اخرج على طول ── */
  if (sessionStorage.getItem('splashSeen')) {
    var s = document.getElementById('itqan-splash');
    var o = document.getElementById('fade-overlay');
    if (s) s.style.display = 'none';
    if (o) o.style.display = 'none';
    return;
  }

  /* ══════════════════════════════════════
     ORBIT ANIMATION
  ══════════════════════════════════════ */
  var cx = 130, cy = 55, rx = 122, ry = 48;
  var star  = document.getElementById('star-pos');
  var t1    = document.getElementById('t1');
  var t2    = document.getElementById('t2');
  var t3    = document.getElementById('t3');
  var shape = document.getElementById('sparkle-shape');

  var PERIOD    = 3200;
  var TRAIL_LAG = [0.06, 0.12, 0.19];

  function pos(angle) {
    return {
      x: cx + rx * Math.cos(angle),
      y: cy + ry * Math.sin(angle)
    };
  }

  function orbitTick(now) {
    var t     = (now % PERIOD) / PERIOD;
    var angle = t * Math.PI * 2 - Math.PI / 2;
    var p     = pos(angle);

    star.setAttribute('transform', 'translate(' + p.x + ',' + p.y + ')');

    var rot   = (now * 0.12) % 360;
    var pulse = 0.8 + 0.4 * Math.abs(Math.sin(now * 0.003));
    shape.setAttribute('transform', 'rotate(' + rot + ')');
    shape.style.transform       = 'rotate(' + rot + 'deg) scale(' + pulse + ')';
    shape.style.transformOrigin = '0 0';

    [t1, t2, t3].forEach(function (dot, i) {
      var ta = angle - TRAIL_LAG[i] * Math.PI * 2;
      var tp = pos(ta);
      dot.setAttribute('cx', tp.x);
      dot.setAttribute('cy', tp.y);
    });

    requestAnimationFrame(orbitTick);
  }
  requestAnimationFrame(orbitTick);

  /* ══════════════════════════════════════
     LOADING BAR
  ══════════════════════════════════════ */
  var fill    = document.getElementById('fill');
  var overlay = document.getElementById('fade-overlay');
  var splash  = document.getElementById('itqan-splash');
  var dur     = 2800;
  var t0      = performance.now();

  function ease(t) {
    return t < 0.65 ? t * 1.38 : 0.897 + 0.103 * ((t - 0.65) / 0.35);
  }

  function loaderTick(now) {
    var raw = Math.min((now - t0) / dur, 1);
    var val = Math.min(ease(raw) * 100, 100);
    fill.style.width = val + '%';

    if (raw < 1) { requestAnimationFrame(loaderTick); return; }

    /* انتهى التحميل — fade out ثم اخفي الـ splash */
    setTimeout(function () {
      overlay.classList.add('active');
      setTimeout(function () {
        splash.style.display  = 'none';
        overlay.style.transition = 'opacity 0.45s ease';
        overlay.style.opacity    = '0';
        sessionStorage.setItem('splashSeen', '1');
        setTimeout(function () {
          overlay.style.pointerEvents = 'none';
        }, 450);
      }, 550);
    }, 150);
  }
  requestAnimationFrame(loaderTick);

})();