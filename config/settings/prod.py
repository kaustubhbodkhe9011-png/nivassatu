import os
import shutil
from pathlib import Path
from decouple import config
from .base import *

DEBUG = config("DEBUG", default=False, cast=bool)
SECRET_KEY = config("SECRET_KEY", default="django-insecure-prod-key-nivassetu-residences-7412")
ALLOWED_HOSTS = ["*"]

# Vercel serverless flag
IS_VERCEL = os.environ.get("VERCEL") == "1"

# Database configuration
DATABASE_URL = config("DATABASE_URL", default=None)
if DATABASE_URL:
    try:
        import dj_database_url
        DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
    except ImportError:
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": Path("/tmp") / "db.sqlite3" if IS_VERCEL else (BASE_DIR / "db.sqlite3"),
            }
        }
else:
    # On Vercel, the root filesystem is read-only. Only /tmp is writable.
    db_path = Path("/tmp") / "db.sqlite3" if IS_VERCEL else (BASE_DIR / "db.sqlite3")
    
    # If a pre-seeded local db exists, copy it to /tmp so data is preserved
    if IS_VERCEL and (BASE_DIR / "db.sqlite3").exists() and not db_path.exists():
        try:
            shutil.copy2(BASE_DIR / "db.sqlite3", db_path)
        except Exception:
            pass

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db_path,
        }
    }
