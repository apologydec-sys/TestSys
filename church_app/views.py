from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Member, Attendance, Announcement
from .forms import MemberForm, AttendanceForm, AnnouncementForm, BulkAttendanceForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'church_app/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # Statistics
    total_members = Member.objects.count()
    today = timezone.now().date()
    
    # Attendance for this week's Sunday
    sunday_attendance = Attendance.objects.filter(
        date__lte=today,
        date__gte=today - timedelta(days=today.weekday() + 1),
        service_type__icontains='Sunday'
    ).count()
    
    # Today's attendance
    today_attendance = Attendance.objects.filter(date=today).count()
    
    # Recent members
    recent_members = Member.objects.order_by('-created_at')[:5]
    
    # Active announcements
    announcements = Announcement.objects.filter(is_active=True)[:5]
    
    # Attendance chart data (last 4 Sundays)
    sunday_data = []
    labels = []
    for i in range(4):
        sunday = today - timedelta(days=today.weekday() + 1 + (i * 7))
        count = Attendance.objects.filter(date=sunday, status='Present').count()
        sunday_data.append(count)
        labels.append(sunday.strftime('%b %d'))
    
    context = {
        'total_members': total_members,
        'sunday_attendance': sunday_attendance,
        'today_attendance': today_attendance,
        'recent_members': recent_members,
        'announcements': announcements,
        'chart_labels': labels[::-1],
        'chart_data': sunday_data[::-1],
    }
    return render(request, 'church_app/dashboard.html', context)


@login_required
def member_list(request):
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    
    members = Member.objects.all()
    
    if search_query:
        members = members.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    if department_filter:
        members = members.filter(department=department_filter)
    
    departments = Member.objects.values_list('department', flat=True).distinct()
    
    context = {
        'members': members,
        'search_query': search_query,
        'department_filter': department_filter,
        'departments': departments,
    }
    return render(request, 'church_app/member_list.html', context)


@login_required
def member_add(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member added successfully!')
            return redirect('member_list')
    else:
        form = MemberForm()
    
    return render(request, 'church_app/member_form.html', {'form': form, 'action': 'Add'})


@login_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    
    return render(request, 'church_app/member_form.html', {'form': form, 'action': 'Edit', 'member': member})


@login_required
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Member deleted successfully!')
        return redirect('member_list')
    
    return render(request, 'church_app/member_delete.html', {'member': member})


@login_required
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    attendances = member.attendances.order_by('-date')[:20]
    total_services = member.attendances.count()
    present_count = member.attendances.filter(status='Present').count()
    attendance_rate = (present_count / total_services * 100) if total_services > 0 else 0
    
    context = {
        'member': member,
        'attendances': attendances,
        'total_services': total_services,
        'attendance_rate': round(attendance_rate, 1),
    }
    return render(request, 'church_app/member_detail.html', context)


@login_required
def attendance_list(request):
    date_filter = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
    service_filter = request.GET.get('service', '')
    
    attendances = Attendance.objects.all()
    
    if date_filter:
        attendances = attendances.filter(date=date_filter)
    
    if service_filter:
        attendances = attendances.filter(service_type__icontains=service_filter)
    
    services = Attendance.objects.values_list('service_type', flat=True).distinct()
    
    context = {
        'attendances': attendances,
        'date_filter': date_filter,
        'service_filter': service_filter,
        'services': services,
    }
    return render(request, 'church_app/attendance_list.html', context)


@login_required
def attendance_mark(request):
    date_str = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
    service_type = request.GET.get('service', 'Sunday Service')
    
    if request.method == 'POST':
        date = request.POST.get('date', date_str)
        service = request.POST.get('service_type', service_type)
        member_ids = request.POST.getlist('member_ids')
        
        # Clear existing attendance for this date and service
        Attendance.objects.filter(date=date, service_type=service).delete()
        
        # Create new attendance records
        for member_id in member_ids:
            status = request.POST.get(f'status_{member_id}', 'Absent')
            Attendance.objects.create(
                member_id=member_id,
                date=date,
                service_type=service,
                status=status,
                marked_by=request.user
            )
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('attendance_list')
    
    # Get all members
    members = Member.objects.all()
    
    # Get existing attendance for this date and service
    existing_attendance = {
        a.member_id: a.status 
        for a in Attendance.objects.filter(date=date_str, service_type=service_type)
    }
    
    context = {
        'members': members,
        'date': date_str,
        'service_type': service_type,
        'existing_attendance': existing_attendance,
    }
    return render(request, 'church_app/attendance_mark.html', context)


@login_required
def attendance_add(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.marked_by = request.user
            attendance.save()
            messages.success(request, 'Attendance recorded successfully!')
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    
    return render(request, 'church_app/attendance_form.html', {'form': form, 'action': 'Add'})


@login_required
def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, pk=pk)
    
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'Attendance record deleted successfully!')
        return redirect('attendance_list')
    
    return render(request, 'church_app/attendance_delete.html', {'attendance': attendance})


@login_required
def announcement_list(request):
    announcements = Announcement.objects.all()
    return render(request, 'church_app/announcement_list.html', {'announcements': announcements})


@login_required
def announcement_add(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.posted_by = request.user
            announcement.save()
            messages.success(request, 'Announcement posted successfully!')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm()
    
    return render(request, 'church_app/announcement_form.html', {'form': form, 'action': 'Add'})


@login_required
def announcement_edit(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('announcement_list')
    else:
        form = AnnouncementForm(instance=announcement)
    
    return render(request, 'church_app/announcement_form.html', {'form': form, 'action': 'Edit', 'announcement': announcement})


@login_required
def announcement_delete(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement deleted successfully!')
        return redirect('announcement_list')
    
    return render(request, 'church_app/announcement_delete.html', {'announcement': announcement})
