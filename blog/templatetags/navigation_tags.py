from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def is_active(context, url_name, section=None, css_class='active'):
    """
    Template tag to check if current page matches a given URL name or section.
    
    Usage:
    {% is_active 'home' %}  # Checks URL name
    {% is_active 'blog' 'blog' %}  # Checks both URL name and section
    {% is_active 'products' css_class='current' %}  # Custom CSS class
    """
    request = context.get('request')
    if not request:
        return ''
        
    current_url = request.path
    if not current_url:
        return ''
    
    # Try to get the current URL name
    try:
        current_url_name = request.resolver_match.url_name
    except AttributeError:
        current_url_name = None
    
    # Get current section (first part of the path)
    current_section = current_url.split('/')[1] if current_url else ''
    
    # Try to reverse the URL name to get the path
    try:
        url_path = reverse(url_name)
    except NoReverseMatch:
        return ''
    
    is_active = False
    
    # Check URL name match
    if current_url_name and current_url_name == url_name:
        is_active = True
    
    # Check section match if provided
    if section and current_section == section:
        is_active = True
    
    # Check if current URL starts with the target URL (for nested paths)
    if url_path and url_path != '/' and current_url.startswith(url_path):
        is_active = True
    
    return css_class if is_active else ''

