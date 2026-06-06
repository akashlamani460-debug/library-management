# College Admission Website

A comprehensive Flask-based college admission portal that allows students to apply for college programs and administrators to manage applications.

## Features

### Student Features
- User registration and authentication
- Comprehensive application form with personal, academic, and address information
- Document upload (PDF, DOC, DOCX, JPG, PNG)
- Real-time application status tracking
- Application history and management

### Admin Features
- Dashboard with statistics (total applications, pending, approved, rejected)
- Application review and management
- Status update functionality
- Program management
- Applicant notifications

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: Bootstrap 5, HTML5, CSS3
- **Authentication**: Werkzeug security utilities

## Installation

1. Clone the repository:
```bash
git clone https://github.com/akashlamani460-debug/library-management.git
cd library-management
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## Usage

### Student Registration
1. Click "Get Started" on the home page
2. Enter your details and create an account
3. Log in with your credentials

### Submitting an Application
1. Click "Apply Now" from the dashboard
2. Fill out the application form with your personal and academic information
3. Upload required documents
4. Submit the application

### Admin Access
1. Create an admin account or modify user role in the database
2. Log in as admin
3. Access the admin dashboard to view all applications
4. Review applications and update status
5. Manage programs and view statistics

## Database Schema

### Users Table
- id: Integer (Primary Key)
- email: String (Unique)
- password: String (Hashed)
- full_name: String
- role: String (student/admin)
- created_at: Timestamp

### Applications Table
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- full_name: String
- dob: String
- gender: String
- phone: String
- address: String
- city: String
- state: String
- zip_code: String
- country: String
- email: String
- program: String
- academic_year: String
- gpa: Float
- entrance_exam_score: String
- extracurricular: String
- essay: String
- status: String (pending/approved/rejected)
- applied_at: Timestamp
- updated_at: Timestamp

### Documents Table
- id: Integer (Primary Key)
- application_id: Integer (Foreign Key)
- document_type: String
- file_path: String
- uploaded_at: Timestamp

### Programs Table
- id: Integer (Primary Key)
- name: String
- description: String
- duration: String
- seats: Integer
- created_at: Timestamp

## File Structure

```
library-management/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── admission.db                    # SQLite database (auto-created)
├── uploads/                        # Document uploads folder
└── templates/
    ├── base.html                   # Base template
    ├── index.html                  # Home page
    ├── register.html               # Registration page
    ├── login.html                  # Login page
    ├── student_dashboard.html      # Student dashboard
    ├── admin_dashboard.html        # Admin dashboard
    ├── application_form.html       # Application form
    ├── view_application.html       # View application details
    ├── manage_programs.html        # Program management
    ├── 404.html                    # 404 error page
    └── 500.html                    # 500 error page
```

## Security Notes

⚠️ **Important**: This is a demonstration project. For production deployment:

1. Change the secret key in `app.py`
2. Use a more robust database (PostgreSQL, MySQL)
3. Implement HTTPS/SSL
4. Add rate limiting
5. Implement CSRF protection
6. Add email verification
7. Use environment variables for sensitive data
8. Implement proper logging

## Contributing

Feel free to fork this project and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Contact

For questions or issues, please create an issue in the repository.
