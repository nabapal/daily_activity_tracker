# activity/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
import csv

from .models import Activity, ActivityUpdate, CustomUser


# Role-based access decorator
def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "Access Denied!")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


@login_required
def user_dashboard(request):
    """ Dashboard for team members to view & update activities """
    activities = Activity.objects.filter(assigned_users=request.user)
    return render(request, 'dashboard.html', {'activities': activities})


@login_required
@role_required(['team_lead', 'super_admin'])
def team_lead_dashboard(request):
    """ Dashboard for Team Leads to manage & assign activities """
    activities = Activity.objects.all()
    users = CustomUser.objects.filter(role="team_member")
    return render(request, 'lead_dashboard.html', {'activities': activities, 'users': users})


@login_required
@role_required(['super_admin'])
def super_admin_dashboard(request):
    """ Dashboard for Super Admin to view all activities & generate reports """
    activities = Activity.objects.all()
    return render(request, 'admin_dashboard.html', {'activities': activities})


@login_required
def activity_detail(request, activity_id):
    """ Activity detail view with historical updates """
    activity = get_object_or_404(Activity, id=activity_id)
    updates = ActivityUpdate.objects.filter(activity=activity).order_by('-update_date')

    if request.method == "POST":
        update_text = request.POST.get("update_text")
        if update_text:
            ActivityUpdate.objects.create(activity=activity, updated_by=request.user, update_text=update_text)
            messages.success(request, "Update added successfully.")
            return redirect('activity_detail', activity_id=activity.id)

    return render(request, 'activity_detail.html', {'activity': activity, 'updates': updates})


@login_required
@role_required(['team_lead', 'super_admin'])
def assign_activity(request):
    """ Assign an activity to multiple team members """
    if request.method == "POST":
        activity_id = request.POST.get("activity_id")
        user_ids = request.POST.getlist("assigned_users")

        activity = get_object_or_404(Activity, id=activity_id)
        users = CustomUser.objects.filter(id__in=user_ids)
        activity.assigned_users.set(users)

        messages.success(request, "Activity assigned successfully.")
        return redirect('team_lead_dashboard')

    return redirect('team_lead_dashboard')


@login_required
@role_required(['super_admin'])
def export_report(request):
    """ Export activity report to CSV """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="activity_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Activity Title', 'Node Name', 'Status', 'Start Date', 'End Date', 'Assigned Users'])

    activities = Activity.objects.all()
    for activity in activities:
        assigned_users = ", ".join([user.username for user in activity.assigned_users.all()])
        writer.writerow([activity.title, activity.node_name, activity.status, activity.start_date, activity.end_date, assigned_users])

    return response

def home(request):
    return render(request, 'activity/home.html')
