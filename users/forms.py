from django import forms
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from projects.models import Project

from .models import JobTitle, Profile


ACCESS_GROUPS = ('Level 1', 'Level 2', 'Level 3', 'Level 4')


class JobTitleForm(forms.ModelForm):
    class Meta:
        model = JobTitle
        fields = ['name', 'permission_group']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                    'placeholder': 'e.g. Group Managing Director',
                }
            ),
            'permission_group': forms.Select(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permission_group'].queryset = Group.objects.filter(name__in=ACCESS_GROUPS).order_by('name')


class BaseUserForm(forms.ModelForm):
    job_title = forms.ModelChoiceField(
        queryset=JobTitle.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
            }
        ),
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                'placeholder': '0801 234 5678',
            }
        ),
    )
    last_active_project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        required=False,
        widget=forms.Select(
            attrs={
                'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
            }
        ),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                    'placeholder': 'Enter username',
                }
            ),
            'first_name': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                    'placeholder': 'First name',
                }
            ),
            'last_name': forms.TextInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                    'placeholder': 'Last name',
                }
            ),
            'email': forms.EmailInput(
                attrs={
                    'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                    'placeholder': 'name@company.com',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['job_title'].queryset = JobTitle.objects.select_related('permission_group').all()
        self.fields['last_active_project'].queryset = Project.objects.all()

        profile = getattr(self.instance, 'profile', None)
        if profile:
            self.fields['job_title'].initial = profile.job_title
            self.fields['phone_number'].initial = profile.phone_number
            self.fields['last_active_project'].initial = profile.last_active_project


class UserCreateForm(BaseUserForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                'placeholder': 'Create a password',
            }
        ),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                'placeholder': 'Confirm password',
            }
        ),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserUpdateForm(BaseUserForm):
    new_password = forms.CharField(
        label='New Password',
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                'placeholder': 'Leave blank to keep current password',
            }
        ),
        help_text='Leave empty if you do not wish to change the user password.'
    )
    confirm_new_password = forms.CharField(
        label='Confirm New Password',
        required=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'w-full rounded-xl border border-gray-300 bg-white px-4 py-3 text-base text-gray-900 shadow-sm focus:border-[#bfa12c] focus:ring-4 focus:ring-[#bfa12c]/15 outline-none',
                'placeholder': 'Confirm new password',
            }
        ),
    )

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm = self.cleaned_data.get('confirm_new_password')
        if new_password and not confirm:
            raise forms.ValidationError('Please confirm the new password.')
        if new_password and confirm and new_password != confirm:
            raise forms.ValidationError('Passwords do not match.')
        return confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
