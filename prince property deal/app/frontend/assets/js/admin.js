// Admin Panel JavaScript

const API_URL = 'http://localhost:5000/api';

// Check authentication
if (!localStorage.getItem('access_token')) {
    window.location.href = 'login.html';
}

// Theme toggle
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
    });
}

// Sidebar toggle
const sidebarToggle = document.querySelector('.sidebar-toggle');
const sidebar = document.querySelector('.admin-sidebar');
if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });
}

// Navigation items
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        const section = this.getAttribute('data-section');
        switchSection(section);
        
        // Mobile: close sidebar
        if (window.innerWidth <= 768) {
            sidebar.classList.remove('active');
        }
    });
});

// Switch sections
function switchSection(section) {
    // Hide all sections
    document.querySelectorAll('.admin-section').forEach(el => {
        el.classList.remove('active');
    });
    
    // Remove active class from nav
    document.querySelectorAll('.nav-item').forEach(el => {
        el.classList.remove('active');
    });
    
    // Show selected section
    const selectedSection = document.getElementById(`${section}-section`);
    if (selectedSection) {
        selectedSection.classList.add('active');
    }
    
    // Add active class to nav item
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
}

// Load dashboard statistics
async function loadDashboardStats() {
    try {
        const response = await apiCall('/admin/dashboard');
        if (!response) return;
        
        const data = await response.json();
        
        if (data.statistics) {
            document.getElementById('totalUsers').textContent = data.statistics.total_users;
            document.getElementById('totalProperties').textContent = data.statistics.total_properties;
            document.getElementById('totalContacts').textContent = data.statistics.total_contacts;
            document.getElementById('pendingInquiries').textContent = data.statistics.pending_inquiries;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load users
async function loadUsers() {
    try {
        const response = await apiCall('/admin/users');
        if (!response) return;
        
        const data = await response.json();
        const tableBody = document.getElementById('usersTableBody');
        
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        if (data.data && data.data.length > 0) {
            data.data.forEach(user => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.username}</td>
                    <td>${user.email}</td>
                    <td><span class="badge">${user.role}</span></td>
                    <td>${user.is_active ? 'Active' : 'Inactive'}</td>
                    <td>${new Date(user.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn-sm" onclick="editUser(${user.id})">Edit</button>
                        <button class="btn-sm danger" onclick="deactivateUser(${user.id})">Deactivate</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

// Load properties
async function loadAdminProperties() {
    try {
        const response = await apiCall('/admin/properties');
        if (!response) return;
        
        const data = await response.json();
        const tableBody = document.getElementById('propertiesTableBody');
        
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        if (data.data && data.data.length > 0) {
            data.data.forEach(prop => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${prop.id}</td>
                    <td>${prop.title}</td>
                    <td>${prop.owner}</td>
                    <td>$${formatPrice(prop.price)}</td>
                    <td><span class="badge">${prop.status}</span></td>
                    <td>${prop.views}</td>
                    <td>
                        <button class="btn-sm" onclick="viewProperty(${prop.id})">View</button>
                        <button class="btn-sm" onclick="featureProperty(${prop.id})">Feature</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading properties:', error);
    }
}

// Load contacts
async function loadContacts() {
    try {
        const response = await apiCall('/admin/contacts');
        if (!response) return;
        
        const data = await response.json();
        const tableBody = document.getElementById('contactsTableBody');
        
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        if (data.data && data.data.length > 0) {
            data.data.forEach(contact => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${contact.id}</td>
                    <td>${contact.name}</td>
                    <td>${contact.email}</td>
                    <td>${contact.subject}</td>
                    <td>${contact.is_replied ? 'Replied' : 'Pending'}</td>
                    <td>${new Date(contact.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn-sm" onclick="replyContact(${contact.id})">Reply</button>
                        <button class="btn-sm" onclick="viewContact(${contact.id})">View</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading contacts:', error);
    }
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Format price
function formatPrice(price) {
    return new Intl.NumberFormat('en-US').format(price);
}

// API helper with auth
async function apiCall(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers
    });
    
    // Handle token expiration
    if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = 'login.html';
        return null;
    }
    
    return response;
}

// Mock functions
function editUser(id) { alert(`Edit user ${id}`); }
function deactivateUser(id) { alert(`Deactivate user ${id}`); }
function viewProperty(id) { alert(`View property ${id}`); }
function featureProperty(id) { alert(`Feature property ${id}`); }
function replyContact(id) { alert(`Reply to contact ${id}`); }
function viewContact(id) { alert(`View contact ${id}`); }

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    loadUsers();
    loadAdminProperties();
    loadContacts();
    switchSection('dashboard');
});
