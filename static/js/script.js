// ===== Sticky header on scroll =====
const header = document.getElementById('siteHeader');
const onScroll = () => {
  if (window.scrollY > 40) header.classList.add('is-scrolled');
  else header.classList.remove('is-scrolled');
};
window.addEventListener('scroll', onScroll, { passive: true });
onScroll();

// ===== Mobile nav toggle =====
const navToggle = document.getElementById('navToggle');
const mainNav = document.getElementById('mainNav');
if (navToggle) {
  navToggle.addEventListener('click', () => {
    const open = mainNav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', open);
    document.body.classList.toggle('nav-open', open);
  });
  mainNav.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      mainNav.classList.remove('is-open');
      navToggle.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('nav-open');
    });
  });
}

// ===== Hero image fallback =====
// Shows the placeholder plate only if the photo actually fails to load —
// no longer depends on timing, so it can't get stuck showing after a
// cached refresh serves the image instantly.
const heroImg = document.getElementById('heroImg');
const heroFallback = document.getElementById('heroFallback');
if (heroImg && heroFallback) {
  heroImg.addEventListener('error', () => {
    heroFallback.style.display = 'block';
    heroImg.style.display = 'none';
  });
}

// ===== Stat counter (part of the hero's single load sequence) =====
document.querySelectorAll('.stat-num[data-count]').forEach(el => {
  const target = parseInt(el.getAttribute('data-count'), 10);
  let current = 0;
  const duration = 900;
  const start = performance.now() + 900;
  const step = (now) => {
    if (now < start) { requestAnimationFrame(step); return; }
    const progress = Math.min((now - start) / duration, 1);
    current = Math.floor(progress * target);
    el.textContent = current;
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target;
  };
  requestAnimationFrame(step);
});

// ===== Location route draw — single reveal, triggers once on scroll into view =====
const routeSvg = document.getElementById('routeSvg');
if (routeSvg) {
  const paths = routeSvg.querySelectorAll('.route-path');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        paths.forEach(p => p.classList.add('is-drawn'));
        observer.disconnect();
      }
    });
  }, { threshold: 0.4 });
  observer.observe(routeSvg);
}

// ===== Scroll reveal (section heads + grouped cards, once each) =====
const revealTargets = document.querySelectorAll('.reveal-on-scroll');
if (revealTargets.length) {
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
  revealTargets.forEach(el => revealObserver.observe(el));
}

// ===== Hero parallax (subtle, capped, skipped for reduced-motion) =====
const heroMedia = document.querySelector('.hero-media');
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (heroMedia && !prefersReducedMotion) {
  const heroSection = document.querySelector('.hero');
  const onParallax = () => {
    if (!heroSection) return;
    const rect = heroSection.getBoundingClientRect();
    if (rect.bottom < 0 || rect.top > window.innerHeight) return;
    const offset = Math.max(-40, Math.min(40, window.scrollY * 0.12));
    heroMedia.style.transform = `translateY(${offset}px)`;
  };
  window.addEventListener('scroll', onParallax, { passive: true });
  onParallax();
}

// ===== Move-in checklist carousel (homepage) =====
const checklistTrack = document.getElementById('checklistTrack');
const checklistPrev = document.getElementById('checklistPrev');
const checklistNext = document.getElementById('checklistNext');
if (checklistTrack && checklistPrev && checklistNext) {
  const scrollByCard = (dir) => {
    const card = checklistTrack.querySelector('.checklist-card');
    const gap = parseFloat(getComputedStyle(checklistTrack).gap) || 0;
    const distance = card ? card.getBoundingClientRect().width + gap : 300;
    checklistTrack.scrollBy({ left: dir * distance, behavior: 'smooth' });
  };
  checklistPrev.addEventListener('click', () => scrollByCard(-1));
  checklistNext.addEventListener('click', () => scrollByCard(1));

  const updateChecklistArrows = () => {
    const maxScroll = checklistTrack.scrollWidth - checklistTrack.clientWidth - 1;
    checklistPrev.setAttribute('aria-disabled', checklistTrack.scrollLeft <= 0);
    checklistNext.setAttribute('aria-disabled', checklistTrack.scrollLeft >= maxScroll);
  };
  checklistTrack.addEventListener('scroll', updateChecklistArrows, { passive: true });
  window.addEventListener('resize', updateChecklistArrows);
  updateChecklistArrows();

  // ---- Auto-premium slide: advances one card at a time on its own,
  // pauses the moment someone touches/hovers/focuses the carousel, and
  // resumes shortly after they let go. Off entirely for reduced motion.
  if (!prefersReducedMotion) {
    let autoplayTimer = null;
    const stopAutoplay = () => { if (autoplayTimer) clearInterval(autoplayTimer); };
    const startAutoplay = () => {
      stopAutoplay();
      autoplayTimer = setInterval(() => {
        const maxScroll = checklistTrack.scrollWidth - checklistTrack.clientWidth - 1;
        if (checklistTrack.scrollLeft >= maxScroll) {
          checklistTrack.scrollTo({ left: 0, behavior: 'smooth' });
        } else {
          scrollByCard(1);
        }
      }, 3800);
    };

    ['pointerenter', 'touchstart', 'focusin'].forEach(evt =>
      checklistTrack.addEventListener(evt, stopAutoplay, { passive: true })
    );
    ['pointerleave', 'touchend'].forEach(evt =>
      checklistTrack.addEventListener(evt, startAutoplay, { passive: true })
    );
    document.addEventListener('visibilitychange', () => {
      document.hidden ? stopAutoplay() : startAutoplay();
    });

    startAutoplay();
  }
}

// ===== Bottom nav active state on scroll (homepage only) =====
const bottomNavItems = document.querySelectorAll('.bottom-nav-item');
const sectionIds = ['top', 'apartments', 'location', 'enquire'];
const sections = sectionIds.map(id => document.getElementById(id)).filter(Boolean);

if (bottomNavItems.length && sections.length) {
  const setActive = (id) => {
    bottomNavItems.forEach(item => item.classList.toggle('is-active', item.dataset.target === id));
  };
  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => { if (entry.isIntersecting) setActive(entry.target.id); });
  }, { rootMargin: '-40% 0px -40% 0px' });
  sections.forEach(sec => sectionObserver.observe(sec));
}
