# Tutor Help - Deployment Guide

## Production Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
# IMPORTANT: Change SECRET_KEY to a secure random string
```

Generate a secure SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Initialize Database

```bash
python3 -c "from database import init_db, add_indexes; init_db(); add_indexes()"
```

### 4. Start Application

**Option A: Using startup script (Recommended)**
```bash
chmod +x start.sh
./start.sh
```

**Option B: Using Gunicorn directly**
```bash
gunicorn -c gunicorn_config.py app:app
```

**Option C: Using systemd (Linux)**
```bash
# Edit tutor-help.service and update paths
sudo cp tutor-help.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tutor-help
sudo systemctl start tutor-help

# Check status
sudo systemctl status tutor-help

# View logs
sudo journalctl -u tutor-help -f
```

### 5. Verify

Check if application is running:
```bash
curl http://localhost:5000
```

## Performance Tuning

### Worker Count
Adjust in `gunicorn_config.py`:
```python
workers = multiprocessing.cpu_count() * 2 + 1
```

For low-resource servers, use:
```python
workers = 2  # Minimum 2 workers
```

### Database Optimization
Indexes are automatically added on startup. To verify:
```bash
sqlite3 tutor_app.db ".indexes"
```

## Monitoring

### Logs
- Access logs: stdout (redirect to file if needed)
- Error logs: stderr (redirect to file if needed)
- Application logs: Configure in app.py

### Health Check
```bash
curl http://localhost:5000/
```

### Check Database Size
```bash
ls -lh tutor_app.db
```

## Troubleshooting

### Database locked errors
- Reduce concurrent writes
- Consider PostgreSQL for high concurrency (1000+ tutors)
- Add connection pooling

### High memory usage
- Reduce worker count in gunicorn_config.py
- Add pagination to queries
- Monitor with: `ps aux | grep gunicorn`

### Slow queries
- Check if indexes are created: `sqlite3 tutor_app.db ".indexes"`
- Analyze query performance
- Consider database migration to PostgreSQL

### Port already in use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

## Production Checklist

- [ ] SECRET_KEY changed from default
- [ ] FLASK_DEBUG set to False
- [ ] Database indexes created
- [ ] Gunicorn configured with appropriate workers
- [ ] Logs configured and monitored
- [ ] Backup strategy in place
- [ ] SSL/TLS configured (if using HTTPS)
- [ ] Firewall rules configured
- [ ] Monitoring set up

## Backup

### Database Backup
```bash
# Manual backup
cp tutor_app.db tutor_app.db.backup

# Automated backup (add to cron)
0 2 * * * cp /path/to/tutor_app.db /path/to/backups/tutor_app_$(date +\%Y\%m\%d).db
```

### Full Backup
```bash
tar -czf tutor-help-backup-$(date +%Y%m%d).tar.gz \
    tutor_app.db \
    uploads/ \
    .env
```

## Scaling

### Current Capacity (SQLite)
- **Recommended**: 500-1,000 tutors
- **Maximum**: 2,000 tutors (with optimizations)
- **Concurrent Users**: 50-100

### When to Migrate to PostgreSQL
- Database size > 5 GB
- > 1,000 active tutors
- > 50 concurrent writes
- Query times > 500ms

## Security

### Environment Variables
- Never commit `.env` file
- Use strong SECRET_KEY
- Restrict file permissions: `chmod 600 .env`

### File Permissions
```bash
chmod 600 .env
chmod 755 start.sh
chmod 644 gunicorn_config.py
```

### Firewall
```bash
# Allow only necessary ports
ufw allow 5000/tcp
ufw enable
```

## Updates

### Updating Application
```bash
# Stop application
pkill gunicorn

# Pull latest code
git pull

# Install new dependencies
pip install -r requirements.txt

# Run migrations
python3 -c "from database import migrate_db, add_indexes; migrate_db(); add_indexes()"

# Restart application
./start.sh
```

