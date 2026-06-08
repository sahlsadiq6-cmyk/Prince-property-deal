// Dashboard JavaScript

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
const sidebar = document.querySelector('.dashboard-sidebar');
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
    document.querySelectorAll('.content-section').forEach(el => {
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

// Load user profile
async function loadUserProfile() {
    try {
        const response = await apiCall('/users/profile');
        if (!response) return;
        
        const data = await response.json();
        
        if (data.data) {
            const user = data.data;
            document.querySelector('.user-name').textContent = `${user.first_name} ${user.last_name}`;
            
            // Update profile form if on profile page
            const firstNameInput = document.getElementById('firstName');
            if (firstNameInput) {
                firstNameInput.value = user.first_name || '';
                document.getElementById('lastName').value = user.last_name || '';
                document.getElementById('email').value = user.email || '';
                document.getElementById('phone').value = user.phone || '';
                document.getElementById('bio').value = user.bio || '';
            }
        }
    } catch (error) {
        console.error('Error loading profile:', error);
    }
}

// Load user properties
async function loadUserProperties() {
    try {
        const response = await apiCall('/users/properties');
        if (!response) return;
        
        const data = await response.json();
        const tableBody = document.getElementById('propertiesTableBody');
        
        if (!tableBody) return;
        
        tableBody.innerHTML = '';
        
        if (data.data && data.data.length > 0) {
            data.data.forEach(prop => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${prop.title}</td>
                    <td>$${formatPrice(prop.price)}</td>
                    <td><span class="status-badge">${prop.status}</span></td>
                    <td>${prop.views}</td>
                    <td>5</td>
                    <td>
                        <button class="btn-sm" onclick="editProperty(${prop.id})">Edit</button>
                        <button class="btn-sm danger" onclick="deleteProperty(${prop.id})">Delete</button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        } else {
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align:center;">No properties yet</td></tr>';
        }
    } catch (error) {
        console.error('Error loading properties:', error);
    }
}

// Update profile
document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const data = {
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                phone: document.getElementById('phone').value,
                bio: document.getElementById('bio').value
            };
            
            try {
                const response = await apiCall('/users/profile', {
                    method: 'PUT',
                    body: JSON.stringify(data)
                });
                
                if (response && response.ok) {
                    alert('Profile updated successfully');
                } else {
                    alert('Error updating profile');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error updating profile');
            }
        });
    }
});

// Change password
function changePassword() {
    const newPassword = prompt('Enter new password:');
    if (newPassword) {
        const currentPassword = prompt('Enter current password:');
        if (currentPassword) {
            // Call API to change password
            alert('Password changed (mock)');
        }
    }
}

// Delete account
function deleteAccount() {
    if (confirm('Are you sure you want to delete your account? This cannot be undone.')) {
        if (confirm('This action is permanent. Confirm again?')) {
            alert('Account deleted (mock)');
            logout();
        }
    }
}

// Logout
function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/';
}

// Redirect helper
function redirectTo(page) {
    window.location.href = page;
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

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadUserProfile();
    loadUserProperties();
    switchSection('dashboard');
});
