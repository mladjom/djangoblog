from PIL import Image
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

def calculate_height(width, aspect_ratio=(16, 10)):
    """Calculate height based on width and aspect ratio"""
    return int(width * (aspect_ratio[1] / aspect_ratio[0]))

def resize_and_compress_images(image_path, base_path, new_base_filename, sizes=None, quality=85, aspect_ratio=(16, 10)):
    """
    Resize and compress an image to multiple sizes while maintaining aspect ratio
    
    Args:
        image_path: Original image path
        base_path: Base path for saving resized images
        new_base_filename: New base filename (typically slugified site title)
        sizes: List of widths to resize to
        quality: WebP compression quality (1-100)
        aspect_ratio: Tuple of (width, height) ratio
    """
    if sizes is None:
        sizes = [576, 768, 992, 1200, 1400]  # Default breakpoint widths
    
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
    """
    Generate a dynamic path for uploading images based on the model name and current date.
    """
    today = datetime.now().strftime('%Y/%m/%d')
    model_name = instance.__class__.__name__.lower()
    base_path = f'{model_name}s/{today}'
    return os.path.join(base_path, filename)

def process_single_image(image_path, output_path, target_width, quality=85, aspect_ratio=(16, 10)):
    """Process a single image to specific dimensions"""
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