#!/usr/bin/env python3
"""Generate VAPID keys for push notifications"""
from py_vapid import Vapid01
import base64

# Generate VAPID keys
vapid = Vapid01()
keys = vapid.generate_keys()

# Convert to base64 URL-safe format (for web push)
public_key_bytes = keys.public_key.public_bytes_raw()
private_key_bytes = keys.private_key.private_bytes_raw()

public_key = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
private_key = base64.urlsafe_b64encode(private_key_bytes).decode('utf-8').rstrip('=')

print("=" * 60)
print("VAPID Keys Generated Successfully!")
print("=" * 60)
print("\nAdd these to your .env file or set as environment variables:")
print("\nVAPID_PUBLIC_KEY=" + public_key)
print("VAPID_PRIVATE_KEY=" + private_key)
print("VAPID_CLAIM_EMAIL=your-email@example.com")
print("\n" + "=" * 60)
print("\nFor testing, you can also add them directly to config.py")
print("=" * 60)

