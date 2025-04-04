# activity/forms.py

from django import forms
from .models import Activity, ActivityUpdate, CustomUser


class ActivityForm(forms.ModelForm):
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(role='team_member'),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Activity
        fields = ['title', 'description', 'node_name', 'activity_type', 'status', 'start_date', 'end_date', 'assigned_users']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class ActivityUpdateForm(forms.ModelForm):
    class Meta:
        model = ActivityUpdate
        fields = ['update_text']
        widgets = {
            'update_text': forms.Textarea(attrs={'rows': 3}),
        }
