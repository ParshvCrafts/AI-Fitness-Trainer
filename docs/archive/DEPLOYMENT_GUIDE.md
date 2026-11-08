# AI Fitness Trainer - Complete Deployment Guide

This guide covers multiple deployment options for the AI Fitness Trainer application.

## Table of Contents
1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Production Best Practices](#production-best-practices)

---

## Local Development

### Windows

1. **Run the batch file**:
```cmd
run.bat
```

Or manually:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Linux/Mac

1. **Make script executable**:
```bash
chmod +x run.sh
./run.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

2. **Access**: Navigate to `http://localhost:5000`

---

## Docker Deployment

### Simple Docker Run

```bash
# Build the image
docker build -t ai-fitness-trainer .

# Run the container
docker run -p 5000:5000 ai-fitness-trainer
```

### Docker Compose (Recommended)

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

---

## Cloud Deployment

### Heroku

1. **Install Heroku CLI**:
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Login to Heroku**:
```bash
heroku login
```

3. **Create application**:
```bash
heroku create your-app-name
```

4. **Set environment variables**:
```bash
heroku config:set SECRET_KEY=your-secure-random-key
heroku config:set FLASK_ENV=production
```

5. **Deploy**:
```bash
git push heroku main
```

6. **Open application**:
```bash
heroku open
```

### AWS Elastic Beanstalk

1. **Install EB CLI**:
```bash
pip install awsebcli
```

2. **Initialize EB**:
```bash
eb init -p docker ai-fitness-trainer
```

3. **Create environment**:
```bash
eb create ai-fitness-env
```

4. **Deploy**:
```bash
eb deploy
```

5. **Open application**:
```bash
eb open
```

### Google Cloud Platform (Cloud Run)

1. **Install gcloud CLI**

2. **Build and push image**:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/ai-trainer
```

3. **Deploy to Cloud Run**:
```bash
gcloud run deploy ai-trainer \
  --image gcr.io/PROJECT-ID/ai-trainer \
  --platform managed \
  --port 5000 \
  --allow-unauthenticated
```

### Azure App Service

1. **Install Azure CLI**

2. **Login**:
```bash
az login
```

3. **Create resource group**:
```bash
az group create --name ai-trainer-rg --location eastus
```

4. **Create App Service plan**:
```bash
az appservice plan create \
  --name ai-trainer-plan \
  --resource-group ai-trainer-rg \
  --is-linux \
  --sku B1
```

5. **Create web app**:
```bash
az webapp create \
  --resource-group ai-trainer-rg \
  --plan ai-trainer-plan \
  --name your-app-name \
  --deployment-container-image-name ai-fitness-trainer
```

### DigitalOcean App Platform

1. **Push code to GitHub**

2. **Create new app** on DigitalOcean

3. **Select Dockerfile deployment**

4. **Configure**:
   - Environment: Production
   - HTTP Port: 5000
   - Health Check Path: /

5. **Deploy**

---

## Production Best Practices

### 1. Security

#### Change Secret Key
```bash
# Generate a secure secret key
python -c 'import secrets; print(secrets.token_hex(32))'
```

Update in `docker-compose.yml` or environment variables:
```yaml
environment:
  - SECRET_KEY=your-generated-key-here
```

#### Enable HTTPS
Camera access requires HTTPS in production. Use:
- Let's Encrypt (free SSL)
- Cloudflare (free SSL + CDN)
- Your cloud provider's SSL service

#### Configure CORS
In production, restrict CORS to your domain:
```python
# app.py
socketio = SocketIO(app, cors_allowed_origins="https://yourdomain.com")
```

### 2. Performance Optimization

#### Use Production Server
Instead of Flask's development server, use Gunicorn:

```dockerfile
# Add to Dockerfile
RUN pip install gunicorn

# Change CMD to:
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "app:app"]
```

Update `requirements.txt`:
```txt
gunicorn==21.2.0
eventlet==0.33.3
```

#### Nginx Reverse Proxy
Create `nginx.conf`:
```nginx
upstream app {
    server localhost:5000;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /socket.io {
        proxy_pass http://app/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Monitoring

#### Application Logs
```bash
# Docker logs
docker-compose logs -f

# Save logs to file
docker-compose logs > app.log
```

#### Health Checks
The application includes a health check endpoint.

Test it:
```bash
curl http://localhost:5000/
```

### 4. Scaling

#### Horizontal Scaling
For high traffic, use multiple instances with load balancer:

```yaml
# docker-compose.yml for scaling
version: '3.8'
services:
  ai-trainer:
    build: .
    ports:
      - "5000-5002:5000"
    deploy:
      replicas: 3
```

Run:
```bash
docker-compose up --scale ai-trainer=3
```

#### Vertical Scaling
Increase resources in cloud provider or Docker:

```yaml
services:
  ai-trainer:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### 5. Environment Variables

Always use environment variables for sensitive data:

1. Copy example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your values

3. Load in application or Docker Compose

### 6. Database (Optional)

For storing user data, add database:

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_trainer
      POSTGRES_USER: trainer
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 7. CDN Integration

For faster static file delivery:
1. Upload static files to CDN (Cloudflare, AWS CloudFront)
2. Update static file URLs in templates
3. Configure cache headers

### 8. Backup Strategy

```bash
# Backup Docker volumes
docker run --rm -v web_app_logs:/data -v $(pwd):/backup ubuntu tar czf /backup/logs-backup.tar.gz /data

# Restore
docker run --rm -v web_app_logs:/data -v $(pwd):/backup ubuntu tar xzf /backup/logs-backup.tar.gz -C /
```

---

## Troubleshooting

### Issue: Camera not accessible
**Solution**: Ensure HTTPS is enabled in production

### Issue: High CPU usage
**Solution**: Reduce frame processing rate in `script.js`

### Issue: WebSocket disconnections
**Solution**: Increase timeout values in nginx/load balancer

### Issue: Memory leaks
**Solution**: Restart containers periodically or implement connection cleanup

---

## Monitoring Tools

Recommended tools for production monitoring:
- **Application**: Sentry, New Relic, Datadog
- **Infrastructure**: Prometheus + Grafana
- **Logs**: ELK Stack, Splunk
- **Uptime**: UptimeRobot, Pingdom

---

## Cost Optimization

### Free Tier Options
- **Heroku**: Free dyno (sleeps after 30 min)
- **GCP Cloud Run**: Free quota (2 million requests/month)
- **AWS Free Tier**: 12 months free
- **DigitalOcean**: $200 credit for 60 days

### Cost Reduction Tips
1. Use auto-scaling to reduce idle resources
2. Implement CDN for static content
3. Optimize image quality/compression
4. Use spot/preemptible instances
5. Set up budget alerts

---

## Support & Maintenance

### Regular Updates
```bash
# Update dependencies
pip list --outdated
pip install --upgrade package-name

# Update Docker base image
docker pull python:3.10-slim
docker-compose build --no-cache
```

### Security Patches
- Subscribe to security advisories for Flask, OpenCV, MediaPipe
- Run security audits: `pip-audit`
- Keep Docker images updated

---

## Checklist Before Going Live

- [ ] Change SECRET_KEY to secure random value
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS for your domain only
- [ ] Set up monitoring and logging
- [ ] Configure backups
- [ ] Test on multiple devices/browsers
- [ ] Set up error tracking (Sentry)
- [ ] Configure rate limiting
- [ ] Add analytics (optional)
- [ ] Create privacy policy/terms
- [ ] Set up domain name
- [ ] Configure CDN
- [ ] Load testing
- [ ] Documentation for users

---

**Congratulations!** Your AI Fitness Trainer is ready for the world!
