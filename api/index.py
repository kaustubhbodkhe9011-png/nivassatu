import os
import sys
from pathlib import Path

# Add project root and apps directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "apps"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

import django
django.setup()

from django.core.management import call_command
from django.db import connection

# Automatically migrate and seed database on Vercel if not already initialized
try:
    tables = connection.introspection.table_names()
    if "society_society" not in tables:
        call_command("migrate", interactive=False)
        call_command("seed_demo")
except Exception as e:
    print("Vercel initialization notice:", e)

from django.core.wsgi import get_wsgi_application

# Vercel looks for 'app' or 'application'
app = get_wsgi_application()
