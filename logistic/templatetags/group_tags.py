from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """Return True if the user belongs to the given group name."""
    if not hasattr(user, 'groups'):
        return False
    return user.groups.filter(name=group_name).exists()
