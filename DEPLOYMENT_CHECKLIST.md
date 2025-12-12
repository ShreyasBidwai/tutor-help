# TuitionTrack - Production Deployment Checklist

Use this checklist to ensure your application is ready for production deployment.

## Pre-Deployment Setup

### 1. Environment Variables ✅
- [ ] Copy `.env.example` to `.env`
- [ ] Generate `SECRET_KEY` using `python3 generate_secret_key.py`
- [ ] Generate VAPID keys using `python3 generate_vapid_keys.py`
- [ ] Get Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Set `FLASK_DEBUG=False` in `.env`
- [ ] Set `SESSION_COOKIE_SECURE=True` (if using HTTPS)
- [ ] Set `VAPID_CLAIM_EMAIL` to your email address

### 2. Dependencies ✅
- [ ] Install all dependencies: `pip install -r requirements.txt`
- [ ] Verify all packages installed successfully
- [ ] Check for any version conflicts

### 3. Database Setup ✅
- [ ] Initialize database: `python3 -c "from database import init_db, migrate_db, add_indexes; migrate_db(); add_indexes()"`
- [ ] Verify database file created (`tutor_app.db`)
- [ ] Test database connection
- [ ] (Optional) Populate with test data: `python3 populate_db.py`

### 4. RAG System Setup ✅
- [ ] Build RAG index: `python3 build_rag_index.py`
- [ ] Verify index files created:
  - [ ] `data/niya_faiss.index`
  - [ ] `data/niya_embeddings.pkl`
  - [ ] `data/niya_vectorizer.pkl`
- [ ] Test Niya help bot functionality

### 5. File Structure ✅
- [ ] Verify `uploads/homework/` directory exists
- [ ] Verify `logs/` directory exists
- [ ] Check all required static files are present
- [ ] Verify all templates are in place

## Security Checklist

### 6. Security Configuration ✅
- [ ] `.env` file is NOT committed to git (check `.gitignore`)
- [ ] `SECRET_KEY` is strong and unique
- [ ] VAPID keys are generated and secure
- [ ] No hardcoded secrets in code
- [ ] HTTPS configured (required for push notifications)
- [ ] Session cookies configured securely

### 7. Code Security ✅
- [ ] SQL injection prevention (parameterized queries)
- [ ] Input validation on all forms
- [ ] File upload validation
- [ ] XSS protection (Flask auto-escapes templates)
- [ ] CSRF protection (session cookies with SameSite)

## Application Testing

### 8. Functional Testing ✅
- [ ] User registration/login works
- [ ] Student management (add, edit, delete)
- [ ] Batch management (create, edit, assign students)
- [ ] Attendance marking (with batch timing validation)
- [ ] Homework sharing (text, files, YouTube links)
- [ ] Attendance reports (batch and student views)
- [ ] Student portal login and features
- [ ] Niya help bot responds correctly
- [ ] Push notifications work (if HTTPS enabled)

### 9. Error Handling ✅
- [ ] 404 error page displays correctly
- [ ] 500 error page displays correctly
- [ ] Health check endpoint (`/health`) returns 200
- [ ] Error logging works

### 10. Performance Testing ✅
- [ ] Application starts without errors
- [ ] Database queries are optimized
- [ ] No memory leaks
- [ ] Response times are acceptable
- [ ] File uploads work correctly

## Deployment Configuration

### 11. Hosting Platform Setup (Render/Heroku/etc.) ✅
- [ ] Environment variables set in platform dashboard:
  - [ ] `SECRET_KEY`
  - [ ] `VAPID_PUBLIC_KEY`
  - [ ] `VAPID_PRIVATE_KEY`
  - [ ] `VAPID_CLAIM_EMAIL`
  - [ ] `GEMINI_API_KEY`
  - [ ] `FLASK_DEBUG=False`
  - [ ] `SESSION_COOKIE_SECURE=True`
- [ ] Build command configured (if needed)
- [ ] Start command configured: `gunicorn -c gunicorn_config.py app:app`
- [ ] Port configuration (usually auto-set by platform)

### 12. Post-Deployment Verification ✅
- [ ] Application accessible via URL
- [ ] Health check endpoint works: `curl https://your-app.com/health`
- [ ] Can register/login
- [ ] All features work correctly
- [ ] Push notifications work (test on mobile)
- [ ] HTTPS certificate valid
- [ ] No console errors in browser

## Monitoring & Maintenance

### 13. Monitoring Setup ✅
- [ ] Logging configured and working
- [ ] Error tracking set up (optional)
- [ ] Uptime monitoring configured (optional)
- [ ] Health check endpoint monitored

### 14. Backup Strategy ✅
- [ ] Database backup plan in place
- [ ] Uploaded files backup plan
- [ ] RAG index backup (optional, can be regenerated)
- [ ] Backup frequency determined
- [ ] Backup restoration tested

## Documentation

### 15. Documentation Complete ✅
- [ ] `README.md` updated
- [ ] `PRODUCTION_SETUP.md` reviewed
- [ ] `.env.example` created and documented
- [ ] Deployment instructions clear

## Final Steps

### 16. Go-Live Preparation ✅
- [ ] All checklist items completed
- [ ] Final testing completed
- [ ] Team notified of deployment
- [ ] Rollback plan prepared (if needed)
- [ ] Support contact information ready

---

## Quick Deployment Commands

```bash
# 1. Generate keys
python3 generate_secret_key.py
python3 generate_vapid_keys.py

# 2. Setup environment
cp .env.example .env
# Edit .env with generated keys

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python3 -c "from database import init_db, migrate_db, add_indexes; migrate_db(); add_indexes()"

# 5. Build RAG index
python3 build_rag_index.py

# 6. Test locally
python3 app.py

# 7. Deploy to production
# (Follow your hosting platform's deployment instructions)
```

## Troubleshooting

If you encounter issues:

1. **Check logs**: `tail -f logs/app.log` or platform logs
2. **Verify environment variables**: Ensure all required vars are set
3. **Test health endpoint**: `curl https://your-app.com/health`
4. **Check database**: Verify database file exists and is accessible
5. **Verify HTTPS**: Push notifications require HTTPS

---

**Status**: ⚠️ Complete all items before going live!

