# blog/settings.py
from django.conf import settings

# Image Processing Settings
IMAGE_SETTINGS = {
    # Default image sizes for responsive images
    'SIZES': [576, 768, 992, 1200],
    
    # Image quality settings
    'WEBP_QUALITY': 85,
    
    # Default aspect ratio (16:10)
    'ASPECT_RATIO': (16, 9),
    
    # Upload path settings
    'UPLOAD_PATH_FORMAT': '{model_name}s/{year}/{month}/{day}',

    # Category-specific settings
    'TAXONOMY': {
        'WIDTH': 768,
        'ASPECT_RATIO': (16, 10)
    }
}

# Optional: Override settings from Django main settings
try:
    from django.conf import settings
    
    # Update with any user-defined settings
    if hasattr(settings, 'BLOG_IMAGE_SETTINGS'):
        IMAGE_SETTINGS.update(settings.BLOG_IMAGE_SETTINGS)
except ImportError:
    pass