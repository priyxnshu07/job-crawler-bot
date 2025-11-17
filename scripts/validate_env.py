#!/usr/bin/env python3
"""
Environment variable validation script.
Validates that all required environment variables are set.
"""
import os
import sys


REQUIRED_ENV_VARS = {
    'SECRET_KEY': 'Flask secret key for session management',
    'DATABASE_URL': 'PostgreSQL database connection URL',
    'REDIS_URL': 'Redis connection URL',
}

OPTIONAL_ENV_VARS = {
    'EMAIL_USER': 'Email address for sending alerts',
    'EMAIL_PASSWORD': 'Email app password',
    'FLASK_ENV': 'Flask environment (development/production)',
    'PORT': 'Port number for the application',
}


def validate_env():
    """Validate environment variables."""
    missing_vars = []
    warnings = []
    
    print("🔍 Validating environment variables...\n")
    
    # Check required variables
    for var, description in REQUIRED_ENV_VARS.items():
        value = os.environ.get(var)
        if not value:
            missing_vars.append((var, description))
            print(f"❌ {var}: MISSING - {description}")
        else:
            # Mask sensitive values
            if 'PASSWORD' in var or 'SECRET' in var or 'KEY' in var:
                display_value = '*' * len(value)
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
    
    # Check optional variables
    print("\n📋 Optional variables:")
    for var, description in OPTIONAL_ENV_VARS.items():
        value = os.environ.get(var)
        if not value:
            warnings.append((var, description))
            print(f"⚠️  {var}: NOT SET - {description}")
        else:
            if 'PASSWORD' in var:
                display_value = '*' * len(value)
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
    
    # Summary
    print("\n" + "=" * 60)
    if missing_vars:
        print("❌ Validation FAILED")
        print(f"\nMissing required variables: {len(missing_vars)}")
        for var, description in missing_vars:
            print(f"  - {var}: {description}")
        print("\nPlease set these variables before running the application.")
        return False
    else:
        print("✅ Validation PASSED")
        if warnings:
            print(f"\n⚠️  Warnings: {len(warnings)} optional variables not set")
            print("The application may work with limited functionality.")
        return True


def check_database_connection():
    """Check database connection."""
    try:
        from config import DATABASE_CONFIG
        import psycopg2
        
        print("\n🔌 Testing database connection...")
        conn = psycopg2.connect(**DATABASE_CONFIG)
        conn.close()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def check_redis_connection():
    """Check Redis connection."""
    try:
        import redis
        from config import DATABASE_CONFIG
        
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        print("\n🔌 Testing Redis connection...")
        r = redis.from_url(redis_url)
        r.ping()
        print("✅ Redis connection successful")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("Environment Variable Validation")
    print("=" * 60)
    
    # Validate environment variables
    env_valid = validate_env()
    
    # Test connections if env is valid
    if env_valid:
        db_valid = check_database_connection()
        redis_valid = check_redis_connection()
        
        if db_valid and redis_valid:
            print("\n" + "=" * 60)
            print("✅ All checks passed! Application is ready to run.")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("⚠️  Some connection checks failed. Please verify your configuration.")
            print("=" * 60)
            sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("❌ Environment validation failed. Please fix the issues above.")
        print("=" * 60)
        sys.exit(1)

