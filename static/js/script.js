document.addEventListener('DOMContentLoaded', function() {
    // --- Mobile Menu Toggle & Smooth Scrolling ---
    const menuToggle = document.getElementById('mobile-menu');
    const navMenu = document.querySelector('.nav-menu');
  
    if (menuToggle && navMenu) {
      menuToggle.addEventListener('click', function() {
        navMenu.classList.toggle('active');
        menuToggle.classList.toggle('active');
      });
  
      document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener('click', function(e) {
          e.preventDefault();
          const target = document.querySelector(this.getAttribute('href'));
          if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
          }
          // Close mobile menu if open
          if (navMenu.classList.contains('active')) {
            navMenu.classList.remove('active');
            menuToggle.classList.remove('active');
          }
        });
      });
    }
  
    // --- Intersection Observer for Reversible Slide-Up Animation ---
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
  
    if ('IntersectionObserver' in window) {
      const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.10 // Trigger when 10% of the element is visible
      };
  
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          } else {
            entry.target.classList.remove('visible');
          }
        });
      }, observerOptions);
  
      animatedElements.forEach(el => {
        observer.observe(el);
      });
    } else {
      // Fallback: show all elements immediately
      animatedElements.forEach(el => el.classList.add('visible'));
    }
  
    // // --- Simulate Processing on File Upload ---
    // const uploadForm = document.getElementById('file-upload-form');
    // const progressBar = document.getElementById('progress');
    // const progressText = document.getElementById('progress-text');
  
    // if (uploadForm) {
    //   uploadForm.addEventListener('submit', function(e) {
    //     e.preventDefault();
    //     simulateProcessing();
    //   });
    // }
  
    // function simulateProcessing() {
    //   let progress = 0;
    //   const interval = setInterval(() => {
    //     progress += 5;
    //     if (progress > 100) {
    //       progress = 100;
    //       clearInterval(interval);
    //       progressText.innerText = 'Processing completed';
    //     } else {
    //       progressText.innerText = progress + '% completed';
    //     }
    //     progressBar.style.width = progress + '%';
    //   }, 300); // Update every 300ms
    // }
  });
  