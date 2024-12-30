export class MainNavigation {
    constructor() {
      this.header = document.querySelector('.site-header');
      this.toggle = document.querySelector('.nav-toggle');
      this.nav = document.querySelector('.main-nav');
      this.navItems = this.nav?.querySelectorAll('.main-nav__item');
      this.dropdowns = this.nav?.querySelectorAll('.main-nav__submenu');
      this.isOpen = false;
  
      this.init();
    }
  
    init() {
      this.toggle.addEventListener('click', () => this.toggleMenu());
      window.addEventListener('resize', () => this.handleResize());
      window.addEventListener('scroll', () => this.handleScroll());
      this.initDropdowns();
      this.initFocusTrap();
      this.closeOnOutsideClick();
      this.closeOnEscape();
    }
  
    toggleMenu() {
      this.isOpen = !this.isOpen;
      this.toggle.setAttribute('aria-expanded', this.isOpen);
      this.nav.setAttribute('aria-expanded', this.isOpen);
  
      if (this.isOpen) {
        document.body.style.overflow = 'hidden';
      } else {
        document.body.style.overflow = '';
      }
    }
  
    handleResize() {
      if (window.innerWidth >= 768 && this.isOpen) {
        this.closeMenu();
      }
    }
  
    handleScroll() {
      const scrollTop = window.scrollY || document.documentElement.scrollTop;
      if (scrollTop > 0) {
        this.header.classList.add('site-header--scrolled');
      } else {
        this.header.classList.remove('site-header--scrolled');
      }
    }
  
    closeMenu() {
      this.isOpen = false;
      this.toggle.setAttribute('aria-expanded', false);
      this.nav.setAttribute('aria-expanded', false);
      document.body.style.overflow = '';
    }
  
    initDropdowns() {
      this.navItems.forEach((item) => {
        const link = item.querySelector('.main-nav__link');
        const submenu = item.querySelector('.main-nav__submenu');
        
        if (submenu) {
          // Set initial aria state
          link.setAttribute('aria-expanded', 'false');
          
          link.addEventListener('click', (e) => {
            e.preventDefault();
            const isExpanded = link.getAttribute('aria-expanded') === 'true';
            this.closeAllDropdowns();
            
            if (!isExpanded) {
              link.setAttribute('aria-expanded', 'true');
              submenu.classList.add('show');
            }
          });
        }
      });
    }
    
  
    closeAllDropdowns() {
      this.navItems.forEach((item) => {
        const toggle = item.querySelector('.main-nav__link');
        const submenu = item.querySelector('.main-nav__submenu');
        if (toggle && submenu) {
          toggle.setAttribute('aria-expanded', 'false');
          submenu.classList.remove('show');
        }
      });
    }
  
    closeOnOutsideClick() {
      document.addEventListener('click', (e) => {
        if (!this.nav.contains(e.target) && !this.toggle.contains(e.target)) {
          this.closeMenu();
          this.closeAllDropdowns();
        }
      });
    }
  
    closeOnEscape() {
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          this.closeMenu();
          this.closeAllDropdowns();
        }
      });
    }
  
    initFocusTrap() {
      const focusableElements = this.nav?.querySelectorAll(
        'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
  
      if (focusableElements?.length) {
        const firstFocusable = focusableElements[0];
        const lastFocusable = focusableElements[focusableElements.length - 1];
  
        this.nav.addEventListener('keydown', (e) => {
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
    }
  }
    