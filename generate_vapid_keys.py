#!/usr/bin/env python3
"""Generate VAPID keys for push notifications"""
try:
    from pywebpush import WebPusher
    import json
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.backends import default_backend
    import base64
except ImportError:
    print("Error: Required packages not installed.")
    print("Install with: pip install pywebpush cryptography")
    exit(1)

# Generate VAPID keys using cryptography
private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
public_key = private_key.public_key()

# Get the public key in uncompressed format (0x04 + X + Y)
public_numbers = public_key.public_numbers()
x = public_numbers.x
y = public_numbers.y

# Convert to bytes (65 bytes: 0x04 + 32-byte X + 32-byte Y)
public_key_bytes = b'\x04' + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')

# Get private key bytes (32 bytes)
private_key_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')

# Encode in base64 URL-safe format (no padding)
public_key_b64 = base64.urlsafe_b64encode(public_key_bytes).decode('utf-8').rstrip('=')
private_key_b64 = base64.urlsafe_b64encode(private_key_bytes).decode('utf-8').rstrip('=')

print("=" * 60)
print("VAPID Keys Generated Successfully!")
print("=" * 60)
print("\nAdd these to your .env file or set as environment variables:")
print("\nVAPID_PUBLIC_KEY=" + public_key_b64)
print("VAPID_PRIVATE_KEY=" + private_key_b64)
print("VAPID_CLAIM_EMAIL=your-email@example.com")
print("\n" + "=" * 60)
print("\nFor testing, you can also add them directly to config.py")
print("=" * 60)

