from django import template
import math
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta
register = template.Library()

@register.filter
def reading_time(content):
    """
    Returns the estimated reading time for the given content.
    """
    word_count = len(content.split())
    minutes = math.ceil(word_count / 200)  # Average reading speed
    return f"{minutes} {_('min read')}"

@register.filter
def relative_date(value):
    """
    Returns a humanized string representing time difference between now and the input date.
    
    Usage: {{ post.created_at|relative_date }}
    """
    if not isinstance(value, datetime):
        return value
        
    now = timezone.now()
    
    # Convert to timezone-aware if needed
    if timezone.is_naive(value):
        value = timezone.make_aware(value, tz.utc)
    
    diff = now - value
    
    if diff < timedelta(minutes=1):
        return _('just now')
    elif diff < timedelta(hours=1):
        minutes = int(diff.total_seconds() / 60)
        return _('%(minutes)d minute ago', '%(minutes)d minutes ago', minutes) % {'minutes': minutes}
    elif diff < timedelta(days=1):
        hours = int(diff.total_seconds() / 3600)
        return _('%(hours)d hour ago', '%(hours)d hours ago', hours) % {'hours': hours}
    elif diff < timedelta(days=30):
        days = diff.days
        return _('%(days)d day ago', '%(days)d days ago', days) % {'days': days}
    elif diff < timedelta(days=365):
        months = int(diff.days / 30)
        return _('%(months)d month ago', '%(months)d months ago', months) % {'months': months}
    else:
        years = int(diff.days / 365)
        return _('%(years)d year ago', '%(years)d years ago', years) % {'years': years}

# @register.filter
# def relative_date(value):
#     """
#     Returns a human-readable relative date, e.g., "2 days ago" or "Just now".
#     """
#     if not value:
#         return ''
    
#     delta = now() - value

#     if delta < timedelta(minutes=1):
#         return 'Just now'
#     elif delta < timedelta(hours=1):
#         minutes = delta.seconds // 60
#         return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
#     elif delta < timedelta(days=1):
#         hours = delta.seconds // 3600
#         return f'{hours} hour{"s" if hours > 1 else ""} ago'
#     elif delta < timedelta(days=30):
#         days = delta.days
#         return f'{days} day{"s" if days > 1 else ""} ago'
#     else:
#         return value.strftime('%B %d, %Y')  # Fallback to exact date