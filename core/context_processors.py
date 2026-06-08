def projects_context(request):
    from core.models import Project
    return {
        'all_projects': Project.objects.all()
    }
