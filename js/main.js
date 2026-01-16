/**
 * Matt McCoy Portfolio - Main JavaScript
 * Handles modals, menu, cursor, and animations
 */

document.addEventListener('DOMContentLoaded', () => {
  // Custom Cursor
  const cursor = document.querySelector('.cursor');

  if (cursor && window.matchMedia('(hover: hover)').matches) {
    document.addEventListener('mousemove', (e) => {
      cursor.style.left = e.clientX + 'px';
      cursor.style.top = e.clientY + 'px';
    });

    // Add hover effect to interactive elements
    const interactiveElements = document.querySelectorAll('a, button, [data-modal], .work-card, .project-card, .music-content');
    interactiveElements.forEach(el => {
      el.addEventListener('mouseenter', () => cursor.classList.add('hover'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('hover'));
    });
  }

  // Menu Toggle
  const navToggle = document.querySelector('.nav__toggle');
  const menuOverlay = document.querySelector('.menu-overlay');
  const menuLinks = document.querySelectorAll('.menu-overlay__link');

  if (navToggle && menuOverlay) {
    navToggle.addEventListener('click', () => {
      const isActive = menuOverlay.classList.contains('active');

      if (isActive) {
        menuOverlay.classList.remove('active');
        navToggle.querySelector('.nav__toggle-text').textContent = 'Menu';
        document.body.style.overflow = '';
      } else {
        menuOverlay.classList.add('active');
        navToggle.querySelector('.nav__toggle-text').textContent = 'Close';
        document.body.style.overflow = 'hidden';

        // Stagger animation for menu links
        menuLinks.forEach((link, i) => {
          link.style.transitionDelay = `${i * 0.05}s`;
        });
      }
    });

    // Close menu when clicking a link
    menuLinks.forEach(link => {
      link.addEventListener('click', () => {
        menuOverlay.classList.remove('active');
        navToggle.querySelector('.nav__toggle-text').textContent = 'Menu';
        document.body.style.overflow = '';
      });
    });
  }

  // Modal System
  const modalTriggers = document.querySelectorAll('[data-modal]');
  const modals = document.querySelectorAll('.modal');
  const modalCloseButtons = document.querySelectorAll('.modal__close');
  const modalBackdrops = document.querySelectorAll('.modal__backdrop');

  function openModal(modalId) {
    const modal = document.getElementById(`modal-${modalId}`);
    if (modal) {
      modal.classList.add('active');
      document.body.classList.add('modal-open');
    }
  }

  function closeModal(modal) {
    modal.classList.remove('active');
    document.body.classList.remove('modal-open');
  }

  function closeAllModals() {
    modals.forEach(modal => closeModal(modal));
  }

  // Open modal on trigger click
  modalTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
      const modalId = trigger.dataset.modal;
      openModal(modalId);
    });
  });

  // Close modal on close button click
  modalCloseButtons.forEach(button => {
    button.addEventListener('click', () => {
      const modal = button.closest('.modal');
      closeModal(modal);
    });
  });

  // Close modal on backdrop click
  modalBackdrops.forEach(backdrop => {
    backdrop.addEventListener('click', () => {
      const modal = backdrop.closest('.modal');
      closeModal(modal);
    });
  });

  // Close modal on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeAllModals();
    }
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href === '#') return;

      e.preventDefault();
      const target = document.querySelector(href);
      if (target) {
        const offset = 80;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;

        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // Current Time Display
  const timeElement = document.getElementById('current-time');

  function updateTime() {
    if (timeElement) {
      const now = new Date();
      const options = {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
        timeZone: 'America/New_York'
      };
      timeElement.textContent = now.toLocaleTimeString('en-US', options);
    }
  }

  updateTime();
  setInterval(updateTime, 60000);

  // Intersection Observer for animations
  const observerOptions = {
    root: null,
    rootMargin: '0px',
    threshold: 0.1
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  // Animate elements on scroll
  const animateElements = document.querySelectorAll('.work-card, .project-card, .music-content, .section__header');
  animateElements.forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = `opacity 0.6s ease ${i * 0.1}s, transform 0.6s ease ${i * 0.1}s`;
    observer.observe(el);
  });

  // Parallax effect on hero background
  const heroBg = document.querySelector('.hero__bg');

  if (heroBg) {
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      heroBg.style.transform = `translateY(${scrolled * 0.3}px)`;
    });
  }

  // Nav appearance on scroll
  const nav = document.querySelector('.nav');
  let lastScroll = 0;

  window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll > 100) {
      nav.style.mixBlendMode = 'normal';
      nav.style.background = 'rgba(10, 10, 10, 0.9)';
      nav.style.backdropFilter = 'blur(10px)';
    } else {
      nav.style.mixBlendMode = 'difference';
      nav.style.background = 'transparent';
      nav.style.backdropFilter = 'none';
    }

    lastScroll = currentScroll;
  });
});
