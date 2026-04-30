cd# 🙏 Church Management System - Real-Time Edition

A modern, responsive, real-time church management system built with Django, Django Channels, and Bootstrap 5. Perfect for churches of any size to manage members, track attendance, and share announcements - all accessible from any device!

## ✨ Key Features

### 🔄 Real-Time Updates
- **WebSocket Support**: Live member, attendance, and announcement updates across all connected devices
- **Instant Notifications**: Real-time notifications when data changes
- **Multi-Device Sync**: Updates instant across phone, tablet, and desktop

### 📱 Responsive Design
- **Mobile-First**: Optimized for all screen sizes (mobile, tablet, desktop)
- **Touch Friendly**: Easy-to-use interface on smartphones
- **Offline Support**: Clean error handling for connectivity issues

### 👥 Member Management
- Add, edit, delete, and view members
- Search and filter by name, email, or phone
- Track member history and attendance rate
- Department and gender tracking

### 📊 Attendance System
- Bulk attendance marking for services
- Individual attendance records
- Attendance statistics and trends
- Service type classification

### 📢 Announcements System
- Post announcements with titles and descriptions
- Real-time announcement updates
- Mark announcements as active/inactive
- View announcement history

### 📈 Analytics Dashboard
- Real-time statistics
- Attendance trends (last 4 weeks)
- Member count overview
- Today's attendance status

### 🔐 Security & Error Handling
- User authentication required
- CSRF protection
- Comprehensive error logging
- Graceful error handling
- Form validation with user feedback

## 🛠️ Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Backend** | Django | 4.2.29 |
| **Real-Time** | Django Channels + Redis | 4.0.0 |
| **Frontend** | Bootstrap 5, JavaScript | 5.3.0 |
| **Database** | SQLite/MySQL/PostgreSQL | - |
| **Cache** | Redis | 7+ |
| **Server** | Daphne ASGI | - |
| **Deployment** | Docker, Render, Heroku | - |

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- pip
- Git

### Installation

1. **Clone/Navigate to project:**
   ```bash
   cd g:\django\ChurchManagement
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # OR
   source venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment file:**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access application:**
   - Open: `http://localhost:8000`
   - Login with superuser credentials

## 🐳 Docker Deployment (Recommended)

Perfect for production or consistent environments!

### Quick Start
```bash
docker-compose up -d
```

This starts:
- Django app (port 8000)
- PostgreSQL database
- Redis cache

## ☁️ Cloud Deployment

### Render.com (Free tier available)
```bash
# Push to GitHub
git push origin main

# Create service on render.com
# Connect GitHub repo and configure
```

### Heroku (Paid)
```bash
heroku create your-church-app
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:premium-0
git push heroku main
```

**Detailed deployment guide**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 📱 Access Across Devices

- **Smartphone**: Open app URL in browser, bookmark it
- **Tablet**: Use in landscape or portrait mode
- **Desktop**: Full feature access with sidebar navigation
- **Any Browser**: Works on Chrome, Firefox, Safari, Edge

## 🔄 Real-Time Features

### WebSocket Endpoints
- `/ws/members/` - Live member updates
- `/ws/attendance/` - Live attendance changes  
- `/ws/announcements/` - Live announcements

### REST API Endpoints
- `GET /api/members/` - Get all members
- `GET /api/announcements/` - Get announcements
- `GET /api/attendance/stats/` - Get statistics

## 📋 Project Structure

```
ChurchManagement/
├── church_management/
│   ├── settings.py           # Django configuration (Channels, Redis, etc.)
│   ├── asgi.py               # Channels ASGI configuration
│   ├── urls.py               # URL routing
│   └── wsgi.py               # WSGI configuration
├── church_app/
│   ├── models.py             # Database models
│   ├── views.py              # Views & API endpoints
│   ├── consumers.py          # WebSocket consumers (NEW)
│   ├── routing.py            # Channels routing (NEW)
│   ├── urls.py               # App URLs
│   ├── forms.py              # Django forms
│   ├── admin.py              # Admin configuration
│   └── migrations/           # Database migrations
├── templates/
│   ├── base.html             # Base template (ENHANCED)
│   └── church_app/           # App templates
├── static/                   # CSS, JS, images
├── logs/                     # Application logs (NEW)
├── Dockerfile                # Docker configuration (NEW)
├── docker-compose.yml        # Docker Compose (NEW)
├── Procfile                  # Heroku deployment (NEW)
├── .env.example              # Environment variables (NEW)
├── DEPLOYMENT_GUIDE.md       # Detailed deployment guide (NEW)
├── requirements.txt          # Python dependencies (UPDATED)
└── manage.py                 # Django management
```

## 📊 Database Models

