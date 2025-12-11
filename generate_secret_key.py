#!/usr/bin/env python3
"""Generate a secure SECRET_KEY for Flask sessions"""
import secrets

# Generate a secure random key (32 bytes = 64 hex characters)
secret_key = secrets.token_hex(32)

print("=" * 60)
print("SECRET_KEY Generated Successfully!")
print("=" * 60)
print("\nAdd this to your .env file:")
print(f"\nSECRET_KEY={secret_key}")
print("\n" + "=" * 60)
print("\n⚠️  IMPORTANT: Keep this key secret and never commit it to git!")
print("=" * 60)

