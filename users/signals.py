from django.contrib.auth.models import Group, User
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import Profile


ACCESS_GROUPS = ('Level 1', 'Level 2', 'Level 3', 'Level 4')


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)


@receiver(post_migrate)
def ensure_access_groups(sender, **kwargs):
    if sender and sender.name != 'users':
        return
    for name in ACCESS_GROUPS:
        Group.objects.get_or_create(name=name)
