/**
 * ============================================
 * JARRY'S HOUSE — Shared JavaScript
 * ============================================
 */

document.addEventListener('DOMContentLoaded', () => {

  // ============================================
  // 1. SET FOOTER YEAR AUTOMATICALLY
  // ============================================
  const yearEls = document.querySelectorAll('.js-year');
  const currentYear = new Date().getFullYear();
  yearEls.forEach(el => {
    el.textContent = currentYear;
  });

  // ============================================
  // 2. MOBILE NAV HAMBURGER TOGGLE
  // ============================================
  const hamburger = document.querySelector('.navbar__hamburger');
  const navLinks  = document.querySelector('.navbar__links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      navLinks.classList.toggle('open');
      // aria
      const expanded = hamburger.classList.contains('open');
      hamburger.setAttribute('aria-expanded', expanded);
    });

    // Close nav when a link is clicked (mobile)
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        hamburger.classList.remove('open');
        navLinks.classList.remove('open');
        hamburger.setAttribute('aria-expanded', false);
      });
    });
  }

  // ============================================
  // 3. ACTIVE NAV LINK — based on current page
  // ============================================
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.navbar__links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  // ============================================
  // 4. SMOOTH SCROLL FOR ANCHOR LINKS
  // ============================================
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ============================================
  // 5. SCROLL REVEAL (IntersectionObserver)
  // ============================================
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target); // only trigger once
      }
    });
  }, {
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px'
  });

  // Observe single elements
  document.querySelectorAll('.reveal').forEach(el => {
    revealObserver.observe(el);
  });

  // Observe parent containers for staggered children
  document.querySelectorAll('.reveal-children').forEach(el => {
    revealObserver.observe(el);
  });

  // ============================================
  // 6. STAT BARS ANIMATION (team page)
  // ============================================
  const statObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const fills = entry.target.querySelectorAll('.stat-bar-fill');
        fills.forEach(fill => {
          const target = fill.dataset.width || '60%';
          // Small delay to let the element render before animating
          setTimeout(() => {
            fill.style.width = target;
          }, 100);
        });
        statObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll('.team-card').forEach(card => {
    statObserver.observe(card);
  });

  // ============================================
  // 7. PIXEL SPARKLE ON BUTTON HOVER
  // ============================================
  document.querySelectorAll('.btn-pixel').forEach(btn => {
    btn.addEventListener('mouseenter', (e) => {
      spawnSparkles(btn, 6);
    });
  });

  function spawnSparkles(parent, count) {
    const rect = parent.getBoundingClientRect();
    for (let i = 0; i < count; i++) {
      const spark = document.createElement('span');
      spark.style.cssText = `
        position: fixed;
        width: 6px;
        height: 6px;
        background: #fdcb6e;
        border-radius: 0;
        pointer-events: none;
        z-index: 9999;
        left: ${rect.left + Math.random() * rect.width}px;
        top: ${rect.top + Math.random() * rect.height}px;
        animation: sparkFly 0.5s ease forwards;
      `;
      document.body.appendChild(spark);
      setTimeout(() => spark.remove(), 550);
    }
  }

  // Inject sparkle keyframe
  if (!document.getElementById('sparkle-style')) {
    const style = document.createElement('style');
    style.id = 'sparkle-style';
    style.textContent = `
      @keyframes sparkFly {
        0%   { opacity: 1; transform: translate(0, 0) scale(1); }
        100% { opacity: 0; transform: translate(${randDir()}px, ${randDir()}px) scale(0); }
      }
    `;
    document.head.appendChild(style);
  }

  function randDir() {
    return (Math.random() - 0.5) * 40;
  }

  // ============================================
  // 8. GENERATE PIXEL STARS IN .pixel-bg
  // ============================================
  document.querySelectorAll('.pixel-bg').forEach(bg => {
    const count = parseInt(bg.dataset.stars || '40');
    for (let i = 0; i < count; i++) {
      const star = document.createElement('span');
      star.classList.add('star');
      const size = Math.random() < 0.7 ? 2 : 3;
      star.style.cssText = `
        width: ${size}px;
        height: ${size}px;
        top: ${Math.random() * 100}%;
        left: ${Math.random() * 100}%;
        --dur: ${1.5 + Math.random() * 2.5}s;
        --delay: -${Math.random() * 3}s;
        opacity: ${0.2 + Math.random() * 0.8};
      `;
      bg.appendChild(star);
    }
  });

  // ============================================
  // 9. GENERATE PIXEL CLOUDS
  // ============================================
  document.querySelectorAll('.pixel-bg').forEach(bg => {
    for (let i = 0; i < 3; i++) {
      const cloud = document.createElement('div');
      cloud.classList.add('pixel-cloud');
      const w = 60 + Math.random() * 80;
      const h = 20 + Math.random() * 20;
      cloud.style.cssText = `
        width: ${w}px;
        height: ${h}px;
        top: ${10 + Math.random() * 40}%;
        left: -200px;
        --dur: ${18 + Math.random() * 20}s;
        --delay: -${Math.random() * 15}s;
      `;
      bg.appendChild(cloud);
    }
  });

});

// ============================================
// 10. THE END SCREEN (used on final-level.html)
// ============================================
function showEndScreen() {
  let overlay = document.querySelector('.the-end-overlay');

  // Create if it doesn't exist yet
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.classList.add('the-end-overlay');
    overlay.setAttribute('role', 'dialog');
    overlay.setAttribute('aria-label', 'The End screen');
    overlay.innerHTML = `
      <p class="the-end-overlay__blackout" id="theEndBlackout">
        ... THE SCREEN GOES BLACK ...
      </p>
      <h1 class="the-end-overlay__title" id="theEndTitle">THE END</h1>
      <a href="index.html" class="btn-pixel the-end-overlay__replay" id="theEndReplay">
        ▶ PLAY AGAIN?
      </a>
    `;
    document.body.appendChild(overlay);
  }

  // Trigger overlay
  overlay.classList.add('active');

  // Sequence: blackout text → THE END → replay button
  const blackout = overlay.querySelector('#theEndBlackout');
  const title    = overlay.querySelector('#theEndTitle');
  const replay   = overlay.querySelector('#theEndReplay');

  setTimeout(() => {
    blackout.classList.add('show');
  }, 500);

  setTimeout(() => {
    title.classList.add('show');
  }, 2500);

  setTimeout(() => {
    replay.classList.add('show');
  }, 4500);

  // Allow ESC to close
  document.addEventListener('keydown', function escHandler(e) {
    if (e.key === 'Escape') {
      overlay.classList.remove('active');
      document.removeEventListener('keydown', escHandler);
    }
  });
}
