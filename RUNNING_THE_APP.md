# Digital Facial Recognition Attendance System - 3FA Setup

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/mukeshsardiwal/Desktop/Digital-Facial-Recognisation-Attendance-System
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app_auth.py
```

The app will start on `http://localhost:5000`

### 3. Access the System

- **Homepage**: http://localhost:5000/
- **Login**: http://localhost:5000/login
- **Register**: http://localhost:5000/register
- **Dashboard**: http://localhost:5000/dashboard (after login)

## Database

The system uses **SQLite** with the following tables:

1. **users** - User accounts with 3FA settings
2. **students** - Student records with facial embeddings
3. **attendance** - Attendance records
4. **login_history** - Login attempts and logs
5. **otp_attempts** - OTP verification records
6. **sessions** - Active sessions
7. **audit_logs** - Audit trail

Database file: `facial_attendance.db`

## API Endpoints

### Authentication API

#### Register User

```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe"
}
```

#### Login Step 1: Verify Username/Password

```bash
POST /api/auth/step1
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

Response:

```json
{
  "user_id": 1,
  "message": "OTP sent to your email"
}
```

#### Login Step 2: Verify OTP

```bash
POST /api/auth/step2
Content-Type: application/json

{
  "user_id": 1,
  "otp_code": "123456"
}
```

Response:

```json
{
  "user_id": 1,
  "message": "OTP verified. Proceed to facial recognition"
}
```

#### Login Step 3: Verify Facial Recognition

```bash
POST /api/auth/step3
Content-Type: application/json

{
  "user_id": 1,
  "facial_embedding": [0.1, 0.2, ...] // 128-D embedding
}
```

Response:

```json
{
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "username": "john_doe",
    "full_name": "John Doe"
  }
}
```

#### Logout

```bash
POST /api/auth/logout
Authorization: Bearer <token>
```

## Testing

### Test Registration via cURL

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Password123!",
    "full_name": "Test User"
  }'
```

### Test Registration via Python

```bash
python test_register.py
```

## Troubleshooting

### Port 5000 Already in Use

```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or use a different port
python app_auth.py --port 5001
```

### Database Issues

```bash
# Reset database
rm facial_attendance.db

# Reinitialize
python -c "from database import db; db.init_db()"
```

### Missing Dependencies

```bash
pip install --upgrade -r requirements.txt
```

## Features

✅ **3-Factor Authentication**

- Username/Password
- OTP via Email
- Facial Recognition

✅ **User Management**

- Register new users
- Manage facial data
- Session tracking

✅ **Attendance Tracking**

- Mark attendance via facial recognition
- Attendance history
- Reports

✅ **Security**

- Password hashing with bcrypt
- JWT tokens
- Session management
- Audit logging

## Configuration

Edit `.env` file for custom settings:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Production Deployment

For production, ensure:

1. Set `DEBUG=False` in `.env`
2. Generate strong `SECRET_KEY`
3. Use environment variables for sensitive data
4. Set up HTTPS/SSL
5. Configure CORS properly
6. Use production WSGI server (gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_auth:app
```

## Support

For issues or questions, check:

- `DOCUMENTATION_INDEX.md` - Complete documentation
- `QUICKSTART.md` - Quick setup guide
- `3FA_SETUP_GUIDE.md` - Detailed 3FA setup
