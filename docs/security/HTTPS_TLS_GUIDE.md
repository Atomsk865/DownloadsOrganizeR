# HTTPS/TLS Configuration Guide

## Overview

The SortNStore Dashboard should **always** run behind HTTPS in production to protect authentication credentials and session cookies. This guide covers multiple deployment scenarios.

---

## Quick Start: Self-Signed Certificate (Testing Only)

### Generate Self-Signed Certificate

```bash
# Create certificate directory
mkdir -p /etc/ssl/sortnstore
cd /etc/ssl/sortnstore

# Generate private key and certificate (valid 365 days)
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout key.pem \
    -out cert.pem \
    -days 365 \
    -subj "/CN=dashboard.local"

# Set restrictive permissions
chmod 600 key.pem
chmod 644 cert.pem
```

### Run Flask with HTTPS (Development)

```python
# In SortNStoreDashboard.py or wrapper script
if __name__ == "__main__":
    import ssl
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('/etc/ssl/sortnstore/cert.pem', 
                           '/etc/ssl/sortnstore/key.pem')
    
    app.run(host='0.0.0.0', port=5000, ssl_context=context)
```

**⚠️ Warning:** Self-signed certificates trigger browser warnings. Use only for testing.

---

## Production: Reverse Proxy with Let's Encrypt

### Option 1: Nginx Reverse Proxy (Recommended)

#### 1. Install Nginx and Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# RHEL/CentOS
sudo yum install nginx certbot python3-certbot-nginx
```

#### 2. Configure Nginx

**File:** `/etc/nginx/sites-available/sortnstore`

```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name dashboard.example.com;
    
    # Certbot challenge location
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name dashboard.example.com;
    
    # SSL Configuration (Certbot will fill these in)
    ssl_certificate /etc/letsencrypt/live/dashboard.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard.example.com/privkey.pem;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    
    # HSTS (already set by Flask app, but good to have here too)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Rate limiting (backup layer)
    limit_req_zone $binary_remote_addr zone=dashboard_ratelimit:10m rate=5r/s;
    limit_req zone=dashboard_ratelimit burst=10 nodelay;
    
    # Proxy to Flask app
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (for SSE streams)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Security headers (Flask already sets these, but belt-and-suspenders)
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Logging
    access_log /var/log/nginx/sortnstore_access.log;
    error_log /var/log/nginx/sortnstore_error.log;
}
```

#### 3. Enable Site and Obtain Certificate

```bash
# Create symlink to enable site
sudo ln -s /etc/nginx/sites-available/sortnstore /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

# Obtain Let's Encrypt certificate
sudo certbot --nginx -d dashboard.example.com

# Certbot will:
# 1. Verify domain ownership via HTTP challenge
# 2. Obtain certificate from Let's Encrypt
# 3. Update Nginx config with SSL paths
# 4. Set up automatic renewal (via systemd timer or cron)
```

#### 4. Verify Auto-Renewal

```bash
# Test renewal process (dry run)
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

---

### Option 2: Apache Reverse Proxy

#### 1. Install Apache and Certbot

```bash
# Ubuntu/Debian
sudo apt install apache2 certbot python3-certbot-apache

# Enable required modules
sudo a2enmod proxy proxy_http ssl headers rewrite
```

#### 2. Configure Apache

**File:** `/etc/apache2/sites-available/sortnstore-ssl.conf`

```apache
<VirtualHost *:80>
    ServerName dashboard.example.com
    
    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>

<VirtualHost *:443>
    ServerName dashboard.example.com
    
    # SSL Configuration (Certbot fills these)
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/dashboard.example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/dashboard.example.com/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf
    
    # Security Headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Frame-Options "DENY"
    Header always set X-Content-Type-Options "nosniff"
    
    # Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    # Logging
    ErrorLog ${APACHE_LOG_DIR}/sortnstore_error.log
    CustomLog ${APACHE_LOG_DIR}/sortnstore_access.log combined
</VirtualHost>
```

#### 3. Enable and Obtain Certificate

```bash
# Enable site
sudo a2ensite sortnstore-ssl

# Test configuration
sudo apache2ctl configtest

# Reload Apache
sudo systemctl reload apache2

# Obtain certificate
sudo certbot --apache -d dashboard.example.com
```

---

## Windows IIS with Let's Encrypt

### Using win-acme (Automated)

#### 1. Download win-acme

Download from: https://github.com/win-acme/win-acme/releases

```powershell
# Extract to C:\win-acme
cd C:\win-acme
```

#### 2. Install Certificate

```powershell
# Run as Administrator
.\wacs.exe

# Follow prompts:
# - Choose "Create new certificate (full options)"
# - Select "Single binding of IIS site"
# - Choose your dashboard site
# - Select validation method (HTTP-01 recommended)
# - Accept default certificate storage
```

#### 3. Configure IIS Reverse Proxy

**Prerequisites:**
```powershell
# Install URL Rewrite and ARR modules
# Download from IIS Downloads page
```

