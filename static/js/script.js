// ===== PackAxis Smooth Experience JavaScript =====

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar scroll effect with smooth transition
const navbar = document.querySelector('.navbar');
let lastScroll = 0;
let ticking = false;

function updateNavbar() {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 80) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
    
    lastScroll = currentScroll;
    ticking = false;
}

window.addEventListener('scroll', () => {
    if (!ticking) {
        requestAnimationFrame(updateNavbar);
        ticking = true;
    }
});

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });
}

// Close mobile menu when clicking on a link
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        hamburger?.classList.remove('active');
        navMenu?.classList.remove('active');
    });
});

// ===== Scroll-triggered animations with Intersection Observer =====
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -60px 0px'
};

// Create observer for fade-in animations
const animationObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            
            // Add stagger effect for grid items
            if (entry.target.classList.contains('stagger-children')) {
                entry.target.classList.add('visible');
            }
        }
    });
}, observerOptions);

// Observe elements that should animate on scroll
document.querySelectorAll('.animate-on-scroll, .stagger-children').forEach(el => {
    animationObserver.observe(el);
});

// Add animation classes to common elements
document.querySelectorAll('.feature-card, .product-card, .testimonial-card, .industry-card').forEach((el, index) => {
    el.classList.add('animate-on-scroll');
    el.classList.add(`delay-${(index % 4) + 1}`);
    animationObserver.observe(el);
});

// ===== Smooth Counter Animation =====
const animateCounter = (element, target, suffix = '') => {
    const duration = 2000;
    const startTime = performance.now();
    const startValue = 0;
    
    function easeOutExpo(t) {
        return t === 1 ? 1 : 1 - Math.pow(2, -10 * t);
    }
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easeOutExpo(progress);
        const currentValue = Math.floor(startValue + (target - startValue) * easedProgress);
        
        element.textContent = currentValue.toLocaleString() + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
};

// Observe stats section for counter animation
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const stats = entry.target.querySelectorAll('.stat-item h3, .stat-number');
            stats.forEach(stat => {
                const text = stat.textContent;
                const number = parseInt(text.replace(/\D/g, ''));
                const suffix = text.replace(/[0-9,]/g, '');
                if (number) {
                    stat.classList.add('counting');
                    animateCounter(stat, number, suffix);
                    setTimeout(() => stat.classList.remove('counting'), 2100);
                }
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.5 });

const heroStats = document.querySelector('.hero-stats');
if (heroStats) {
    statsObserver.observe(heroStats);
}

// ===== Smooth Hover Effects for Cards =====
document.querySelectorAll('.product-card, .feature-card, .industry-card').forEach(card => {
    card.classList.add('hover-lift');
});

