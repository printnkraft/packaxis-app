#!/usr/bin/env python
"""
Generate a secure SECRET_KEY for Django production deployment
Run this and copy the output to Railway environment variables
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    secret_key = get_random_secret_key()
    print("\n" + "="*70)
    print("🔐 NEW SECRET KEY FOR PRODUCTION")
    print("="*70)
    print(f"\n{secret_key}\n")
    print("="*70)
    print("\n📋 Copy this key and add to Railway:")
    print("   1. Go to Railway Dashboard → Your Project")
    print("   2. Click 'Variables' tab")
    print("   3. Add new variable: SECRET_KEY")
    print(f"   4. Paste: {secret_key}")
    print("\n⚠️  IMPORTANT: Never commit this key to git!")
    print("="*70 + "\n")
