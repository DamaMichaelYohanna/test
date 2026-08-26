from django import template

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    """Return True if the user belongs to the given group name."""
    if not hasattr(user, 'groups'):
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter(name='short_mda')
def short_mda(val):
    """Return the short acronym of an MDA if in parentheses, else return val."""
    if not val:
        return ""
    val_str = str(val).strip()
    if '(' in val_str and ')' in val_str:
        short = val_str.split('(')[-1].split(')')[0].strip()
        if short:
            return short
    return val_str

