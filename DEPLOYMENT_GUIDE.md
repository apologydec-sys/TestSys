# 🙏 Church Management System - Real-Time Edition

A modern, responsive, real-time church management system built with Django, Django Channels, and Bootstrap 5. Features real-time updates across all devices, comprehensive member management, attendance tracking, and announcement systems.

## ✨ Features

- **Real-Time Updates**: WebSocket-based live updates for members, attendance, and announcements
- **Responsive Design**: Mobile-first approach works on phones, tablets, and desktops
- **Member Management**: Add, edit, delete, and search members by name, phone, or email
- **Attendance Tracking**: Bulk attendance marking with service type tracking
- **Announcements**: Post and manage church announcements with real-time notifications
- **Dashboard Analytics**: View attendance statistics and member insights
- **Authentication**: Secure login system with session management
- **Error Handling**: Comprehensive error logging and user-friendly error messages
- **Multi-Device Support**: Access from any device with a web browser
- **Caching**: Redis-based caching for optimal performance

## 🚀 Quick Start

### Local Development (Recommended for Testing)

#### Prerequisites
- Python 3.11+
- pip package manager
- Redis (optional for local development)

#### Setup Steps

1. **Clone and navigate to project**
```bash
cd g:\django\ChurchManagement
```

2. **Create virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Create .env file**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run migrations**
```bash
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Collect static files**
```bash
python manage.py collectstatic --noinput
```

8. **Start development server** (choose one)

   **Without Redis (basic mode):**
   ```bash
   python manage.py runserver
   ```

   **With Redis (full real-time features):**
   ```bash
   # Make sure Redis is running (redis-server or redis-cli)
   daphne -b 0.0.0.0 -p 8000 church_management.asgi:application
   ```

9. **Access the application**
   - Open browser: `http://localhost:8000`
   - Login with superuser credentials

---

## 🐳 Docker Deployment (Recommended for Production)

Docker provides isolated, reproducible environments perfect for production deployment.

### Prerequisites
- Docker
- Docker Compose

### Quick Start with Docker

1. **Start services**
```bash
docker-compose up -d
```

2. **Create superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

3. **Access application**
   - Open: `http://localhost:8000`

### Build Custom Docker Image

```bash
# Build image
docker build -t church-management:latest .

# Run container with environment
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=sqlite:///db.sqlite3 \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  --name church-app \
  church-management:latest
```

---

## ☁️ Cloud Deployment

### Deploy on Render.com (Free Tier Available)

1. **Create Render account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub account

2. **Connect Repository**
   - Create new "Web Service"
   - Connect GitHub repo
   - Select Python as environment

3. **Configure Build & Deploy**
   - Build Command: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - Start Command: `daphne -b 0.0.0.0 -p 8080 church_management.asgi:application`

4. **Add Environment Variables**
   ```
   DEBUG=False
   SECRET_KEY=<generate-secure-key>
   DATABASE_URL=<postgresql-url>
   REDIS_URL=<redis-url>
   ALLOWED_HOSTS=your-app.onrender.com
   ```

5. **Add PostgreSQL Database**
   - Create new PostgreSQL database
   - Copy URL to DATABASE_URL

6. **Add Redis Cache**
   - Create new Redis database
   - Copy URL to REDIS_URL

### Deploy on Heroku (Paid)

1. **Create Heroku app**
```bash
heroku create your-church-app
```

2. **Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

3. **Add Redis**
```bash
heroku addons:create heroku-redis:premium-0
```

4. **Set environment variables**
```bash
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=<your-secret-key>
```

5. **Deploy**
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Deploy on PythonAnywhere (Paid)

1. Upload files via WebDAV or git
2. Set Python 3.11 version
3. Configure WSGI file to use Daphne
4. Add environment variables
5. Reload web app

---

## 📱 Using on Different Devices

### Mobile (iPhone/Android)
1. Open application URL in browser
2. bookmark or add to home screen
3. Works like native app with responsive design

### Tablet
- Optimized for landscape and portrait modes
- Touch-friendly buttons and forms
- Large readable text

### Desktop
- Full features accessible
- Side navigation bar
- Perfect for administration

---

## 🔄 Real-Time Features

### WebSocket Endpoints
- `/ws/members/` - Member updates
- `/ws/attendance/` - Attendance changes
- `/ws/announcements/` - New announcements

### API Endpoints
- `GET /api/members/` - Get all members
- `GET /api/announcements/` - Get active announcements
- `GET /api/attendance/stats/` - Get attendance statistics

