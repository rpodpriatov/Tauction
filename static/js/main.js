document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const body = document.body;
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
            updateDarkModeIcon();
        });
        // Check for saved dark mode preference
        if (localStorage.getItem('darkMode') === 'true') {
            body.classList.add('dark-mode');
        }
        updateDarkModeIcon();
    }

    function updateDarkModeIcon() {
        const icon = darkModeToggle.querySelector('i');
        if (body.classList.contains('dark-mode')) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList.add('fa-moon');
        }
    }

    // Search functionality
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchTerm = searchInput.value.trim();
            if (searchTerm) {
                window.location.href = `/search?q=${encodeURIComponent(searchTerm)}`;
            }
        });
    }

    // Add fade-in effect to cards
    function fadeInCards() {
        const cards = document.querySelectorAll('.card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in');
            }, index * 100);
        });
    }
    fadeInCards();

    // Update countdown timers
    function updateCountdowns() {
        document.querySelectorAll('.countdown').forEach(function(element) {
            const endTime = new Date(element.dataset.endTime).getTime();
            const now = new Date().getTime();
            const timeLeft = endTime - now;
            if (timeLeft > 0) {
                const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
                const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);
                element.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            } else {
                element.textContent = "Auction ended";
                element.closest('.card').classList.add('auction-ended');
            }
        });
    }
    updateCountdowns();
    setInterval(updateCountdowns, 1000);

    // Masonry layout initialization
    const grid = document.querySelector('.auction-grid');
    if (grid) {
        new Masonry(grid, {
            itemSelector: '.auction-item',
            columnWidth: '.auction-item',
            percentPosition: true
        });
    }

    // Navbar scrolling effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }
    });

    // Hero section animation
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.classList.add('animate__animated', 'animate__fadeIn');
    }

    // Custom form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Update minimum bid amount
    function updateMinBidAmount() {
        const currentPriceElements = document.querySelectorAll('.current-price');
        const minBidAmountElements = document.querySelectorAll('.min-bid-amount');
        
        currentPriceElements.forEach((element, index) => {
            const currentPrice = parseFloat(element.textContent);
            if (minBidAmountElements[index]) {
                minBidAmountElements[index].textContent = (currentPrice + 0.1).toFixed(1);
            }
        });
    }

    // Call updateMinBidAmount initially and set interval
    updateMinBidAmount();
    setInterval(updateMinBidAmount, 5000);
});