// ===== Smooth Button Ripple Effect =====
function createRipple(event) {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    
    const ripple = document.createElement('span');
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.4);
        border-radius: 50%;
        transform: scale(0);
        animation: rippleEffect 0.6s ease-out forwards;
        pointer-events: none;
    `;
    
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    
    ripple.addEventListener('animationend', () => ripple.remove());
}

// Add ripple to buttons
document.querySelectorAll('.cta-button, .btn-primary, .btn-secondary, .auth-btn, .checkout-btn').forEach(button => {
    button.addEventListener('click', createRipple);
});

// Add ripple animation keyframes
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes rippleEffect {
        to {
            transform: scale(2.5);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);

// ===== Smooth Image Loading =====
document.querySelectorAll('img').forEach(img => {
    if (!img.complete) {
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.4s ease';
        img.addEventListener('load', () => {
            img.style.opacity = '1';
        });
    }
});

// ===== Smooth Cart Badge Animation =====
function animateCartBadge() {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.classList.remove('cart-badge-animate');
        void badge.offsetWidth; // Trigger reflow
        badge.classList.add('cart-badge-animate');
    }
}

// ===== Active Navigation State =====
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-link');

function updateActiveNav() {
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        if (pageYOffset >= sectionTop - 200) {
            current = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href')?.includes(current)) {
            link.classList.add('active');
        }
    });
}

window.addEventListener('scroll', () => {
    if (!ticking) {
        requestAnimationFrame(() => {
            updateActiveNav();
        });
    }
});

// ===== Smooth Form Focus States =====
document.querySelectorAll('input, textarea, select').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement?.classList.add('input-focused');
    });
    
    input.addEventListener('blur', function() {
        this.parentElement?.classList.remove('input-focused');
    });
});

// ===== Product Slider with Smooth Scrolling =====
const productsSlider = document.querySelector('.products-slider');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');

if (productsSlider && prevBtn && nextBtn) {
    const slideWidth = 300;
    const productSlides = productsSlider.querySelectorAll('.product-slide');
    
    if (productSlides.length <= 4) {
        nextBtn.style.display = 'none';
        prevBtn.style.display = 'none';
    }
    
    prevBtn.addEventListener('click', () => {
        productsSlider.scrollBy({
            left: -slideWidth,
            behavior: 'smooth'
        });
    });
    
    nextBtn.addEventListener('click', () => {
        productsSlider.scrollBy({
            left: slideWidth,
            behavior: 'smooth'
        });
    });
    
    // Smooth button opacity transitions
    productsSlider.addEventListener('scroll', () => {
        const maxScroll = productsSlider.scrollWidth - productsSlider.clientWidth;
        
        prevBtn.style.opacity = productsSlider.scrollLeft <= 0 ? '0.3' : '1';
        prevBtn.style.pointerEvents = productsSlider.scrollLeft <= 0 ? 'none' : 'auto';
        
        nextBtn.style.opacity = productsSlider.scrollLeft >= maxScroll - 5 ? '0.3' : '1';
        nextBtn.style.pointerEvents = productsSlider.scrollLeft >= maxScroll - 5 ? 'none' : 'auto';
    });
    
    prevBtn.style.opacity = '0.3';
    prevBtn.style.pointerEvents = 'none';
}

// ===== Smooth Toast Notifications =====
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
        <span class="toast-message">${message}</span>
    `;
    toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#2f2e0c' : type === 'error' ? '#ff6b6b' : '#333'};
        color: ${type === 'success' ? '#d4ff9e' : 'white'};
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 600;
        z-index: 10000;
        animation: toastIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Make showToast globally available
window.showToast = showToast;

// ===== Smooth Parallax Effect for Hero =====
const heroSection = document.querySelector('.hero');
if (heroSection) {
    const heroContent = heroSection.querySelector('.hero-content');
    const heroImage = heroSection.querySelector('.hero-image');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroHeight = heroSection.offsetHeight;
        
        if (scrolled < heroHeight) {
            const parallaxValue = scrolled * 0.3;
            if (heroContent) {
                heroContent.style.transform = `translateY(${parallaxValue * 0.5}px)`;
                heroContent.style.opacity = 1 - (scrolled / heroHeight) * 0.5;
            }
            if (heroImage) {
                heroImage.style.transform = `translateY(${parallaxValue * 0.2}px)`;
            }
        }
    });
}

