import os
from pathlib import Path
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent  # Adjusted for nested structure


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'blog/templates'),
        ],
        'APP_DIRS': True,
        # ...existing code...
    },
]
# ...existing code...
