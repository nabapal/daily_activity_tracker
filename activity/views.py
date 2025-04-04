from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Activity, ActivityUpdate
from .forms import ActivityUpdateForm, ActivityForm


@login_required
def user_dashboard(request):
    # Get activities assigned to user or where user is creator
    activities = Activity.objects.filter(
        Q(assigned_to=request.user) | Q(created_by=request.user)
    ).distinct().order_by('-created_at')

    return render(request, 'activity/dashboard.html', {
        'activities': activities
    })


@login_required
def activity_detail(request, pk):
    activity = get_object_or_404(Activity, pk=pk)

    if request.method == 'POST':
        form = ActivityUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.activity = activity
            update.user = request.user
            update.save()
            return redirect('activity_detail', pk=pk)
    else:
        form = ActivityUpdateForm()

    return render(request, 'activity/activity_detail.html', {
        'activity': activity,
        'updates': activity.updates.all(),
        'assigned_users': activity.assigned_to.all(),
        'form': form
    })


@login_required
def team_lead_dashboard(request):
    if not request.user.role == 'LEAD':
        return redirect('dashboard')

    team_activities = Activity.objects.filter(
        Q(created_by=request.user) |
        Q(assigned_to__in=request.user.team_members.all())
    ).distinct()

    return render(request, 'activity/lead_dashboard.html', {
        'activities': team_activities
    })
def is_super_admin(user):
    return user.role == 'ADMIN'  # Or whatever your super admin role check is

@login_required
@user_passes_test(is_super_admin)
def super_admin_dashboard(request):
    activities = Activity.objects.all()
    return render(request, 'activity/super_admin_dashboard.html', {
        'activities': activities
    })


@login_required
def assign_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            form.save_m2m()  # Needed for many-to-many relationships
            return redirect('dashboard')  # Redirect to dashboard after assignment
    else:
        form = ActivityForm()

    return render(request, 'activity/assign_activity.html', {
        'form': form
    })


# Assign Activity View
@login_required
def assign_activity(request):
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.created_by = request.user
            activity.save()
            form.save_m2m()  # Save many-to-many relationships
            return redirect('dashboard')
    else:
        form = ActivityForm()

    return render(request, 'activity/assign_activity.html', {'form': form})


# Export Report View
@login_required
def export_report(request):
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="activity_report.csv"'

    writer = csv.writer(response)
    # Write CSV header
    writer.writerow(['ID', 'Title', 'Status', 'Start Date', 'End Date', 'Assigned Users', 'Last Update'])

    # Get activities for the current user
    activities = Activity.objects.filter(
        Q(assigned_to=request.user) | Q(created_by=request.user)
    ).distinct()

    for activity in activities:
        last_update = activity.updates.last()
        writer.writerow([
            activity.id,
            activity.title,
            activity.get_status_display(),
            activity.start_date.strftime('%Y-%m-%d'),
            activity.end_date.strftime('%Y-%m-%d'),
            ', '.join([user.username for user in activity.assigned_to.all()]),
            last_update.created_at.strftime('%Y-%m-%d %H:%M') if last_update else 'None'
        ])

    return response


@login_required
def home(request):
    # Get activities for the current user
    user_activities = Activity.objects.filter(assigned_to=request.user).order_by('-start_date')

    return render(request, 'activity/home.html', {
        'activities': user_activities
    })