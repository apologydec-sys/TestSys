"""
WebSocket consumers for real-time updates in Django Channels
"""

import logging
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Member, Attendance, Announcement

logger = logging.getLogger(__name__)


class MemberConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time member updates"""
    
    async def connect(self):
        """Handle new WebSocket connection"""
        self.room_group_name = 'members'
        
        # Check authentication
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.scope['user']} connected to members group")
            
            # Send initial data
            await self.send_initial_data()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("User disconnected from members group")
    
    async def receive(self, text_data):
        """Receive message from client"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'get_members':
                await self.send_initial_data()
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Unknown action'
                }))
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
    
    async def member_update(self, event):
        """Handle member update from group"""
        await self.send(text_data=json.dumps({
            'type': 'member_update',
            'action': event['action'],
            'member_id': event.get('member_id'),
            'member_name': event.get('member_name'),
        }))
    
    async def send_initial_data(self):
        """Send initial member data to client"""
        members = await self.get_members()
        await self.send(text_data=json.dumps({
            'type': 'initial_data',
            'members': members,
        }))
    
    @database_sync_to_async
    def get_members(self):
        """Get all members from database"""
        return list(
            Member.objects.all().values('id', 'name', 'email', 'phone', 'department')
        )


class AttendanceConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time attendance updates"""
    
    async def connect(self):
        """Handle new WebSocket connection"""
        self.room_group_name = 'attendance'
        
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.scope['user']} connected to attendance group")
            
            # Send attendance statistics
            await self.send_stats()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("User disconnected from attendance group")
    
    async def receive(self, text_data):
        """Receive message from client"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'get_stats':
                await self.send_stats()
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Unknown action'
                }))
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
    
    async def attendance_update(self, event):
        """Handle attendance update from group"""
        await self.send(text_data=json.dumps({
            'type': 'attendance_update',
            'action': event['action'],
            'date': event.get('date'),
            'service': event.get('service'),
            'count': event.get('count'),
            'timestamp': str(event.get('timestamp', '')),
        }))
    
    async def send_stats(self):
        """Send attendance statistics"""
        stats = await self.get_attendance_stats()
        await self.send(text_data=json.dumps({
            'type': 'attendance_stats',
            'stats': stats,
        }))
    
    @database_sync_to_async
    def get_attendance_stats(self):
        """Get attendance statistics from database"""
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        return {
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


class AnnouncementConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time announcement updates"""
    
    async def connect(self):
        """Handle new WebSocket connection"""
        self.room_group_name = 'announcements'
        
        if self.scope['user'].is_authenticated:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.scope['user']} connected to announcements group")
            
            # Send initial announcements
            await self.send_announcements()
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info("User disconnected from announcements group")
    
    async def receive(self, text_data):
        """Receive message from client"""
        try:
            data = json.loads(text_data)
            action = data.get('action')
            
            if action == 'get_announcements':
                await self.send_announcements()
            else:
                await self.send(text_data=json.dumps({
                    'error': 'Unknown action'
                }))
        
        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
    
    async def announcement_update(self, event):
        """Handle announcement update from group"""
        await self.send(text_data=json.dumps({
            'type': 'announcement_update',
            'action': event['action'],
            'title': event.get('title'),
            'announcement_id': event.get('announcement_id'),
            'timestamp': str(event.get('timestamp', '')),
        }))
    
    async def send_announcements(self):
        """Send active announcements"""
        announcements = await self.get_announcements()
        await self.send(text_data=json.dumps({
            'type': 'announcements_list',
            'announcements': announcements,
        }))
    
    @database_sync_to_async
    def get_announcements(self):
        """Get all active announcements from database"""
        return list(
            Announcement.objects.filter(is_active=True).values(
                'id', 'title', 'message', 'date_posted', 'posted_by__username'
            ).order_by('-date_posted')[:10]
        )
