cd# Church Management System

A web-based Church Management System built with Django that helps churches manage members, track attendance, and share announcements digitally.

## Features

- **Admin Dashboard** - Overview with statistics and charts
- **Member Management** - Add, edit, delete, and view members with search and filter
- **Attendance System** - Mark attendance per service, view attendance history
- **Announcements** - Post and manage church announcements
- **Authentication** - Secure login system for administrators

## Tech Stack

- **Backend**: Django 4.2 (Python)
- **Database**: SQLite (default) / MySQL (configurable)
- **Frontend**: Bootstrap 5, Bootstrap Icons, Chart.js
- **Styling**: Custom CSS with modern design

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- (Optional) MySQL if using MySQL database

### Setup Steps

1. **Navigate to the project folder:**
   ```bash
   cd ChurchManagement
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create admin user:**
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create a username and password.

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the application:**
   Open your browser and go to: `http://127.0.0.1:8000/`

## Default Login

If you haven't created a superuser yet, you can use Django admin to create one, or run:
```bash
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@church.com', 'admin123')"
```

Then login with:
- **Username**: admin
- **Password**: admin123

## Database Configuration (Optional - MySQL)

To use MySQL instead of SQLite:

1. Install MySQL client: `pip install mysqlclient`
2. Update `church_management/settings.py`:
   - Comment out the SQLite DATABASES configuration
   - Uncomment the MySQL DATABASES configuration
   - Update database credentials (NAME, USER, PASSWORD, HOST)
3. Create the database in MySQL: `CREATE DATABASE church_db;`
4. Run migrations again

## Project Structure

```
ChurchManagement/
├── church_management/      # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── church_app/               # Main application
│   ├── models.py             # Member, Attendance, Announcement models
│   ├── views.py              # All view functions
│   ├── urls.py               # URL routing
│   ├── forms.py              # Django forms
│   ├── admin.py              # Admin configuration
│   └── migrations/           # Database migrations
├── templates/                # HTML templates
│   ├── base.html             # Base template with sidebar
│   └── church_app/           # App templates
├── static/                   # CSS, JS, images
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Pages

1. **Login** (`/`) - Authentication page
2. **Dashboard** (`/dashboard/`) - Statistics and overview
3. **Members** (`/members/`) - Member list with search/filter
4. **Add Member** (`/members/add/`) - Add new member form
5. **Edit Member** (`/members/<id>/edit/`) - Edit member form
6. **Member Detail** (`/members/<id>/`) - View member details
7. **Attendance** (`/attendance/`) - View attendance records
8. **Mark Attendance** (`/attendance/mark/`) - Bulk attendance marking
9. **Announcements** (`/announcements/`) - View all announcements
10. **Add Announcement** (`/announcements/add/`) - Create new announcement

## Models

### Member
- `name` - Full name
- `phone` - Phone number
- `email` - Email address
- `gender` - Male/Female
- `department` - Church department (Ushering, Choir, Prayer, etc.)
- `date_joined` - Date when member joined
- `address` - Physical address

### Attendance
- `member` - Foreign key to Member
- `date` - Attendance date
- `status` - Present/Absent
- `service_type` - Type of service (e.g., Sunday Service)
- `marked_by` - User who marked the attendance

### Announcement
- `title` - Announcement title
- `message` - Announcement content
- `date_posted` - Date and time posted
- `posted_by` - User who posted
- `is_active` - Whether announcement is active

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
