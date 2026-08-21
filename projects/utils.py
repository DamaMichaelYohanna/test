from .models import ProjectActivityLog

def log_project_activity(project, user, action_type, title, description="", changes_json=None):
    """
    Helper utility to record a project change notification / activity log entry.
    """
    if changes_json is None:
        changes_json = {}

    return ProjectActivityLog.objects.create(
        project=project,
        user=user if (user and user.is_authenticated) else None,
        action_type=action_type,
        title=title,
        description=description,
        changes_json=changes_json
    )
