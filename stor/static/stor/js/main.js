/* -------- From base.html -------- */
(function () {
            var b = document.getElementById('pg');
            function tick() {
                var s = document.documentElement.scrollTop || document.body.scrollTop;
                var h = document.documentElement.scrollHeight - document.documentElement.clientHeight;
                b.style.width = h > 0 ? (s / h * 100) + '%' : '0%';
            }
            window.addEventListener('scroll', tick, { passive: true });

            var contactLink = document.getElementById('navContactLink');
            if (contactLink) {
                contactLink.addEventListener('click', function (e) {
                    e.preventDefault();
                    var footer = document.getElementById('footer');
                    if (footer) {
                        footer.scrollIntoView({ behavior: 'smooth' });
                        setTimeout(function () {
                            var socials = document.querySelectorAll('.social-icons a');
                            socials.forEach(function (icon) {
                                icon.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                                icon.style.transform = 'scale(1.15) translateY(-8px)';
                                icon.style.boxShadow = '0 8px 24px rgba(31,158,170,0.4)';
                                icon.style.background = 'rgba(31,158,170,0.2)';
                                icon.style.borderColor = 'var(--tq)';
                                icon.style.color = '#fff';

                                setTimeout(function () {
                                    icon.style.transform = '';
                                    icon.style.boxShadow = '';
                                    icon.style.background = '';
                                    icon.style.borderColor = '';
                                    icon.style.color = '';
                                }, 1500);
                            });
                        }, 500);
                    }
                });
            }
        }());


/* -------- From index.html -------- */
function initSlider(sliderId, trackId) {
        const slider = document.getElementById(sliderId);
        const track = document.getElementById(trackId);
        if (!slider || !track) return;

        let isDragging = false;
        let startX = 0;
        let startOffset = 0;
        let offset = 0;

        const getMaxOffset = () => {
            const containerWidth = slider.clientWidth;
            const trackWidth = track.scrollWidth;
            return Math.min(0, containerWidth - trackWidth);
        };

        const clamp = (value) => Math.min(0, Math.max(getMaxOffset(), value));

        const applyTransform = (instant = false) => {
            track.style.transition = instant ? 'none' : 'transform 0.1s linear';
            track.style.transform = `translate3d(${offset}px, 0, 0)`;
        };

        const onDragStart = (clientX) => {
            isDragging = true;
            startX = clientX;
            startOffset = offset;
            slider.style.cursor = 'grabbing';
        };

        const onDragMove = (clientX) => {
            if (!isDragging) return;
            const delta = clientX - startX;
            offset = clamp(startOffset + delta);
            applyTransform(true);
        };

        const onDragEnd = () => {
            isDragging = false;
            slider.style.cursor = 'grab';
        };

        slider.addEventListener('mousedown', (e) => {
            e.preventDefault();
            onDragStart(e.clientX);
        });
        window.addEventListener('mousemove', (e) => {
            if (isDragging) onDragMove(e.clientX);
        });
        window.addEventListener('mouseup', onDragEnd);

        slider.addEventListener('touchstart', (e) => onDragStart(e.touches[0].clientX), { passive: true });
        slider.addEventListener('touchmove', (e) => {
            if (isDragging) {
                // Prevent scrolling when dragging slider on touch devices
                e.preventDefault();
                onDragMove(e.touches[0].clientX);
            }
        }, { passive: false });
        slider.addEventListener('touchend', onDragEnd);

        // Handle window resize
        window.addEventListener('resize', () => {
            offset = clamp(offset);
            applyTransform(true);
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        initSlider('productsSlider', 'productsTrack');
        initSlider('featuredSlider', 'featuredTrack');
    });

    // Make CTA buttons link correctly to footer
    var navContactBtn = document.getElementById('navContactBtn');
    if (navContactBtn) {
        navContactBtn.addEventListener('click', function (e) {
            e.preventDefault();
            var footer = document.getElementById('footer');
            if (footer) {
                footer.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }
