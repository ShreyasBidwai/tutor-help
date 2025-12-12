# Production Setup Guide - TuitionTrack

This guide will help you set up TuitionTrack for production deployment.

## Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Generate Keys

### Generate SECRET_KEY

```bash
python3 generate_secret_key.py
```

Copy the generated `SECRET_KEY` value.

### Generate VAPID Keys (for Push Notifications)

```bash
python3 generate_vapid_keys.py
```

Copy the generated `VAPID_PUBLIC_KEY` and `VAPID_PRIVATE_KEY` values.

## Step 3: Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your generated keys:
```bash
nano .env  # or use your preferred editor
```

3. Update the following values:
   - `SECRET_KEY` - Paste the key from `generate_secret_key.py`
   - `VAPID_PUBLIC_KEY` - Paste from `generate_vapid_keys.py`
   - `VAPID_PRIVATE_KEY` - Paste from `generate_vapid_keys.py`
   - `VAPID_CLAIM_EMAIL` - Your email address
   - `FLASK_DEBUG=False` - Ensure this is False for production
   - `SESSION_COOKIE_SECURE=True` - Set to True if using HTTPS

## Step 4: Initialize Database

```bash
python3 -c "from database import init_db, migrate_db, add_indexes; migrate_db(); add_indexes()"
```

## Step 5: Start the Application

### Option A: Using startup script (Recommended)

```bash
chmod +x start.sh
./start.sh
```

### Option B: Using Gunicorn directly

```bash
gunicorn -c gunicorn_config.py app:app
```

### Option C: Using systemd (Linux)

```bash
# Edit tutor-help.service and update paths
sudo cp tutor-help.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tutor-help
sudo systemctl start tutor-help

# Check status
sudo systemctl status tutor-help
```

## Step 6: Verify Installation

1. Check health endpoint:
```bash
curl http://localhost:5000/health
```

2. Open in browser:
```
http://your-server-ip:5000
```

## Production Checklist

- [ ] SECRET_KEY generated and set in `.env`
- [ ] VAPID keys generated and set in `.env`
- [ ] FLASK_DEBUG set to False
- [ ] SESSION_COOKIE_SECURE set to True (if using HTTPS)
- [ ] Database initialized and indexes created
- [ ] Application starts without errors
- [ ] Health check endpoint returns 200
- [ ] HTTPS configured (recommended)
- [ ] Firewall rules configured
- [ ] Backup strategy in place

## Security Notes

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use HTTPS in production** - Required for PWA features and secure cookies
3. **Keep keys secret** - Never share or expose your SECRET_KEY or VAPID keys
4. **Regular backups** - Set up automated database backups

## Troubleshooting

### Database locked errors
- Reduce concurrent writes
- Check if WAL mode is enabled
- Consider PostgreSQL for high concurrency

### Port already in use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
```

### Push notifications not working
- Verify VAPID keys are correctly set
- Ensure HTTPS is enabled (required for push notifications)
- Check browser console for errors

## APK Generation

The app is configured for fullscreen mode in the manifest, which means:
- No browser header will appear in the APK
- App will look like a native Android app
- Display mode is set to "fullscreen" in `manifest.json`

To generate APK, use Bubblewrap or similar PWA-to-APK tools.

## Support

For issues or questions, check the logs:
```bash
# View application logs
tail -f logs/app.log

# View system logs (if using systemd)
sudo journalctl -u tutor-help -f
```