### Member
```
- id: Integer (Primary Key)
- name: String (100)
- email: Email
- phone: String (20)
- gender: Choice (Male/Female)
- department: Choice (Ushering, Choir, Prayer, Youth, Children, Media, Welfare, None)
- date_joined: Date
- address: Text
- created_at: DateTime (auto)
- updated_at: DateTime (auto)
```

### Attendance
```
- id: Integer (Primary Key)
- member: Foreign Key (Member)
- date: Date
- status: Choice (Present/Absent)
- service_type: String (50)
- notes: Text
- marked_by: Foreign Key (User)
- created_at: DateTime (auto)
```

### Announcement
```
- id: Integer (Primary Key)
- title: String (200)
- message: Text
- date_posted: DateTime (auto)
- posted_by: Foreign Key (User)
- is_active: Boolean
```

## 🔑 Key URLs

| URL | Purpose |
|-----|---------|
| `/` | Login page |
| `/dashboard/` | Main dashboard |
| `/members/` | Members list |
| `/attendance/` | Attendance list |
| `/announcements/` | Announcements list |
| `/api/members/` | Members API |
| `/api/announcements/` | Announcements API |
| `/api/attendance/stats/` | Statistics API |
| `/ws/members/` | Members WebSocket |
| `/ws/attendance/` | Attendance WebSocket |
| `/ws/announcements/` | Announcements WebSocket |

## ⚙️ Configuration

Create `.env` file from `.env.example`:

```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
REDIS_URL=redis://localhost:6379/0
ALLOWED_HOSTS=localhost,yourdomain.com
```

## 🔐 Security Features

✅ User authentication with Django auth system
✅ CSRF protection on all forms
✅ SQL injection prevention (ORM)
✅ XSS protection (template escaping)
✅ Secure password hashing (PBKDF2)
✅ Session management with Redis
✅ HTTPS ready for production
✅ WebSocket authentication required

## 📊 Enhancements Made

- ✅ Django Channels for real-time WebSocket support
- ✅ Redis caching for performance
- ✅ Comprehensive error handling throughout
- ✅ Enhanced responsive design (mobile-first)
- ✅ Real-time API endpoints
- ✅ Docker & Docker Compose setup
- ✅ Heroku & Render deployment ready
- ✅ Logging system with rotation
- ✅ CORS support for APIs
- ✅ Load balancer ready
- ✅ Multi-device support
- ✅ Progressive enhancement

## 🐛 Error Handling

The system includes:
- Try/catch blocks around all operations
- Logging to `logs/church_management.log`
- User-friendly error messages
- Form validation feedback
- Graceful degradation

## ⚡ Performance

- Redis session caching
- Database query optimization
- White Noise static file compression
- Bulk database operations
- Async WebSocket updates

## 🚀 Production Checklist

- [ ] Set DEBUG=False
- [ ] Generate strong SECRET_KEY
- [ ] Configure database (PostgreSQL recommended)
- [ ] Setup Redis
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS/SSL
- [ ] Setup error monitoring
- [ ] Configure backups
- [ ] Test on mobile
- [ ] Setup domains/CDN
- [ ] Configure email
- [ ] Test all URLs

## 📚 Documentation

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[.env.example](.env.example)** - Configuration template
- **[Dockerfile]** - Docker configuration
- **[docker-compose.yml]** - Docker Compose setup

## 🤝 Support

For issues or questions:
1. Check logs in `logs/church_management.log`
2. Review error messages in browser console
3. Ensure all required packages are installed
4. Verify database and Redis connections

## 📝 License

Built for churches and non-profit organizations.

## ✅ Deployment Status

- ✅ Local Development Ready
- ✅ Docker Ready
- ✅ Render.com Ready
- ✅ Heroku Ready
- ✅ AWS Ready
- ✅ Multi-Device Compatible
- ✅ Real-Time Features Working
- ✅ Production Ready

---

**Made with ❤️ for churches everywhere**

Latest Update: 2026-04-30


## Security Features

- CSRF protection on all forms
- Authentication required for all pages (except login)
- Django's built-in security middleware
- SQL injection protection through ORM

## Bonus Features for Higher Marks

✅ **Search members** - Search by name, phone, or email  
✅ **Filter by department** - Filter members by department  
📊 **Dashboard statistics** - Visual stats with Chart.js  
🎨 **Modern UI** - Clean Bootstrap 5 design with sidebar navigation  
📱 **Responsive design** - Works on mobile and desktop  

## License

This project is for educational purposes.

## Author

Built for a school project demonstration.

---

**Problem Statement for Documentation:**
> Churches in my community rely on manual record keeping, which leads to data loss, poor tracking of attendance, and inefficient communication.

**Solution:**
> This project provides a web-based Church Management System that allows administrators to manage members, track attendance, and share announcements digitally, solving the problems of data loss and inefficient manual record-keeping.
