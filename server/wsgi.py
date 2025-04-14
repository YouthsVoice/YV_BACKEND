import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

django_asgi_app = get_asgi_application()