# 🗃️ Flask File Upload & User Management System

A simple Flask-based web application for user-based file uploads, admin control, and role management. Users can upload, download, and delete files. Admins can manage users and access all uploads.

## 🚀 Features

- 🔐 Login/Logout functionality
- 👤 User and Admin roles
- 📤 File upload (by user)
- 🗂 Admin panel to manage all users and files
- 🧾 Create, update, and delete users
- 📦 Download multiple files as ZIP
- 🧹 Filter files by name, type, and date

file_upload_portal/
│
├── app.py               # Main Flask app
├── auth.py              # Auth logic (login, roles, CRUD users)
├── database.py          # DB initialization
├── users.db             # SQLite DB (auto-generated)
│
├── templates/           # HTML templates (Jinja2)
│   ├── login.html
│   ├── upload.html
│   ├── admin.html
│   ├── create_user.html
│   └── edit_user.html
│
├── uploads/             # Uploaded user files
├── venv/                # (Optional) Python virtual environment
├── requirements.txt     # Python dependencies
└── README.md            # You are here!

## ⚙️ Setup Instructions

### 🔧 Local Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Adrian-Manongdo/file_upload_portal.git
   cd file_upload_portal

2. (Optional but recommended) Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install the dependencies:

pip install -r requirements.txt

4. Run the Flask server:

python app.py

5. Open your browser and go to:

http://127.0.0.1:5000/



🧪 Default Admin Credentials

When you first run the app, it auto-generates an admin user:

    Username: admin

    Password: admin123

    Change this as soon as possible in production use.


📸 Admin Dashboard Preview

    Features like:

    Filter by user, date, filename

    Upload for any user

    Delete individual or all files

    Pagination

    Role management


🧰 Tech Stack

    Python

    Flask

    SQLite

    Bootstrap 5

    HTML/CSS/Jinja2


📄 License

This project is licensed under the [MIT License](LICENSE).


🙌 Acknowledgments

Created by Adrian Manongdo. Inspired by real-world file handling use cases.
