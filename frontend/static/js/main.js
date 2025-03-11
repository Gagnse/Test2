// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenu = document.getElementById('mobile-menu');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (mobileMenu) {
        mobileMenu.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            navbarMenu.classList.toggle('active');
        });
    }

    // Close mobile menu when clicking on a nav link
    const navLinks = document.querySelectorAll('.navbar-link');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            navbarMenu.classList.remove('active');
        });
    });

    // Highlight current page in navigation
    const currentLocation = location.pathname;

    navLinks.forEach(link => {
        const linkPath = link.getAttribute('href');

        if (currentLocation === linkPath) {
            link.classList.add('active');
        } else if (currentLocation !== '/' && linkPath !== '/' && currentLocation.includes(linkPath)) {
            // For subpages - highlights parent menu item
            link.classList.add('active');
        }
    });

    // Enhanced parallax scrolling effects
    const parallaxScroll = () => {
        const scrollPosition = window.pageYOffset;

        // Get all parallax elements
        const parallaxElements = document.querySelectorAll('.parallax-hero, .parallax-section');

        parallaxElements.forEach(element => {
            // Calculate how far the element is from the top of the page
            const elementTop = element.offsetTop;
            const elementHeight = element.offsetHeight;

            // Check if element is in view
            if (scrollPosition + window.innerHeight > elementTop &&
                scrollPosition < elementTop + elementHeight) {

                // Calculate the parallax offset
                const offset = (scrollPosition - elementTop) * 0.4;

                // Apply the parallax effect to the background
                const bgElement = element.querySelector('.parallax-bg') || element;
                if (bgElement.style) {
                    bgElement.style.backgroundPositionY = `calc(50% + ${offset}px)`;
                }
            }
        });

        // Fade in effect for feature cards
        const featureCards = document.querySelectorAll('.feature-card');
        featureCards.forEach(card => {
            const cardTop = card.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;

            if (cardTop < windowHeight * 0.75) {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            } else {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
            }
        });
    };

    // Add scroll event for parallax effect
    window.addEventListener('scroll', parallaxScroll);

    // Initial call to set positions
    parallaxScroll();

    // Add scroll-to-top button functionality
    const scrollToTopBtn = document.createElement('button');
    scrollToTopBtn.innerHTML = '↑';
    scrollToTopBtn.className = 'scroll-to-top';
    scrollToTopBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: #3498db;
        color: white;
        font-size: 24px;
        border: none;
        cursor: pointer;
        display: none;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    `;

    document.body.appendChild(scrollToTopBtn);

    scrollToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.style.display = 'block';
        } else {
            scrollToTopBtn.style.display = 'none';
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();

            const targetId = this.getAttribute('href');
            if (targetId === '#') return;

            const targetElement = document.querySelector(targetId);

            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80, // Account for fixed navbar
                    behavior: 'smooth'
                });
            }
        });
    });

    // Make feature cards initially hidden for animation
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
});