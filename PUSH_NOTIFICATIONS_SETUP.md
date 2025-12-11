# Push Notifications Setup Guide

## ✅ Implementation Complete!

Push notifications have been successfully implemented in TuitionTrack. Here's what was done and what you need to know.

## What Was Implemented

### 1. **VAPID Keys Generated**
- VAPID keys have been generated and added to `config.py`
- Keys are also available as environment variables

### 2. **Push Subscription Management**
- API endpoints: `/api/push/subscribe` and `/api/push/unsubscribe`
- Subscriptions are stored in the `push_subscriptions` table
- Auto-subscription on page load (if permission granted)

### 3. **Push Notification Sending**
- **Attendance Marked**: Students receive push notification when attendance is marked
- **New Homework**: Students receive push notification when homework is assigned
- Utility functions in `utils/push_notifications.py`

### 4. **Frontend Integration**
- Push subscription JavaScript in `static/js/push-notifications.js`
- Auto-subscription on login
- Service worker handles push events

## How It Works

### For Students:
1. Student logs in → Auto-subscribes to push notifications (if permission granted)
2. Tutor marks attendance → Student receives push notification
3. Tutor creates homework → Student receives push notification

### For Tutors:
- Push notifications can be added for batch reminders (future enhancement)

## Environment Variables (Optional)

You can set these in your `.env` file or environment:

```bash
VAPID_PUBLIC_KEY=your_public_key_here
VAPID_PRIVATE_KEY=your_private_key_here
VAPID_CLAIM_EMAIL=your-email@example.com
```

**Note**: Default keys are already in `config.py` for testing. For production, generate new keys using:

```bash
python3 generate_vapid_keys.py
```

## Testing Push Notifications

### 1. **Test Subscription**
- Login as a student
- Check browser console for subscription messages
- Verify subscription in database: `SELECT * FROM push_subscriptions;`

### 2. **Test Attendance Notification**
- Login as tutor
- Mark attendance for a student
- Student should receive push notification (even if app is closed)

### 3. **Test Homework Notification**
- Login as tutor
- Create homework for a batch
- Students in that batch should receive push notification

## Important Notes

### HTTPS Required
- Push notifications **require HTTPS** in production
- For local testing, use `localhost` (HTTPS not required for localhost)

### Browser Support
- ✅ Chrome/Edge (Android & Desktop)
- ✅ Firefox (Android & Desktop)
- ✅ Safari (iOS 16.4+)
- ❌ Safari (iOS < 16.4) - Limited support

### APK Compatibility
- ✅ Works in APK (TWA/Trusted Web Activity)
- ✅ Works when app is closed
- ⚠️ May require disabling battery optimization on some devices

## Troubleshooting

### Notifications Not Working?

1. **Check Permission**: Browser must have notification permission granted
2. **Check Subscription**: Verify subscription exists in database
3. **Check HTTPS**: Must be HTTPS (or localhost) in production
4. **Check Service Worker**: Service worker must be registered
5. **Check Console**: Look for errors in browser console

### Common Issues

**"Push notifications not supported"**
- Browser doesn't support Push API
- Try Chrome or Firefox

**"Notification permission denied"**
- User denied permission
- Clear browser data and try again

**"Subscription failed"**
- Check VAPID keys are correct
- Verify server is accessible

## Next Steps (Optional Enhancements)

1. **Notification Settings Page**: Let users enable/disable specific notification types
2. **Batch Reminders**: Push notifications for tutors before batch starts
3. **Homework Due Reminders**: Push notifications 1 day before due date
4. **Notification History**: Show notification history in app

## Files Modified

- `config.py` - Added VAPID configuration
- `blueprints/auth.py` - Added subscription API endpoints
- `blueprints/attendance.py` - Added push notification on attendance mark
- `blueprints/homework.py` - Added push notification on homework creation
- `utils/push_notifications.py` - New utility module
- `static/js/push-notifications.js` - New frontend subscription code
- `templates/base.html` - Added push notification script
- `requirements.txt` - Added pywebpush and py-vapid
- `database.py` - push_subscriptions table already exists

## Support

If you encounter any issues:
1. Check browser console for errors
2. Verify VAPID keys are correct
3. Ensure HTTPS is enabled (for production)
4. Check service worker registration

