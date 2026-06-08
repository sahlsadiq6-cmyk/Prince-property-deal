// Main JavaScript - Prince Property

const API_URL = 'http://localhost:5000/api';

// Theme toggle
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const htmlElement = document.documentElement;
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        htmlElement.style.colorScheme = 'dark';
        if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
            htmlElement.style.colorScheme = isDark ? 'dark' : 'light';
            themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        });
    }
});

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.getElementById('navMenu');

if (hamburger) {
    hamburger.addEventListener('click', function() {
        navMenu.classList.toggle('active');
    });
}

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href !== '#' && document.querySelector(href)) {
            e.preventDefault();
            document.querySelector(href).scrollIntoView({ behavior: 'smooth' });
            if (navMenu) navMenu.classList.remove('active');
        }
    });
});

// Search functionality
function searchProperties() {
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    
    if (query) {
        window.location.href = `pages/properties.html?search=${encodeURIComponent(query)}`;
    }
}

// Load featured properties
async function loadFeaturedProperties() {
    try {
        const response = await fetch(`${API_URL}/properties?per_page=6`);
        const data = await response.json();
        
        const container = document.getElementById('propertiesContainer');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (data.data && data.data.length > 0) {
            data.data.forEach(property => {
                const card = createPropertyCard(property);
                container.appendChild(card);
            });
        } else {
            container.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No properties available</p>';
        }
    } catch (error) {
        console.error('Error loading properties:', error);
    }
}

// Create property card
function createPropertyCard(property) {
    const card = document.createElement('div');
    card.className = 'property-card';
    
    const imageUrl = property.main_image || '/assets/images/property-placeholder.jpg';
    const price = formatPrice(property.price);
    
    card.innerHTML = `
        <div class="property-image">
            <img src="${imageUrl}" alt="${property.title}">
            <span class="property-badge">Featured</span>
        </div>
        <div class="property-content">
            <h3 class="property-title">${escapeHtml(property.title)}</h3>
            <p class="property-location">
                <i class="fas fa-map-marker-alt"></i> ${escapeHtml(property.city)}
            </p>
            <div class="property-details">
                <span class="property-detail">
                    <i class="fas fa-door-open"></i> ${property.bedrooms || 0} Beds
                </span>
                <span class="property-detail">
                    <i class="fas fa-bath"></i> ${property.bathrooms || 0} Baths
                </span>
                <span class="property-detail">
                    <i class="fas fa-ruler"></i> ${property.square_feet || 0} sqft
                </span>
            </div>
            <div class="property-price">$${price}</div>
            <div class="property-footer">
                <div class="property-rating">
                    <i class="fas fa-star"></i>
                    <span>4.8 (${Math.floor(Math.random() * 100)} reviews)</span>
                </div>
                <span class="property-views">
                    <i class="fas fa-eye"></i> ${property.views || 0} views
                </span>
            </div>
        </div>
    `;
    
    card.addEventListener('click', () => {
        window.location.href = `pages/property-detail.html?id=${property.id}`;
    });
    
    return card;
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(price);
}

// Escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Load blog posts
async function loadBlogPosts() {
    const container = document.getElementById('blogContainer');
    if (!container) return;
    
    // Mock blog data
    const blogs = [
        {
            id: 1,
            title: 'Tips for First-Time Home Buyers',
            excerpt: 'Discover essential tips and strategies for purchasing your first home...',
            category: 'Buying Guide',
            author: 'John Smith',
            date: '2024-01-15',
            image: '/assets/images/blog1.jpg'
        },
        {
            id: 2,
            title: 'Real Estate Market Trends 2024',
            excerpt: 'Explore the latest trends shaping the real estate market...',
            category: 'Market News',
            author: 'Sarah Johnson',
            date: '2024-01-10',
            image: '/assets/images/blog2.jpg'
        },
        {
            id: 3,
            title: 'How to Stage Your Home for Sale',
            excerpt: 'Learn professional staging techniques to sell your property faster...',
            category: 'Selling Guide',
            author: 'Mike Brown',
            date: '2024-01-05',
            image: '/assets/images/blog3.jpg'
        }
    ];
    
    container.innerHTML = blogs.map(blog => `
        <div class="blog-card">
            <div class="blog-image">
                <img src="${blog.image}" alt="${blog.title}">
            </div>
            <div class="blog-content">
                <span class="blog-category">${blog.category}</span>
                <h3 class="blog-title">${escapeHtml(blog.title)}</h3>
                <p class="blog-excerpt">${blog.excerpt}</p>
                <div class="blog-meta">
                    <span><i class="fas fa-user"></i> ${blog.author}</span>
                    <span><i class="fas fa-calendar"></i> ${new Date(blog.date).toLocaleDateString()}</span>
                </div>
            </div>
        </div>
    `).join('');
}

// Load FAQ
async function loadFAQ() {
    const container = document.getElementById('faqContainer');
    if (!container) return;
    
    const faqs = [
        {
            id: 1,
            question: 'How do I search for properties?',
            answer: 'Use our search bar to find properties by location, price range, or property type. You can also browse our featured listings or contact our agents for personalized assistance.'
        },
        {
            id: 2,
            question: 'What documents do I need to buy a property?',
            answer: 'You will typically need proof of income, credit history, identification, and pre-approval letter from your lender. Our team can guide you through the process.'
        },
        {
            id: 3,
            question: 'How can I sell my property?',
            answer: 'Contact our sales team to get a free property valuation. We will help you list your property and connect you with potential buyers.'
        },
        {
            id: 4,
            question: 'Are your listings verified?',
            answer: 'Yes, all our listings are verified and updated regularly. We ensure accuracy and transparency in all property information.'
        }
    ];
    
    container.innerHTML = faqs.map(faq => `
        <div class="faq-item" onclick="this.classList.toggle('active')">
            <div class="faq-question">
                <span class="faq-q-text">${faq.question}</span>
                <i class="fas fa-chevron-down faq-icon"></i>
            </div>
            <div class="faq-answer">
                <p>${faq.answer}</p>
            </div>
        </div>
    `).join('');
}

// Contact form submission
document.addEventListener('DOMContentLoaded', function() {
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                name: formData.get('name') || this.querySelector('input[placeholder*="Name"]')?.value,
                email: formData.get('email') || this.querySelector('input[placeholder*="Email"]')?.value,
                subject: formData.get('subject') || this.querySelector('input[placeholder*="Subject"]')?.value,
                message: formData.get('message') || this.querySelector('textarea')?.value
            };
            
            try {
                const response = await fetch(`${API_URL}/contact`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Message sent successfully! We will contact you soon.');
                    this.reset();
                } else {
                    alert('Error sending message. Please try again.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error sending message.');
            }
        });
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadFeaturedProperties();
    loadBlogPosts();
    loadFAQ();
});
