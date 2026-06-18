def projects_context(request):
    from projects.models import Project
    return {
        'all_projects': Project.objects.all()
    }


def users_context(request):
    management_levels = ('Level 1', 'Level 3', 'Level 4')
    user = getattr(request, 'user', None)
    can_manage_users = False
    if user and user.is_authenticated:
        can_manage_users = user.is_superuser or user.is_staff or user.groups.filter(name__in=management_levels).exists()
    return {
        'can_manage_users': can_manage_users,
    }
