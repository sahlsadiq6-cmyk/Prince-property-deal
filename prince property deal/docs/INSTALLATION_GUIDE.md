# Prince Property - Complete Installation & Deployment Guide

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Guide](#installation-guide)
3. [Configuration](#configuration)
4. [Database Setup](#database-setup)
5. [Running the Application](#running-the-application)
6. [Deployment Guide](#deployment-guide)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Backend
- Python 3.8 or higher
- MySQL 5.7 or higher
- Redis (optional, for caching)
- pip (Python package manager)

### Frontend
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No build process required (vanilla HTML/CSS/JS)

### Server
- Linux (Ubuntu 20.04+ recommended)
- 2GB RAM minimum
- 10GB disk space minimum
- Nginx or Apache web server

---

## Installation Guide

### 1. Clone or Extract Project

```bash
cd /path/to/prince\ property\ deal
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd app/backend
pip install -r requirements.txt
```

#### Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

Then install requirements:
```bash
pip install -r requirements.txt
```

### 3. Frontend Setup

No special setup required! Frontend files are plain HTML/CSS/JavaScript.

---

## Configuration

### 1. Environment Variables

Create `.env` file in `app/backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_APP=app.py

# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/prince_property

# JWT
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@princeproperties.com

# Application
APP_URL=http://localhost:5000
APP_NAME=Prince Property
```

### 2. Gmail Configuration for Email

1. Go to [Google Account](https://myaccount.google.com/)
2. Enable 2-Factor Authentication
3. Generate [App Password](https://myaccount.google.com/apppasswords)
4. Use the app password in `.env` file

---

## Database Setup

### 1. Create Database

```bash
# Access MySQL
mysql -u root -p

# In MySQL console
CREATE DATABASE prince_property;
USE prince_property;
```

### 2. Run Schema

```bash
# In MySQL console
source /path/to/database/schema.sql;
```

Or from terminal:

```bash
mysql -u root -p prince_property < database/schema.sql
```

### 3. Verify Tables

```bash
mysql -u root -p prince_property -e "SHOW TABLES;"
```

---

## Running the Application

### 1. Backend Development Server

```bash
cd app/backend
python app.py
```

Server will run at: `http://localhost:5000`

### 2. Frontend Local Server

Use Python's built-in server:

```bash
cd app/frontend
python -m http.server 8000
```

Or use LiveServer extension in VS Code.

Access at: `http://localhost:8000`

### 3. Test API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# API info
curl http://localhost:5000/api/info
```

---

## Deployment Guide

### 1. Production Environment Setup

#### Install Production Dependencies

```bash
# Install Gunicorn for production WSGI server
pip install gunicorn

# Install Nginx
sudo apt-get install nginx

# Install MySQL Server
sudo apt-get install mysql-server
```

#### Create Production Directory

```bash
sudo mkdir -p /var/www/prince-property
sudo chown $USER:$USER /var/www/prince-property
```

### 2. Deploy Backend

#### Copy Files

```bash
cp -r app/backend /var/www/prince-property/
cp -r app/frontend /var/www/prince-property/
```

#### Update Environment

```bash
cd /var/www/prince-property/backend
cp .env.example .env
# Edit .env with production values
nano .env
```

Change to production:
```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/prince_property
```

#### Run with Gunicorn

```bash
cd /var/www/prince-property/backend
gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
```

### 3. Nginx Configuration

Create `/etc/nginx/sites-available/prince-property`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend
    location / {
        root /var/www/prince-property/frontend;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Uploads
    location /uploads/ {
        alias /var/www/prince-property/backend/uploads/;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/prince-property /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. SSL Certificate (Let's Encrypt)

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 5. Systemd Service for Backend

Create `/etc/systemd/system/prince-property.service`:

```ini
[Unit]
Description=Prince Property Flask Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/prince-property/backend
Environment="PATH=/var/www/prince-property/backend/venv/bin"
ExecStart=/var/www/prince-property/backend/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable prince-property
sudo systemctl start prince-property
sudo systemctl status prince-property
```

### 6. Database Backup Script

Create backup script `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backup/mysql"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

mysqldump -u root -p --all-databases > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
```

### 7. Monitoring

Install PM2 for process management:

```bash
npm install -g pm2
pm2 start wsgi.py --name "prince-property"
pm2 startup
pm2 save
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

**Error**: `pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")`

**Solution**:
- Check MySQL is running: `sudo systemctl status mysql`
- Verify credentials in `.env`
- Ensure MySQL user has permissions: `GRANT ALL ON prince_property.* TO 'user'@'localhost';`

#### 2. Import Error: No module named 'flask'

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate
# Reinstall requirements
pip install -r requirements.txt
```

#### 3. CORS Errors

**Solution**:
Update `CORS_ORIGINS` in `config/config.py`:
```python
CORS_ORIGINS = ["http://localhost:3000", "https://yourdomain.com"]
```

#### 4. Email Not Sending

**Solution**:
- Check Gmail app password is correct
- Enable "Less secure app access" if needed
- Check spam folder
- Verify MAIL_USERNAME matches Gmail account

#### 5. Static Files Not Loading

**Solution**:
```nginx
location /assets/ {
    alias /var/www/prince-property/frontend/assets/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### Performance Optimization

#### 1. Enable Caching

Update `config.py`:
```python
REDIS_URL = 'redis://localhost:6379/0'
```

#### 2. Database Optimization

Create indexes (already in schema.sql)

#### 3. Gzip Compression

Add to Nginx:
```nginx
gzip on;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss;
```

#### 4. CDN Configuration

Use CDN for static assets:
```html
<link rel="stylesheet" href="https://cdn.example.com/css/style.css">
```

---

## Security Checklist

- [ ] Change all default passwords
- [ ] Enable HTTPS/SSL
- [ ] Set secure JWT secrets
- [ ] Enable CSRF protection
- [ ] Enable SQL injection prevention
- [ ] Enable XSS protection
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Regular backups
- [ ] Keep dependencies updated
- [ ] Monitor logs
- [ ] Enable Two-Factor Authentication for admin

---

## Maintenance

### Regular Tasks

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check logs
tail -f /var/log/nginx/error.log

# Database maintenance
mysqlcheck -u root -p --all-databases

# Disk space check
df -h
```

---

## Support

For issues or questions, contact: support@princeproperties.com