**web.config (in dashboard root):**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <rewrite>
            <rules>
                <rule name="ReverseProxyInboundRule" stopProcessing="true">
                    <match url="(.*)" />
                    <action type="Rewrite" url="http://localhost:5000/{R:1}" />
                    <serverVariables>
                        <set name="HTTP_X_FORWARDED_PROTO" value="https" />
                    </serverVariables>
                </rule>
            </rules>
        </rewrite>
    </system.webServer>
</configuration>
```

---

## Docker with Traefik (Automated HTTPS)

### docker-compose.yml

```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    command:
      - "--api.insecure=false"
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@example.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
    networks:
      - web
  
  dashboard:
    build: .
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashboard.rule=Host(`dashboard.example.com`)"
      - "traefik.http.routers.dashboard.entrypoints=websecure"
      - "traefik.http.routers.dashboard.tls.certresolver=letsencrypt"
      - "traefik.http.services.dashboard.loadbalancer.server.port=5000"
      # Redirect HTTP to HTTPS
      - "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https"
      - "traefik.http.routers.dashboard-http.rule=Host(`dashboard.example.com`)"
      - "traefik.http.routers.dashboard-http.entrypoints=web"
      - "traefik.http.routers.dashboard-http.middlewares=redirect-to-https"
    networks:
      - web

networks:
  web:
    external: false
```

---

## Testing TLS Configuration

### Check Certificate

```bash
# Test SSL handshake
openssl s_client -connect dashboard.example.com:443 -servername dashboard.example.com

# Check certificate expiry
echo | openssl s_client -connect dashboard.example.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Online Tools

- **SSL Labs Test:** https://www.ssllabs.com/ssltest/
  - Comprehensive SSL/TLS analysis
  - Target: A+ rating

- **Security Headers:** https://securityheaders.com/
  - Check HTTP security headers
  - Verify CSP, HSTS, X-Frame-Options

---

## Troubleshooting

### Issue: "Too Many Redirects"

**Cause:** Flask thinks it's running over HTTP when behind HTTPS proxy.

**Solution:** Ensure proxy sets `X-Forwarded-Proto: https` header.

```nginx
# Nginx
proxy_set_header X-Forwarded-Proto $scheme;
```

```apache
# Apache
RequestHeader set X-Forwarded-Proto "https"
```

### Issue: Session Cookies Not Working

**Cause:** Flask's `SESSION_COOKIE_SECURE` flag requires HTTPS.

**Solution:** Set environment variable:
```bash
export FLASK_ENV=production
```

Or in config:
```python
app.config['SESSION_COOKIE_SECURE'] = True
```

### Issue: WebSocket/SSE Streams Not Working

**Cause:** Proxy not configured for long-lived connections.

**Solution (Nginx):**
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
proxy_read_timeout 86400;  # 24 hours
```

---

## Security Best Practices

### TLS Configuration Checklist

- [ ] **Disable SSLv3, TLS 1.0, TLS 1.1** - Use TLS 1.2+ only
- [ ] **Strong cipher suites** - Prefer ECDHE, disable RC4/MD5
- [ ] **HTTP Strict Transport Security (HSTS)** - `max-age=31536000`
- [ ] **Certificate chain complete** - Include intermediate certificates
- [ ] **Automatic renewal** - Certbot timer or cron job active
- [ ] **Monitor expiry** - Alert 30 days before expiration
- [ ] **Redirect HTTP to HTTPS** - No cleartext access
- [ ] **Secure cookie flags** - `Secure`, `HttpOnly`, `SameSite=Lax`

### Monitoring Certificate Expiry

**Cron job example:**
```bash
# /etc/cron.daily/check-cert-expiry
#!/bin/bash
DOMAIN="dashboard.example.com"
DAYS_LEFT=$(echo | openssl s_client -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -checkend $((30*86400)) && echo "OK" || echo "EXPIRING")

if [ "$DAYS_LEFT" != "OK" ]; then
    echo "WARNING: SSL certificate for $DOMAIN expires in <30 days" | mail -s "SSL Certificate Expiry Alert" admin@example.com
fi
```

---

## Production Deployment Checklist

- [ ] Valid SSL certificate installed (Let's Encrypt or commercial CA)
- [ ] HTTP to HTTPS redirect configured
- [ ] TLS 1.2+ enforced, weak ciphers disabled
- [ ] HSTS header enabled with appropriate max-age
- [ ] Certificate auto-renewal tested and scheduled
- [ ] Reverse proxy rate limiting configured
- [ ] Security headers validated (SSLLabs, SecurityHeaders.com)
- [ ] Firewall rules restrict dashboard port to proxy only
- [ ] Monitoring alerts for certificate expiry
- [ ] Backup of private keys stored securely offline

---

**Last Updated:** December 10, 2025  
**Recommended Configuration:** Nginx + Let's Encrypt  
**Minimum TLS Version:** 1.2
