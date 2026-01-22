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
    const interactiveElements = document.querySelectorAll('a, button, [data-modal], .work-card, .project-card, .music-content, .archive-preview');
    interactiveElements.forEach(el => {
      el.addEventListener('mouseenter', () => {
        // Check if we're in contact section (dark background)
        const contactSection = el.closest('.section--contact');
        if (contactSection) {
          cursor.classList.add('hover', 'contact-section');
        } else {
          cursor.classList.add('hover');
        }
      });
      el.addEventListener('mouseleave', () => {
        cursor.classList.remove('hover', 'contact-section');
      });
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
      closeLightbox();
      closeAllModals();
    }
  });

  // Lightbox for gallery images and videos
  const lightbox = document.createElement('div');
  lightbox.className = 'lightbox';
  lightbox.innerHTML = `
    <div class="lightbox__backdrop"></div>
    <div class="lightbox__content">
      <button class="lightbox__close">&times;</button>
      <img class="lightbox__image" src="" alt="" />
      <video class="lightbox__video" controls autoplay loop muted playsinline>
        <source src="" type="video/mp4">
      </video>
      <p class="lightbox__caption"></p>
    </div>
  `;
  document.body.appendChild(lightbox);

  const lightboxImage = lightbox.querySelector('.lightbox__image');
  const lightboxVideo = lightbox.querySelector('.lightbox__video');
  const lightboxVideoSource = lightboxVideo.querySelector('source');
  const lightboxCaption = lightbox.querySelector('.lightbox__caption');
  const lightboxClose = lightbox.querySelector('.lightbox__close');
  const lightboxBackdrop = lightbox.querySelector('.lightbox__backdrop');

  function openLightbox(src, caption, isVideo = false) {
    if (isVideo) {
      lightboxImage.style.display = 'none';
      lightboxVideo.style.display = 'block';
      lightboxVideoSource.src = src;
      lightboxVideo.load();
      lightboxVideo.play();
    } else {
      lightboxVideo.style.display = 'none';
      lightboxImage.style.display = 'block';
      lightboxImage.src = src;
    }
    lightboxCaption.textContent = caption || '';
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    lightboxVideo.pause();
    // Always restore scroll when closing lightbox - modal handles its own overflow
    document.body.style.overflow = '';
    // If a modal is still open, let it manage overflow
    if (document.querySelector('.modal.active')) {
      document.body.classList.add('modal-open');
    }
  }

  // Add click handlers to gallery images and videos
  document.querySelectorAll('.modal__gallery-item').forEach(item => {
    item.style.cursor = 'pointer';
    item.addEventListener('click', (e) => {
      e.stopPropagation();
      const img = item.querySelector('img');
      const video = item.querySelector('video');
      const caption = item.querySelector('span');
      if (video) {
        const source = video.querySelector('source');
        openLightbox(source.src, caption ? caption.textContent : '', true);
      } else if (img) {
        openLightbox(img.src, caption ? caption.textContent : '', false);
      }
    });
  });

  lightboxClose.addEventListener('click', closeLightbox);
  lightboxBackdrop.addEventListener('click', closeLightbox);

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
