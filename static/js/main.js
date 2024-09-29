// Enable Bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Lazy loading for images
document.addEventListener("DOMContentLoaded", function() {
    var lazyImages = [].slice.call(document.querySelectorAll("img.lazy"));

    if ("IntersectionObserver" in window) {
        let lazyImageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    let lazyImage = entry.target;
                    lazyImage.src = lazyImage.dataset.src;
                    lazyImage.classList.remove("lazy");
                    lazyImageObserver.unobserve(lazyImage);
                }
            });
        });

        lazyImages.forEach(function(lazyImage) {
            lazyImageObserver.observe(lazyImage);
        });
    }
});

// Add fade-in effect to cards
function fadeInCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
}

// Call fadeInCards when the page loads
window.addEventListener('load', fadeInCards);

// Implement infinite scrolling for auction listings
let page = 1;
const auctionList = document.querySelector('.masonry-grid');
const loadMoreButton = document.getElementById('load-more');

if (loadMoreButton) {
    loadMoreButton.addEventListener('click', loadMoreAuctions);
}

function loadMoreAuctions() {
    page++;
    fetch(`/api/auctions?page=${page}`)
        .then(response => response.json())
        .then(data => {
            if (data.auctions.length > 0) {
                data.auctions.forEach(auction => {
                    const auctionCard = createAuctionCard(auction);
                    auctionList.appendChild(auctionCard);
                });
                new Masonry(auctionList, {
                    itemSelector: '.col',
                    columnWidth: '.col',
                    percentPosition: true
                });
                fadeInCards();
            } else {
                loadMoreButton.style.display = 'none';
            }
        })
        .catch(error => console.error('Error:', error));
}

function createAuctionCard(auction) {
    const col = document.createElement('div');
    col.className = 'col';
    const card = document.createElement('div');
    card.className = 'card h-100';
    card.innerHTML = `
        <div class="card-body">
            <h5 class="card-title">${auction.title}</h5>
            <p class="card-text">${auction.description}</p>
            <p class="card-text"><strong>Current Price:</strong> ${auction.current_price} XTR</p>
            <p class="card-text"><strong>Ends at:</strong> ${new Date(auction.end_time).toLocaleString()}</p>
        </div>
        <div class="card-footer bg-transparent border-top-0">
            <a href="/auction/${auction.id}" class="btn btn-primary btn-block">View Details</a>
        </div>
    `;
    col.appendChild(card);
    return col;
}

// Add to watchlist functionality
const watchlistButtons = document.querySelectorAll('.watchlist-btn');
watchlistButtons.forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const auctionId = this.dataset.auctionId;
        const action = this.dataset.action;
        
        fetch(`/api/${action}_watchlist/${auctionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrf_token')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.innerHTML = action === 'add' ? '<i class="fas fa-star"></i> Remove from Watchlist' : '<i class="far fa-star"></i> Add to Watchlist';
                this.dataset.action = action === 'add' ? 'remove' : 'add';
                showNotification(data.message, 'success');
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('An error occurred. Please try again.', 'error');
        });
    });
});

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    document.querySelector('main').insertAdjacentElement('afterbegin', notification);
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Add animations to elements when they come into view
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.animate-on-scroll');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
            }
        });
    });

    elements.forEach((element) => {
        observer.observe(element);
    });
};

document.addEventListener('DOMContentLoaded', animateOnScroll);

// Implement dark mode toggle
const darkModeToggle = document.getElementById('dark-mode-toggle');
const darkModeToggleMobile = document.getElementById('dark-mode-toggle-mobile');

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('dark-mode', document.body.classList.contains('dark-mode'));
}

if (darkModeToggle) {
    darkModeToggle.addEventListener('click', toggleDarkMode);
}

if (darkModeToggleMobile) {
    darkModeToggleMobile.addEventListener('click', toggleDarkMode);
}

// Check for saved dark mode preference
if (localStorage.getItem('dark-mode') === 'true') {
    document.body.classList.add('dark-mode');
}

// Implement responsive navigation menu
const navbarToggler = document.querySelector('.navbar-toggler');
const navbarCollapse = document.querySelector('.navbar-collapse');

if (navbarToggler && navbarCollapse) {
    navbarToggler.addEventListener('click', () => {
        navbarCollapse.classList.toggle('show');
    });
}

// Implement search functionality
const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const searchFormMobile = document.getElementById('search-form-mobile');
const searchInputMobile = document.getElementById('search-input-mobile');

function handleSearch(e) {
    e.preventDefault();
    const searchTerm = this.querySelector('input[type="search"]').value.trim();
    if (searchTerm) {
        window.location.href = `/search?q=${encodeURIComponent(searchTerm)}`;
    }
}

if (searchForm && searchInput) {
    searchForm.addEventListener('submit', handleSearch);
}

if (searchFormMobile && searchInputMobile) {
    searchFormMobile.addEventListener('submit', handleSearch);
}

// Initialize Masonry layout
document.addEventListener('DOMContentLoaded', function() {
    const grid = document.querySelector('.masonry-grid');
    if (grid) {
        new Masonry(grid, {
            itemSelector: '.col',
            columnWidth: '.col',
            percentPosition: true
        });
    }
});
