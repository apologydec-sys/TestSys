import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Member, Attendance, Announcement
from .forms import MemberForm, AttendanceForm, AnnouncementForm, BulkAttendanceForm

# Setup logging
logger = logging.getLogger(__name__)


def login_view(request):
    """User login with enhanced error handling"""
    try:
        if request.user.is_authenticated:
            return redirect('dashboard')
        
        if request.method == 'POST':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            
            if not username or not password:
                messages.error(request, 'Username and password are required.')
                return render(request, 'church_app/login.html')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                logger.info(f"User {username} logged in successfully")
                return redirect('dashboard')
            else:
                logger.warning(f"Failed login attempt for user {username}")
                messages.error(request, 'Invalid username or password.')
        
        return render(request, 'church_app/login.html')
    
    except Exception as e:
        logger.error(f"Login view error: {str(e)}")
        messages.error(request, 'An unexpected error occurred. Please try again.')
        return render(request, 'church_app/login.html')


def logout_view(request):
    """User logout"""
    try:
        logout(request)
        logger.info(f"User logged out")
        return redirect('login')
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return redirect('login')


@login_required
def dashboard(request):
    """Dashboard with real-time statistics"""
    try:
        total_members = Member.objects.count()
        today = timezone.now().date()
        
        # Attendance for this week's Sunday
        sunday_attendance = Attendance.objects.filter(
            date__lte=today,
            date__gte=today - timedelta(days=today.weekday() + 1),
            service_type__icontains='Sunday',
            status='Present'
        ).count()
        
        # Today's attendance
        today_attendance = Attendance.objects.filter(date=today, status='Present').count()
        
        # Recent members
        recent_members = Member.objects.order_by('-created_at')[:5]
        
        # Active announcements
        announcements = Announcement.objects.filter(is_active=True)[:5]
        
        # Attendance chart data (last 4 Sundays)
        sunday_data = []
        labels = []
        for i in range(4):
            sunday = today - timedelta(days=today.weekday() + 1 + (i * 7))
            count = Attendance.objects.filter(
                date=sunday, 
                status='Present', 
                service_type__icontains='Sunday'
            ).count()
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
    
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        messages.error(request, 'Error loading dashboard.')
        return render(request, 'church_app/dashboard.html', {})


