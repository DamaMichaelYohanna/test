def projects_context(request):
    from projects.models import Project
    return {
        'all_projects': Project.objects.all()
    }
