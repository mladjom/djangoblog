document.addEventListener('DOMContentLoaded', () => {
  const navContainer = document.querySelector('.nav-container');
  const navToggler = document.querySelector('.nav-toggler');
  const navLinks = document.querySelector('.nav-links');
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

  // Toggle main navigation
  navToggler?.addEventListener('click', () => {
    const isExpanded = navToggler.getAttribute('aria-expanded') === 'true';
    navToggler.setAttribute('aria-expanded', !isExpanded);
    navLinks?.classList.toggle('show');
  });

  // Handle dropdowns
  dropdownToggles.forEach(toggle => {
    const dropdown = toggle.nextElementSibling;
    
    // Toggle dropdown on click
    toggle.addEventListener('click', (e) => {
      e.preventDefault();
      const isExpanded = toggle.getAttribute('aria-expanded') === 'true';
      
      // Close other open dropdowns
      dropdownToggles.forEach(otherToggle => {
        if (otherToggle !== toggle) {
          otherToggle.setAttribute('aria-expanded', 'false');
          otherToggle.nextElementSibling?.classList.remove('show');
        }
      });

      // Toggle current dropdown
      toggle.setAttribute('aria-expanded', !isExpanded);
      dropdown?.classList.toggle('show');
    });

    // Handle hover for desktop
    if (window.innerWidth > 768) {
      toggle.parentElement?.addEventListener('mouseenter', () => {
        toggle.setAttribute('aria-expanded', 'true');
        dropdown?.classList.add('show');
      });

      toggle.parentElement?.addEventListener('mouseleave', () => {
        toggle.setAttribute('aria-expanded', 'false');
        dropdown?.classList.remove('show');
      });
    }
  });

  // Close navigation when clicking outside
  document.addEventListener('click', (e) => {
    if (!navContainer.contains(e.target)) {
      navLinks?.classList.remove('show');
      navToggler?.setAttribute('aria-expanded', 'false');
      
      dropdownToggles.forEach(toggle => {
        toggle.setAttribute('aria-expanded', 'false');
        toggle.nextElementSibling?.classList.remove('show');
      });
    }
  });

  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      navLinks?.classList.remove('show');
      navToggler?.setAttribute('aria-expanded', 'false');
      
      dropdownToggles.forEach(toggle => {
        toggle.setAttribute('aria-expanded', 'false');
        toggle.nextElementSibling?.classList.remove('show');
      });
    }
  });

  // Focus trap for mobile navigation
  const focusableElements = navLinks?.querySelectorAll(
    'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );

  if (focusableElements?.length) {
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];

    navLinks?.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') {
        if (e.shiftKey && document.activeElement === firstFocusable) {
          e.preventDefault();
          lastFocusable.focus();
        } else if (!e.shiftKey && document.activeElement === lastFocusable) {
          e.preventDefault();
          firstFocusable.focus();
        }
      }
    });
  }
});