@login_required
def member_list(request):
    """List members with filtering and search"""
    try:
        search_query = request.GET.get('search', '').strip()
        department_filter = request.GET.get('department', '').strip()
        
        members = Member.objects.all()
        
        if search_query:
            members = members.filter(
                Q(name__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        if department_filter and department_filter != 'All':
            members = members.filter(department=department_filter)
        
        departments = Member.objects.values_list('department', flat=True).distinct()
        
        context = {
            'members': members,
            'search_query': search_query,
            'department_filter': department_filter,
            'departments': departments,
        }
        return render(request, 'church_app/member_list.html', context)
    
    except Exception as e:
        logger.error(f"Member list error: {str(e)}")
        messages.error(request, 'Error loading members.')
        return render(request, 'church_app/member_list.html', {})


@login_required
def member_add(request):
    """Add new member with validation"""
    try:
        if request.method == 'POST':
            form = MemberForm(request.POST)
            if form.is_valid():
                member = form.save()
                logger.info(f"Member {member.name} added successfully")
                
                # Send real-time update via WebSocket
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        'members',
                        {
                            'type': 'member_update',
                            'action': 'added',
                            'member_id': member.id,
                            'member_name': member.name,
                        }
                    )
                except:
                    pass  # Real-time update failed, but form was saved
                
                messages.success(request, 'Member added successfully!')
                return redirect('member_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = MemberForm()
        
        return render(request, 'church_app/member_form.html', {'form': form, 'action': 'Add'})
    
    except Exception as e:
        logger.error(f"Member add error: {str(e)}")
        messages.error(request, 'Error adding member.')
        return render(request, 'church_app/member_form.html', {'form': MemberForm(), 'action': 'Add'})


@login_required
def member_edit(request, pk):
    """Edit existing member"""
    try:
        member = get_object_or_404(Member, pk=pk)
        
        if request.method == 'POST':
            form = MemberForm(request.POST, instance=member)
            if form.is_valid():
                form.save()
                logger.info(f"Member {member.name} updated successfully")
                
                # Send real-time update
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        'members',
                        {
                            'type': 'member_update',
                            'action': 'updated',
                            'member_id': member.id,
                            'member_name': member.name,
                        }
                    )
                except:
                    pass
                
                messages.success(request, 'Member updated successfully!')
                return redirect('member_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = MemberForm(instance=member)
        
        return render(request, 'church_app/member_form.html', {'form': form, 'action': 'Edit', 'member': member})
    
    except Exception as e:
        logger.error(f"Member edit error: {str(e)}")
        messages.error(request, 'Error editing member.')
        return redirect('member_list')


@login_required
def member_delete(request, pk):
    """Delete member"""
    try:
        member = get_object_or_404(Member, pk=pk)
        
        if request.method == 'POST':
            member_name = member.name
            member.delete()
            logger.info(f"Member {member_name} deleted successfully")
            
            # Send real-time update
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'members',
                    {
                        'type': 'member_update',
                        'action': 'deleted',
                        'member_id': pk,
                    }
                )
            except:
                pass
            
            messages.success(request, 'Member deleted successfully!')
            return redirect('member_list')
        
        return render(request, 'church_app/member_delete.html', {'member': member})
    
    except Exception as e:
        logger.error(f"Member delete error: {str(e)}")
        messages.error(request, 'Error deleting member.')
        return redirect('member_list')


@login_required
def member_detail(request, pk):
    """View member details and attendance history"""
    try:
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
    
    except Exception as e:
        logger.error(f"Member detail error: {str(e)}")
        messages.error(request, 'Error loading member details.')
        return redirect('member_list')


@login_required
def attendance_list(request):
    """List attendance records"""
    try:
        date_filter = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
        service_filter = request.GET.get('service', 'Sunday Service')
        
        attendances = Attendance.objects.all()
        
        if date_filter:
            try:
                attendances = attendances.filter(date=date_filter)
            except ValueError:
                logger.warning(f"Invalid date filter: {date_filter}")
        
        if service_filter and service_filter != 'All Services':
            attendances = attendances.filter(service_type__icontains=service_filter)
        
        services = Attendance.objects.values_list('service_type', flat=True).distinct()
        
        context = {
            'attendances': attendances,
            'date_filter': date_filter,
            'service_filter': service_filter,
            'services': services,
        }
        return render(request, 'church_app/attendance_list.html', context)
    
    except Exception as e:
        logger.error(f"Attendance list error: {str(e)}")
        messages.error(request, 'Error loading attendance.')
        return render(request, 'church_app/attendance_list.html', {})


@login_required
def attendance_mark(request):
    """Mark attendance with bulk operations"""
    try:
        date_str = request.GET.get('date', timezone.now().strftime('%Y-%m-%d'))
        service_type = request.GET.get('service', 'Sunday Service')
        
        if request.method == 'POST':
            date = request.POST.get('date', date_str)
            service = request.POST.get('service_type', service_type)
            member_ids = request.POST.getlist('member_ids')
            
            if not member_ids:
                messages.warning(request, 'Please select at least one member.')
                return redirect('attendance_mark')
            
            try:
                # Clear existing attendance for this date and service
                deleted_count, _ = Attendance.objects.filter(date=date, service_type=service).delete()
                
                # Create new attendance records
                attendance_records = []
                for member_id in member_ids:
                    status = request.POST.get(f'status_{member_id}', 'Present')
                    attendance_records.append(
                        Attendance(
                            member_id=member_id,
                            date=date,
                            service_type=service,
                            status=status,
                            marked_by=request.user
                        )
                    )
                
                Attendance.objects.bulk_create(attendance_records)
                logger.info(f"Attendance marked for {len(member_ids)} members on {date}")
                
                # Send real-time update
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        'attendance',
                        {
                            'type': 'attendance_update',
                            'action': 'marked',
                            'date': date,
                            'service': service,
                            'count': len(member_ids),
                        }
                    )
                except:
                    pass
                
                messages.success(request, f'Attendance marked for {len(member_ids)} members!')
                return redirect('attendance_list')
            
            except Exception as e:
                logger.error(f"Error marking attendance: {str(e)}")
                messages.error(request, 'Error marking attendance. Please try again.')
        
        # Get all members
        members = Member.objects.all()
        
        # Get existing attendance for this date and service
        try:
            existing_attendance = {
                a.member_id: a.status 
                for a in Attendance.objects.filter(date=date_str, service_type=service_type)
            }
        except ValueError:
            existing_attendance = {}
        
        context = {
            'members': members,
            'date': date_str,
            'service_type': service_type,
            'existing_attendance': existing_attendance,
        }
        return render(request, 'church_app/attendance_mark.html', context)
    
    except Exception as e:
        logger.error(f"Attendance mark error: {str(e)}")
        messages.error(request, 'Error in attendance marking.')
        return render(request, 'church_app/attendance_mark.html', {})