// ===== Magnetic Button Effect =====
document.querySelectorAll('.cta-button, .nav-quote-btn').forEach(button => {
    button.addEventListener('mousemove', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        
        this.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px)`;
    });
    
    button.addEventListener('mouseleave', function() {
        this.style.transform = 'translate(0, 0)';
    });
});

// ===== Smooth Dropdown Hover =====
document.querySelectorAll('.nav-item-dropdown').forEach(item => {
    const dropdown = item.querySelector('.dropdown-menu');
    if (dropdown) {
        item.addEventListener('mouseenter', () => {
            dropdown.style.opacity = '1';
            dropdown.style.visibility = 'visible';
            dropdown.style.transform = 'translateY(0)';
        });
        
        item.addEventListener('mouseleave', () => {
            dropdown.style.opacity = '0';
            dropdown.style.visibility = 'hidden';
            dropdown.style.transform = 'translateY(-8px)';
        });
    }
});

// ===== Add dynamic styles =====
const dynamicStyles = document.createElement('style');
dynamicStyles.textContent = `
    .nav-link.active {
        color: var(--primary-color);
    }
    
    .nav-link.active::after {
        width: 100%;
    }
    
    .input-focused {
        transform: translateY(-1px);
    }
    
    .nav-menu.active {
        display: flex;
        position: fixed;
        top: 70px;
        left: 0;
        right: 0;
        flex-direction: column;
        background: white;
        padding: 2rem;
        box-shadow: var(--shadow-lg);
        gap: 1rem;
    }
    
    .hamburger.active span:nth-child(1) {
        transform: rotate(45deg) translateY(10px);
    }
    
    .hamburger.active span:nth-child(2) {
        opacity: 0;
    }
    
    .hamburger.active span:nth-child(3) {
        transform: rotate(-45deg) translateY(-10px);
    }
    
    /* Smooth link hover underline */
    .nav-link::after {
        transition: width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    /* Card hover transitions */
    .product-card,
    .feature-card,
    .industry-card {
        transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1),
                    box-shadow 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    /* Smooth button transitions */
    .cta-button,
    .btn-primary,
    .btn-secondary {
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
`;
document.head.appendChild(dynamicStyles);

// ===== Initialize on DOM Load =====
document.addEventListener('DOMContentLoaded', () => {
    // Trigger initial animations for visible elements
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight) {
            el.classList.add('visible');
        }
    });
    
    // Smooth page entrance
    document.body.style.opacity = '1';
    
    // Add smooth hover effects to all links
    document.querySelectorAll('a:not(.btn):not(.cta-button):not(.nav-link)').forEach(link => {
        link.style.transition = 'color 0.3s cubic-bezier(0.16, 1, 0.3, 1)';
    });
    
    // Initialize product image lazy loading with smooth fade
    document.querySelectorAll('.product-image img, .hero-image img').forEach(img => {
        img.loading = 'lazy';
        if (!img.complete) {
            img.style.opacity = '0';
            img.addEventListener('load', () => {
                img.style.transition = 'opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
                img.style.opacity = '1';
            });
        }
    });
});

// ===== Smooth Page Transitions =====
document.querySelectorAll('a[href]:not([href^="#"]):not([href^="javascript"]):not([target="_blank"])').forEach(link => {
    link.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        
        // Skip external links and special protocols
        if (href.startsWith('http') && !href.includes(window.location.hostname)) {
            return;
        }
        
        e.preventDefault();
        
        // Smooth exit animation
        document.body.style.transition = 'opacity 0.25s ease';
        document.body.style.opacity = '0';
        
        setTimeout(() => {
            window.location.href = href;
        }, 250);
    });
});

// ===== Smooth Scroll to Top Button =====
function createScrollToTop() {
    const scrollBtn = document.createElement('button');
    scrollBtn.id = 'scroll-to-top';
    scrollBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M12 19V5M5 12l7-7 7 7"/>
        </svg>
    `;
    scrollBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #2f2e0c;
        color: #d4ff9e;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        visibility: hidden;
        transform: translateY(20px) scale(0.8);
        transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        z-index: 999;
    `;
    
    document.body.appendChild(scrollBtn);
    
    // Show/hide on scroll
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 400) {
            scrollBtn.style.opacity = '1';
            scrollBtn.style.visibility = 'visible';
            scrollBtn.style.transform = 'translateY(0) scale(1)';
        } else {
            scrollBtn.style.opacity = '0';
            scrollBtn.style.visibility = 'hidden';
            scrollBtn.style.transform = 'translateY(20px) scale(0.8)';
        }
    });
    
    // Hover effect
    scrollBtn.addEventListener('mouseenter', () => {
        scrollBtn.style.transform = 'translateY(-5px) scale(1.1)';
        scrollBtn.style.boxShadow = '0 12px 40px rgba(212, 255, 158, 0.3)';
    });
    
    scrollBtn.addEventListener('mouseleave', () => {
        scrollBtn.style.transform = 'translateY(0) scale(1)';
        scrollBtn.style.boxShadow = '0 8px 30px rgba(0, 0, 0, 0.2)';
    });
    
    // Scroll to top on click
    scrollBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

createScrollToTop();

console.log('PackAxis - Smooth Experience Loaded! ✨');
