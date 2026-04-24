(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {

        /* ── Scroll Progress Bar ─────────────────── */
        var pg = document.getElementById('pg');
        if (pg) {
            window.addEventListener('scroll', function () {
                var s = document.documentElement.scrollTop || document.body.scrollTop;
                var h = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                pg.style.width = h > 0 ? (s / h * 100) + '%' : '0%';
            }, { passive: true });
        }

        /* ── Mobile Menu ─────────────────────────── */
        var menuToggle = document.querySelector('.menu-toggle');
        var closeMenuBtn = document.querySelector('.close-menu');
        var mobileNav = document.getElementById('mobileNav');

        if (menuToggle && mobileNav) {
            menuToggle.addEventListener('click', function () {
                mobileNav.classList.add('active');
                menuToggle.classList.add('active');
                document.body.classList.add('no-scroll');
            });

            function closeMobileMenu() {
                mobileNav.classList.remove('active');
                menuToggle.classList.remove('active');
                document.body.classList.remove('no-scroll');
            }

            if (closeMenuBtn) closeMenuBtn.addEventListener('click', closeMobileMenu);

            mobileNav.querySelectorAll('a').forEach(function (link) {
                link.addEventListener('click', closeMobileMenu);
            });

            mobileNav.addEventListener('click', function (e) {
                if (e.target === mobileNav) closeMobileMenu();
            });
        }

        /* ── Home link — scroll to Hot Sale on index page ── */
        function isIndexPage() {
            var p = window.location.pathname;
            return p === '/' || p === '/index' || p === '/index.html';
        }

        function scrollToHotSale(e) {
            if (!isIndexPage()) {
                e.preventDefault();
                window.location.href = '/#hotSaleSection';
                return;
            }
            var hotSale = document.getElementById('hotSaleSection');
            if (hotSale) {
                e.preventDefault();
                hotSale.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }

        var homeLink = document.getElementById('homeLink');
        var mobileHomeLink = document.getElementById('mobileHomeLink');
        if (homeLink) homeLink.addEventListener('click', scrollToHotSale);
        if (mobileHomeLink) mobileHomeLink.addEventListener('click', scrollToHotSale);

        /* ── Handle hash scroll on page load ─────── */
        if (window.location.hash) {
            var target = document.getElementById(window.location.hash.substring(1));
            if (target) {
                setTimeout(function () {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 300);
            }
        }

        /* ── Handle product scroll from sliders ────── */
        var urlParams = new URLSearchParams(window.location.search);
        var scrollToSlug = urlParams.get('scroll_to');
        if (scrollToSlug) {
            var productElement = document.getElementById('product-' + scrollToSlug);
            if (productElement) {
                setTimeout(function () {
                    productElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
        }

        /* ── Auto-scroll to first product on cart page ── */
        if (window.location.pathname.indexOf('/cart') !== -1) {
            var firstProduct = document.querySelector('.summary-item');
            if (firstProduct) {
                setTimeout(function () {
                    firstProduct.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 400);
            }
        }

        /* ── Hero HOT SALE button ────────────────── */
        var heroHotSaleBtn = document.getElementById('heroHotSaleBtn');
        if (heroHotSaleBtn) {
            heroHotSaleBtn.addEventListener('click', function (e) {
                var hotSale = document.getElementById('hotSaleSection');
                if (hotSale) {
                    e.preventDefault();
                    hotSale.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        }

        /* ── Hero BROWSE button ────────────────── */
        var heroBrowseBtn = document.getElementById('heroBrowseBtn');
        if (heroBrowseBtn) {
            heroBrowseBtn.addEventListener('click', function (e) {
                var latestProducts = document.getElementById('latestProducts');
                if (latestProducts) {
                    e.preventDefault();
                    latestProducts.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        }

        /* ── Cart nav — scroll to confirm form if on cart page ── */
        document.querySelectorAll('a.nav-cart, a.mobile-cart-link').forEach(function (link) {
            link.addEventListener('click', function (e) {
                if (window.location.pathname.indexOf('/cart') === -1) return;
                var confirmForm = document.getElementById('confirmOrderForm');
                if (confirmForm) {
                    e.preventDefault();
                    confirmForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            });
        });

        /* ══════════════════════════════════════════
           PRODUCT SLIDER — Infinite Loop & Parallax
           - Clones one set of cards after originals for seamless wrap
           - Starts visible at position 0 (first card in view)
           - Boundary "pre-jump" (no transition) before animating one step so
             RTL arrows never animate across a full strip (blank / fast sweep)
           - Loop length = offset from first original to first clone (layout; works with variable widths)
           - Step = distance between two original cards (one card + gap)
           - Opposite parallax movement on page scroll
        ══════════════════════════════════════════ */

        var slidersRegistry = [];
        var lastGlobalScrollPos = window.scrollY;
        var PARALLAX_SPEED = 0.3;

        /** Parallax fights vertical scrolling on phones; keep slider transform user-driven only there. */
        function allowSliderParallax() {
            if (window.matchMedia('(max-width: 768px)').matches) return false;
            if (window.matchMedia('(pointer: coarse)').matches) return false;
            return true;
        }

        function initSlider(sliderId, trackId, movementMultiplier) {
            var slider = document.getElementById(sliderId);
            var track = document.getElementById(trackId);
            if (!slider || !track) return null;

            /* ── Collect only the original server-rendered cards ── */
            var originalCards = Array.from(track.querySelectorAll('.product-card:not([data-clone])'));
            var originalCount = originalCards.length;
            if (originalCount === 0) return null;

            /* ── Clone one full set and append (for seamless infinite wrap) ── */
            originalCards.forEach(function (card) {
                var clone = card.cloneNode(true);
                clone.setAttribute('data-clone', 'true');
                track.appendChild(clone);
            });

            var wrapper = slider.closest('.slider-wrapper');
            var prevBtn = wrapper ? wrapper.querySelector('.slider-prev') : null;
            var nextBtn = wrapper ? wrapper.querySelector('.slider-next') : null;

            /* ── State ── */
            var isDragging = false;
            var touchDeciding = false; // touch: wait for horizontal vs vertical gesture
            var startTouchX = 0;
            var startTouchY = 0;
            var startX = 0;
            var currentPos = 0;       // current translateX value in px
            var dragDistance = 0;
            var animating = false;
            var cardStep = 0;           // px per card (left edge → next left edge)
            var gap = 24;
            var GESTURE_THRESHOLD = 10;
            /** px tolerance for infinite boundary (float / subpixel / parallax) */
            var LOOP_EDGE_EPS = 3;

            /* ── Helpers ── */
            function refreshGap() {
                var style = window.getComputedStyle(track);
                gap = parseFloat(style.gap) || 24;
            }

            /** One infinite period: layout distance first original → first clone (incl. gap before clone). */
            function measureLoopPeriodPx() {
                refreshGap();
                var firstClone = track.querySelector('.product-card[data-clone="true"]');
                var o0 = originalCards[0];
                if (!firstClone || !o0) return 0;
                var byClone = firstClone.offsetLeft - o0.offsetLeft;
                if (byClone > 0.5) return byClone;
                var sumW = 0;
                originalCards.forEach(function (c) { sumW += c.offsetWidth; });
                return sumW + originalCount * gap;
            }

            /** Distance to next card (for arrows, snap, drag). */
            function measureCardStepPx() {
                if (originalCount <= 1) return measureLoopPeriodPx();
                var o0 = originalCards[0];
                var o1 = originalCards[1];
                var byOff = o1.offsetLeft - o0.offsetLeft;
                if (byOff > 0.5) return byOff;
                return o0.offsetWidth + gap;
            }

            function updateMetrics() {
                cardStep = measureCardStepPx();
            }

            function oneSetWidth() {
                return measureLoopPeriodPx();
            }

            /* ── Position setter with infinite wrap ── */
            function setPos(pos, animate) {
                if (animating && animate) return;

                var setW = oneSetWidth();
                if (setW > 0) {
                    // Wrap: keep pos between -setW and 0
                    // When we scroll past all originals (pos < -setW), jump back
                    // When we scroll before 0 (pos > 0), jump to end of originals
                    while (pos < -setW) pos += setW;
                    while (pos > 0) pos -= setW;
                }

                if (animate) {
                    animating = true;
                    track.style.transition = 'transform .4s cubic-bezier(.4,0,.2,1)';
                    setTimeout(function () {
                        track.style.transition = 'none';
                        animating = false;
                    }, 420);
                } else {
                    track.style.transition = 'none';
                }

                track.style.transform = 'translateX(' + pos + 'px)';
                currentPos = pos;
            }

            /* ── Navigate by one card ── */
            function moveByCards(count, animate) {
                if (animating) return;
                var setW = measureLoopPeriodPx();
                var step = measureCardStepPx();
                if (setW <= 0 || step <= 0) return;
                cardStep = step;

                /* Seamless infinite: shift by one full period invisibly, then animate only one card width. */
                if (animate) {
                    if (count > 0 && currentPos <= -setW + LOOP_EDGE_EPS) {
                        setPos(currentPos + setW, false);
                    } else if (count < 0 && currentPos >= -LOOP_EDGE_EPS) {
                        setPos(currentPos - setW, false);
                    }
                }

                var target = currentPos - (count * step);
                setPos(target, animate);
            }

            /* ── Arrow buttons (always enabled — infinite) ── */
            if (prevBtn) {
                prevBtn.classList.remove('disabled');
                prevBtn.style.pointerEvents = '';
                prevBtn.style.opacity = '';
                prevBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    moveByCards(-1, true);   // scroll track right → show previous
                });
            }
            if (nextBtn) {
                nextBtn.classList.remove('disabled');
                nextBtn.style.pointerEvents = '';
                nextBtn.style.opacity = '';
                nextBtn.addEventListener('click', function (e) {
                    e.preventDefault();
                    moveByCards(1, true);    // scroll track left → show next
                });
            }

            /* ── Drag (mouse + touch) — touch uses direction lock so vertical page scroll is not stolen ── */
            function onDragStart(e) {
                if (animating) return;
                var p = e.touches ? e.touches[0] : e;
                if (e.touches) {
                    touchDeciding = true;
                    isDragging = false;
                    startTouchX = p.clientX;
                    startTouchY = p.clientY;
                } else {
                    touchDeciding = false;
                    isDragging = true;
                }
                dragDistance = 0;
                startX = p.clientX;
                track.style.transition = 'none';
            }
            function onDragMove(e) {
                var p = e.touches ? e.touches[0] : e;
                if (!p) return;

                if (touchDeciding && e.touches) {
                    var dx = p.clientX - startTouchX;
                    var dy = p.clientY - startTouchY;
                    if (Math.abs(dx) < GESTURE_THRESHOLD && Math.abs(dy) < GESTURE_THRESHOLD) return;
                    touchDeciding = false;
                    if (Math.abs(dy) >= Math.abs(dx)) {
                        return;
                    }
                    isDragging = true;
                    startX = p.clientX;
                }

                if (!isDragging) return;

                var x = p.clientX;
                var walk = x - startX;
                dragDistance += Math.abs(walk);
                startX = x;
                setPos(currentPos + walk, false);
            }
            function onDragEnd() {
                touchDeciding = false;
                if (!isDragging) return;
                isDragging = false;
                // Snap to nearest card edge
                if (cardStep > 0) {
                    var snapped = Math.round(currentPos / cardStep) * cardStep;
                    setPos(snapped, true);
                }
            }

            slider.addEventListener('mousedown', onDragStart);
            window.addEventListener('mousemove', onDragMove);
            window.addEventListener('mouseup', onDragEnd);
            slider.addEventListener('touchstart', onDragStart, { passive: true });
            window.addEventListener('touchmove', onDragMove, { passive: true });
            window.addEventListener('touchend', onDragEnd);

            /* Block link clicks that were really drags */
            track.querySelectorAll('a').forEach(function (link) {
                link.addEventListener('click', function (e) {
                    if (dragDistance > 10) e.preventDefault();
                });
            });

            /* ── Resize ── */
            window.addEventListener('resize', function () {
                updateMetrics();
                setPos(currentPos, false);
            });

            /* ── Boot ── */
            updateMetrics();
            setPos(0, false);   // start with first card visible

            /* ── Public API for parallax ── */
            return {
                slider: slider,
                track: track,
                getPos: function () { return currentPos; },
                setPos: setPos,
                multiplier: movementMultiplier,
                isInViewport: function () {
                    var rect = slider.getBoundingClientRect();
                    return rect.top < window.innerHeight && rect.bottom > 0;
                }
            };
        }

        /* ── Initialize both sliders ── */
        var productsSliderCtrl = initSlider('productsSlider', 'productsTrack', 1);
        var featuredSliderCtrl = initSlider('featuredSlider', 'featuredTrack', -1);

        if (productsSliderCtrl) slidersRegistry.push(productsSliderCtrl);
        if (featuredSliderCtrl) slidersRegistry.push(featuredSliderCtrl);

        /* ── Global scroll → parallax (desktop / fine pointer only — avoids jank & conflict with mobile scroll) ── */
        window.addEventListener('scroll', function () {
            var scrollPos = window.scrollY;
            var diff = scrollPos - lastGlobalScrollPos;
            lastGlobalScrollPos = scrollPos;

            if (diff === 0 || !allowSliderParallax()) return;

            slidersRegistry.forEach(function (ctrl) {
                if (!ctrl.isInViewport()) return;
                var delta = diff * PARALLAX_SPEED * ctrl.multiplier;
                ctrl.setPos(ctrl.getPos() - delta, false);
            });
        }, { passive: true });

        /* ── Countdown Timers ───────────────────── */
        function initCountdowns() {
            var timers = document.querySelectorAll('.slim-timer');
            if (!timers.length) return;

            function pad(n) { return String(n).padStart(2, '0'); }

            function tick() {
                var now = Date.now();
                timers.forEach(function (timer) {
                    var endStr = timer.getAttribute('data-endtime');
                    if (!endStr) return;
                    var diff = new Date(endStr).getTime() - now;
                    var span = timer.querySelector('.timer-val');
                    if (!span) return;

                    if (diff <= 0) {
                        span.textContent = 'انتهى العرض';
                        timer.style.background = 'rgba(139,0,0,.9)';
                        return;
                    }
                    var d = Math.floor(diff / 86400000);
                    var h = Math.floor((diff % 86400000) / 3600000);
                    var m = Math.floor((diff % 3600000) / 60000);
                    var s = Math.floor((diff % 60000) / 1000);
                    span.textContent = (d > 0 ? d + 'د:' : '') + pad(h) + ':' + pad(m) + ':' + pad(s);
                });
            }

            tick();
            setInterval(tick, 1000);
        }

        /* ── Reveal on scroll for shared blocks ───── */
        function initRevealOnScroll() {
            var revealTargets = document.querySelectorAll(
                '.card, .product-card, .feature-card, .checkout-card, .contact-info, .social-section, .summary-item'
            );
            if (!revealTargets.length) return;

            if (!('IntersectionObserver' in window)) {
                revealTargets.forEach(function (el) { el.classList.add('is-visible'); });
                return;
            }

            revealTargets.forEach(function (el) { el.classList.add('reveal-on-scroll'); });

            var observer = new IntersectionObserver(function (entries, obs) {
                entries.forEach(function (entry) {
                    if (!entry.isIntersecting) return;
                    entry.target.classList.add('is-visible');
                    obs.unobserve(entry.target);
                });
            }, { threshold: 0.14, rootMargin: '0px 0px -40px 0px' });

            revealTargets.forEach(function (el) { observer.observe(el); });
        }

        initRevealOnScroll();
        initCountdowns();

        /* ══════════════════════════════════════════
           CART FUNCTIONALITY
           - Read cart data from data attributes
           - Quantity controls (+/-)
           - Remove items
           - Order form validation & submit
        ══════════════════════════════════════════ */

        (function () {
            var cartData = Array.from(
                document.querySelectorAll('.summary-item[data-product-id]')
            ).map(function (row) {
                return {
                    id:    parseInt(row.dataset.productId),
                    name:  row.dataset.productName,
                    price: parseFloat(row.dataset.unitPrice),
                    qty:   parseInt(row.dataset.qty)
                };
            });

            if (!cartData.length) return;

            var quantities = {};
            cartData.forEach(function(p) { quantities[p.id] = p.qty; });

            var summaryList  = document.getElementById('summaryList');
            var grandTotalEl = document.getElementById('grandTotal');

            function renderTotals() {
                if (!summaryList) return;
                summaryList.innerHTML = '';
                var total = 0;

                cartData.forEach(function(p) {
                    var qty = quantities[p.id] || 0;
                    if (qty <= 0) return;
                    var line = qty * p.price;
                    total += line;

                    var row = document.querySelector('.summary-item[data-product-id="' + p.id + '"] .item-total');
                    if (row) row.textContent = line.toLocaleString('ar-EG') + ' ج.م';

                    var div = document.createElement('div');
                    div.style.cssText = 'display:flex;justify-content:space-between;font-size:14px;color:var(--ink-70);margin-bottom:8px;';
                    div.innerHTML = '<span>' + p.name + ' × ' + qty + '</span><span style="font-weight:700;color:var(--ink);">' + line.toLocaleString('ar-EG') + ' ج.م</span>';
                    summaryList.appendChild(div);
                });

                if (grandTotalEl) grandTotalEl.textContent = total.toLocaleString('ar-EG') + ' ج.م';
            }

            renderTotals();

            // Quantity Controls
            document.querySelectorAll('.summary-item').forEach(function(row) {
                var id    = parseInt(row.dataset.productId);
                var minus = row.querySelector('.qty-minus');
                var plus  = row.querySelector('.qty-plus');
                var qtyEl = row.querySelector('.qty-value');

                if (minus) minus.addEventListener('click', function() {
                    if (quantities[id] > 1) {
                        quantities[id]--;
                        if (qtyEl) qtyEl.textContent = quantities[id];
                        renderTotals();
                    }
                });
                if (plus) plus.addEventListener('click', function() {
                    quantities[id]++;
                    if (qtyEl) qtyEl.textContent = quantities[id];
                    renderTotals();
                });
            });

            // Remove Item
            document.querySelectorAll('.remove-item-btn').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    var id  = parseInt(btn.dataset.id);
                    var row = btn.closest('.summary-item');
                    if (row) row.remove();
                    quantities[id] = 0;
                    var idx = cartData.findIndex(function(p) { return p.id === id; });
                    if (idx > -1) cartData.splice(idx, 1);
                    renderTotals();
                    if (!cartData.length) {
                        var container = document.getElementById('cartItemsContainer');
                        if (container) {
                            container.innerHTML = '<div class="empty-state" style="padding:40px 0;"><i class="fas fa-shopping-cart" style="font-size:48px;color:var(--tq-20);display:block;margin-bottom:16px;"></i><p>السلة فارغة.</p><a href="/products/" class="btn btn-primary mt-3">تصفح المنتجات</a></div>';
                        }
                    }
                });
            });

            // Scroll to confirm form
            var goToCheckoutBtn = document.getElementById('goToCheckoutBtn');
            if (goToCheckoutBtn) {
                goToCheckoutBtn.addEventListener('click', function() {
                    var formEl = document.getElementById('confirmOrderForm');
                    if (formEl) formEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
                });
            }

            // Order Form Submit
            var form         = document.getElementById('checkoutForm');
            var placeBtn     = document.getElementById('placeOrderBtn');
            var btnLabel     = placeBtn ? placeBtn.querySelector('.btn-label') : null;
            var btnLoading   = placeBtn ? placeBtn.querySelector('.btn-loading') : null;
            var successDiv   = document.getElementById('orderSuccess');
            var nameError    = document.getElementById('nameError');
            var phoneError   = document.getElementById('phoneError');
            var addressError = document.getElementById('addressError');

            if (!form) return;

            form.addEventListener('submit', function (e) {
                e.preventDefault();

                var valid = true;
                var name    = document.getElementById('fullName').value.trim();
                var phone   = document.getElementById('phoneNumber').value.trim();
                var address = document.getElementById('deliveryAddress').value.trim();
                var notes   = document.getElementById('additionalNotes').value.trim();

                if (nameError) nameError.classList.toggle('d-none', name.length > 1);
                if (name.length < 2) valid = false;

                var phoneRegex = /^(01)[0125][0-9]{8}$/;
                if (phoneError) phoneError.classList.toggle('d-none', phoneRegex.test(phone));
                if (!phoneRegex.test(phone)) valid = false;

                if (addressError) addressError.classList.toggle('d-none', address.length > 5);
                if (address.length < 6) valid = false;

                if (!valid) return;

                var orderItems = cartData.map(function(p) {
                    return {
                        product_id: p.id,
                        product_name: p.name,
                        quantity: quantities[p.id] || 0,
                        unit_price: p.price,
                        line_total: (quantities[p.id] || 0) * p.price
                    };
                }).filter(function(i) { return i.quantity > 0; });

                var payload = {
                    customer_name: name,
                    phone: phone,
                    address: address,
                    notes: notes,
                    items: orderItems,
                    total: orderItems.reduce(function(s, i) { return s + i.line_total; }, 0)
                };

                if (btnLabel && btnLoading) {
                    btnLabel.classList.add('d-none');
                    btnLoading.classList.remove('d-none');
                }
                if (placeBtn) placeBtn.disabled = true;

                fetch("{% url 'stor:place_order' %}", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(payload)
                }).then(function(response) {
                    if (response.ok) {
                        form.classList.add('d-none');
                        if (successDiv) successDiv.classList.remove('d-none');
                        successDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    } else {
                        throw new Error('Server error');
                    }
                }).catch(function() {
                    if (btnLabel && btnLoading) {
                        btnLabel.classList.remove('d-none');
                        btnLoading.classList.add('d-none');
                    }
                    if (placeBtn) placeBtn.disabled = false;
                    alert('حدث خطأ أثناء إرسال الطلب. من فضلك حاول مرة أخرى.');
                });
            });

        }());

    });
    
}());
