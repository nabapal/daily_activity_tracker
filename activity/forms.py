from django import forms
from django.contrib.auth import get_user_model
from .models import Activity, ActivityUpdate

User = get_user_model()


class ActivityForm(forms.ModelForm):
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='MEMBER'),  # Match your role choices
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Assign to Team Members"
    )

    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'node_name',
            'activity_type', 'status', 'start_date',
            'end_date', 'assigned_users'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            raise forms.ValidationError("End date must be after start date")

        return cleaned_data


class ActivityUpdateForm(forms.ModelForm):
    class Meta:
        model = ActivityUpdate
        fields = ['description', 'progress']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Enter your activity update...'
            }),
            'progress': forms.NumberInput(attrs={
                'min': 0,
                'max': 100,
                'class': 'progress-input'
            })
        }
        labels = {
            'description': 'Update Details',
            'progress': 'Progress (%)'
        }

    def clean_progress(self):
        progress = self.cleaned_data['progress']
        if progress < 0 or progress > 100:
            raise forms.ValidationError("Progress must be between 0 and 100")
        return progress