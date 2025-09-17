// app/static/js/app.js
console.log("NASA Flask App loaded");

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.querySelector('.nav-toggle');
  const nav = document.getElementById('main-nav');
  if (!btn || !nav) return;

  // Ensure initial state matches viewport
  const mql = window.matchMedia('(max-width: 768px)');
  const setInitial = () => {
    // Desktop: keep nav visible; Mobile: collapsed by default
    if (mql.matches) {
      btn.setAttribute('aria-expanded', 'false');
      nav.hidden = true;
    } else {
      btn.setAttribute('aria-expanded', 'false');
      nav.hidden = false;
    }
  };
  setInitial();
  mql.addEventListener('change', setInitial);

  const closeMenu = () => {
    btn.setAttribute('aria-expanded', 'false');
    nav.hidden = true; // reflect state for a11y
  };
  const openMenu = () => {
    btn.setAttribute('aria-expanded', 'true');
    nav.hidden = false;
  };

  // Toggle on button click
  btn.addEventListener('click', () => {
    const expanded = btn.getAttribute('aria-expanded') === 'true';
    if (expanded) {
      closeMenu();
      btn.focus(); // keep focus on button when closing
    } else {
      openMenu();
    }
  });

  // Close when clicking a nav link (mobile)
  nav.addEventListener('click', (e) => {
    if (e.target.closest('.nav-link')) closeMenu();
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && btn.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      btn.focus();
    }
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (
      btn.getAttribute('aria-expanded') === 'true' &&
      !btn.contains(e.target) &&
      !nav.contains(e.target)
    ) {
      closeMenu();
    }
  });

  // End the gradient loader as soon as DOM is ready
  const finish = () => document.body.classList.add('loaded');
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', finish, { once: true });
  } else {
    finish();
  }

  // Skeleton: remove placeholder when media finish loading
  const clearSkeleton = (el) => el.closest('.skeleton')?.classList.remove('skeleton');

  document.querySelectorAll('img').forEach((img) => {
    if (img.complete && img.naturalWidth > 0) {
      clearSkeleton(img);
    } else {
      img.addEventListener('load', () => clearSkeleton(img), { once: true });
      img.addEventListener('error', () => clearSkeleton(img), { once: true });
    }
  });

  document.querySelectorAll('iframe').forEach((frame) => {
    frame.addEventListener('load', () => clearSkeleton(frame), { once: true });
  });
});