@login_required
def attendance_add(request):
    """Add individual attendance record"""
    try:
        if request.method == 'POST':
            form = AttendanceForm(request.POST)
            if form.is_valid():
                attendance = form.save(commit=False)
                attendance.marked_by = request.user
                attendance.save()
                logger.info(f"Attendance recorded for member on {attendance.date}")
                
                messages.success(request, 'Attendance recorded successfully!')
                return redirect('attendance_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = AttendanceForm()
        
        return render(request, 'church_app/attendance_form.html', {'form': form, 'action': 'Add'})
    
    except Exception as e:
        logger.error(f"Attendance add error: {str(e)}")
        messages.error(request, 'Error adding attendance.')
        return render(request, 'church_app/attendance_form.html', {'form': AttendanceForm(), 'action': 'Add'})


@login_required
def attendance_delete(request, pk):
    """Delete attendance record"""
    try:
        attendance = get_object_or_404(Attendance, pk=pk)
        
        if request.method == 'POST':
            date = attendance.date
            attendence_id = attendance.id
            attendance.delete()
            logger.info(f"Attendance record {attendence_id} deleted")
            
            messages.success(request, 'Attendance record deleted successfully!')
            return redirect('attendance_list')
        
        return render(request, 'church_app/attendance_delete.html', {'attendance': attendance})
    
    except Exception as e:
        logger.error(f"Attendance delete error: {str(e)}")
        messages.error(request, 'Error deleting attendance.')
        return redirect('attendance_list')


@login_required
def announcement_list(request):
    """List announcements"""
    try:
        announcements = Announcement.objects.all()
        context = {'announcements': announcements}
        return render(request, 'church_app/announcement_list.html', context)
    
    except Exception as e:
        logger.error(f"Announcement list error: {str(e)}")
        messages.error(request, 'Error loading announcements.')
        return render(request, 'church_app/announcement_list.html', {'announcements': []})


@login_required
def announcement_add(request):
    """Add new announcement"""
    try:
        if request.method == 'POST':
            form = AnnouncementForm(request.POST)
            if form.is_valid():
                announcement = form.save(commit=False)
                announcement.posted_by = request.user
                announcement.save()
                logger.info(f"Announcement '{announcement.title}' posted")
                
                # Send real-time notification
                try:
                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        'announcements',
                        {
                            'type': 'announcement_update',
                            'action': 'posted',
                            'title': announcement.title,
                            'announcement_id': announcement.id,
                        }
                    )
                except:
                    pass
                
                messages.success(request, 'Announcement posted successfully!')
                return redirect('announcement_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = AnnouncementForm()
        
        return render(request, 'church_app/announcement_form.html', {'form': form, 'action': 'Add'})
    
    except Exception as e:
        logger.error(f"Announcement add error: {str(e)}")
        messages.error(request, 'Error posting announcement.')
        return render(request, 'church_app/announcement_form.html', {'form': AnnouncementForm(), 'action': 'Add'})


@login_required
def announcement_edit(request, pk):
    """Edit announcement"""
    try:
        announcement = get_object_or_404(Announcement, pk=pk)
        
        if request.method == 'POST':
            form = AnnouncementForm(request.POST, instance=announcement)
            if form.is_valid():
                form.save()
                logger.info(f"Announcement {pk} updated")
                
                messages.success(request, 'Announcement updated successfully!')
                return redirect('announcement_list')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = AnnouncementForm(instance=announcement)
        
        return render(request, 'church_app/announcement_form.html', {'form': form, 'action': 'Edit', 'announcement': announcement})
    
    except Exception as e:
        logger.error(f"Announcement edit error: {str(e)}")
        messages.error(request, 'Error updating announcement.')
        return redirect('announcement_list')


@login_required
def member_detail(request, pk):
    try:
        member = Member.objects.get(pk=pk)
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
    except Member.DoesNotExist:
        messages.error(request, 'Member not found.')
        return redirect('member_list')
    except Exception as e:
        logger.error(f"Member detail error: {str(e)}")
        messages.error(request, 'Error loading member details.')
        return redirect('member_list')


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
    """Delete announcement"""
    try:
        announcement = get_object_or_404(Announcement, pk=pk)
        
        if request.method == 'POST':
            title = announcement.title
            announcement.delete()
            logger.info(f"Announcement '{title}' deleted")
            
            messages.success(request, 'Announcement deleted successfully!')
            return redirect('announcement_list')
        
        return render(request, 'church_app/announcement_delete.html', {'announcement': announcement})
    
    except Exception as e:
        logger.error(f"Announcement delete error: {str(e)}")
        messages.error(request, 'Error deleting announcement.')
        return redirect('announcement_list')


# ============ REAL-TIME API ENDPOINTS ============

@login_required
@require_http_methods(["GET"])
def api_members(request):
    """API endpoint for real-time member list"""
    try:
        members = Member.objects.all().values('id', 'name', 'email', 'phone', 'department')
        return JsonResponse({
            'status': 'success',
            'data': list(members),
            'count': len(members),
        })
    except Exception as e:
        logger.error(f"API members error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Error fetching members.',
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_announcements(request):
    """API endpoint for real-time announcements"""
    try:
        announcements = Announcement.objects.filter(is_active=True).values(
            'id', 'title', 'message', 'date_posted', 'posted_by__username'
        )
        return JsonResponse({
            'status': 'success',
            'data': list(announcements),
            'count': len(announcements),
        })
    except Exception as e:
        logger.error(f"API announcements error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Error fetching announcements.',
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_attendance_stats(request):
    """API endpoint for attendance statistics"""
    try:
        today = timezone.now().date()
        
        stats = {
            'today': Attendance.objects.filter(
                date=today, 
                status='Present'
            ).count(),
            'week': Attendance.objects.filter(
                date__lte=today,
                date__gte=today - timedelta(days=7),
                status='Present'
            ).count(),
            'total_members': Member.objects.count(),
        }
        
        return JsonResponse({
            'status': 'success',
            'data': stats,
        })
    except Exception as e:
        logger.error(f"API attendance stats error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Error fetching statistics.',
        }, status=500)
