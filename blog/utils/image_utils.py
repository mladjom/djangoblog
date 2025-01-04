from PIL import Image
from datetime import datetime
import os
import logging
from blog.settings import IMAGE_SETTINGS

logger = logging.getLogger(__name__)

def calculate_height(width, aspect_ratio=None):
    """Calculate height based on width and aspect ratio"""
    if aspect_ratio is None:
        aspect_ratio = IMAGE_SETTINGS['ASPECT_RATIO']
    return int(width * (aspect_ratio[1] / aspect_ratio[0]))

def resize_and_compress_images(image_path, base_path, new_base_filename, sizes=None, quality=None, aspect_ratio=None):
    """Resize and compress an image to multiple sizes while maintaining aspect ratio"""
    sizes = sizes or IMAGE_SETTINGS['SIZES']
    quality = quality or IMAGE_SETTINGS['WEBP_QUALITY']
    aspect_ratio = aspect_ratio or IMAGE_SETTINGS['ASPECT_RATIO']
    
    try:
        logger.info(f"Processing image: {image_path}")
        
        # Use the provided new_base_filename instead of extracting from original
        base_filename = new_base_filename
        
        # Open and convert image if necessary
        with Image.open(image_path) as img:
            logger.debug(f"Original dimensions: {img.size}")
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Process each size
            results = []
            for target_width in sizes:
                # Calculate target height maintaining aspect ratio
                target_height = calculate_height(target_width, aspect_ratio)
                
                # Create a copy of the image for this size
                resized_img = img.copy()
                
                # Resize the image
                resized_img.thumbnail((target_width, target_height), Image.LANCZOS)
                
                # Create new filename with dimensions
                new_filename = f"{base_filename}-{target_width}x{target_height}.webp"
                new_path = os.path.join(base_path, new_filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(new_path), exist_ok=True)
                
                # Save the image
                resized_img.save(new_path, format='WEBP', quality=quality)
                logger.info(f"Saved: {new_path}")
                results.append(new_path)
                
                # Clean up
                resized_img.close()
                
        return results
                
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        return []

def image_upload_path(instance, filename):
    """Generate a dynamic path for uploading images"""
    date_format = datetime.now().strftime('%Y/%m/%d')
    model_name = instance.__class__.__name__.lower()
    path_format = IMAGE_SETTINGS['UPLOAD_PATH_FORMAT'].format(
        model_name=model_name,
        year=datetime.now().strftime('%Y'),
        month=datetime.now().strftime('%m'),
        day=datetime.now().strftime('%d')
    )
    return os.path.join(path_format, filename)

def process_single_image(image_path, output_path, target_width, quality=None, aspect_ratio=None):
    """Process a single image to specific dimensions"""
    quality = quality or IMAGE_SETTINGS['WEBP_QUALITY']
    aspect_ratio = aspect_ratio or IMAGE_SETTINGS['ASPECT_RATIO']
    
    try:
        with Image.open(image_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            target_height = calculate_height(target_width, aspect_ratio)
            img.thumbnail((target_width, target_height), Image.LANCZOS)
            img.save(output_path, format='WEBP', quality=quality)
            return True
    except Exception as e:
        logger.error(f"Error processing image {image_path}: {e}")
        return False
