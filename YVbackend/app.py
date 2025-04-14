from chalice import Chalice
from chalice_wsgi import ChaliceWSGIHandler

import os
import sys

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

# Add Django project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Setup Django
import django
django.setup()

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application
django_app = get_wsgi_application()

# Wrap it for Chalice
app = Chalice(app_name="django_lambda")
wsgi_app = ChaliceWSGIHandler(django_app)

@app.route("/{proxy+}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], content_types=["*/*"])
def index():
    return wsgi_app(app.current_request)