---

## 🔍 Key Application URLs

| URL | Purpose |
|-----|---------|
| `/` or `/login/` | Login page |
| `/dashboard/` | Main dashboard |
| `/members/` | Members list |
| `/members/add/` | Add new member |
| `/attendance/` | Attendance list |
| `/attendance/mark/` | Mark attendance |
| `/announcements/` | Announcements list |
| `/api/members/` | Members API |
| `/api/announcements/` | Announcements API |

---

## 📊 Database Schema

### Member
- ID, Name, Email, Phone
- Gender, Department
- Date Joined, Address
- Created At, Updated At

### Attendance
- ID, Member (FK), Date
- Status (Present/Absent)
- Service Type, Notes
- Marked By (User FK)

### Announcement
- ID, Title, Message
- Date Posted, Posted By (User FK)
- Is Active

---

## 🔐 Security Features

✅ User authentication required  
✅ CSRF protection on forms  
✅ SQL injection prevention (ORM)  
✅ XSS protection via template escaping  
✅ Secure password hashing  
✅ Session management  
✅ HTTPS ready (production)  

---

## 🐛 Error Handling

The application includes comprehensive error handling:
- Try/catch blocks around database operations
- Logging of all errors
- User-friendly error messages
- Form validation with feedback
- Graceful degradation

Logs are stored in: `logs/church_management.log`

---

## ⚡ Performance Optimization

- Redis caching for session data
- Database query optimization
- Static file compression (WhiteNoise)
- Bulk operations for attendance
- Async WebSocket updates
- Lazy loading templates

---

## 🛠️ Troubleshooting

### Redis Connection Error
```
Solution: Install Redis or set CHANNEL_LAYERS to dummy backend
Edit settings.py and comment out Redis, use 'channels.layers.InMemoryChannelLayer'
```

### Database Migration Error
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### WebSocket Connection Failed
- Check browser console for errors
- Verify Daphne is running (not Django runserver)
- Check firewall and proxy settings

---

## 📝 Environment Variables Guide

| Variable | Description | Example |
|----------|-------------|---------|
| `DEBUG` | Debug mode (False in production) | `False` |
| `SECRET_KEY` | Django secret key | `your-secret-key` |
| `DATABASE_URL` | Database connection URL | `sqlite:///db.sqlite3` |
| `REDIS_URL` | Redis cache URL | `redis://localhost:6379` |
| `ALLOWED_HOSTS` | Allowed host domains | `localhost,myapp.com` |
| `TIME_ZONE` | Server time zone | `UTC` |

---

## 📚 Technology Stack

- **Backend**: Django 4.2.29
- **Real-Time**: Django Channels 4.0.0
- **Database**: SQLite/MySQL/PostgreSQL
- **Cache**: Redis 7+
- **Frontend**: Bootstrap 5, JavaScript
- **Server**: Daphne ASGI
- **Deployment**: Docker, Render, Heroku, PythonAnywhere

---

## 📞 Support & Maintenance

### Regular Maintenance Tasks
- Backup database daily
- Monitor error logs
- Update dependencies monthly
- Clean up old logs
- Optimize database

### Monitoring
- Check `logs/church_management.log` regularly
- Monitor Redis memory usage
- Track database size
- Monitor server CPU/RAM

---

## 🚀 Future Enhancements

- [ ] SMS notifications
- [ ] Email digest reports
- [ ] Mobile app (Flutter/React Native)
- [ ] Advanced analytics
- [ ] Sermon management
- [ ] Event scheduling
- [ ] Donation tracking
- [ ] Member directory export
- [ ] Permission roles system
- [ ] Multi-language support

---

## 📄 License

This project is built for churches and non-profit organizations.

---

## 🤝 Development Tips

### For Contributors
1. Create feature branch: `git checkout -b feature/name`
2. Commit changes: `git commit -am 'Add feature'`
3. Push branch: `git push origin feature/name`
4. Create pull request

### Code Style
- Follow PEP 8 Python guidelines
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic
- Write tests for new features

---

## ✅ Deployment Checklist

- [ ] Generate strong SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure allowed hosts
- [ ] Setup HTTPS/SSL
- [ ] Configure database backups
- [ ] Setup error logging/monitoring
- [ ] Configure email for notifications
- [ ] Create superuser account
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Setup Redis for caching
- [ ] Configure CORS if needed
- [ ] Test WebSocket connections
- [ ] Setup database replicas/backups
- [ ] Configure CDN for static files

---

**Made with ❤️ for churches everywhere**
