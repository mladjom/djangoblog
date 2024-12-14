# utils/image_utils.py
from datetime import datetime
from PIL import Image
from django.conf import settings

def resize_and_compress_image(image_path, new_image_path, max_size=(800, 800), quality=85):
    #print(f"Image path: {image_path}")
    #print(f"New image path: {new_image_path}")
    try:
        print(f"Processing image: {image_path}")  # Debug print

        # Open the image file from the path
        with Image.open(image_path) as img:
            # Debug original dimensions
            print(f"Original dimensions: {img.size}")

            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize the image while maintaining the aspect ratio
            img.thumbnail(max_size, Image.LANCZOS)

            # Debug resized dimensions
            print(f"Resized dimensions: {img.size}")

            # Save as WebP format with the specified quality
            img.save(new_image_path, format='WEBP', quality=quality)
            print(f"Image saved successfully: {new_image_path}")

    except Exception as e:
        print(f"Error processing image {image_path}: {e}")


def image_upload_path(instance, filename):
    """
    Generate a dynamic path for uploading images based on the model name and current date.
    """
    today = datetime.now().strftime('%Y/%m/%d')
    model_name = instance.__class__.__name__.lower()  # Use the model name dynamically
    return f'{model_name}s/{today}/{filename}'