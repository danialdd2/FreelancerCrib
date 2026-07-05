readme



# FreelancerCrib

A RESTful Freelancer Marketplace API built with **FastAPI**.  
This project allows clients to create projects, freelancers to submit bids, clients to accept bids, complete projects, rate freelancers, receive notifications, and manage users.

---

## Features

### Authentication
- JWT Authentication
- Login with OAuth2 Password Flow
- Password hashing using bcrypt

### Users
- Register new users
- Update profile
- View profile
- View public user information

### Projects
- Create project
- Edit project
- List all projects
- Search projects
- Filter projects by status
- Accept freelancer bids
- Complete projects
- Cancel projects

### Bids
- Submit bid
- View project bids
- View own bids
- Update bid
- Delete bid

### Ratings
- Rate completed projects
- One rating per project per user

### Notifications
- Get notifications
- Read notification
- Read all notifications
- Delete notification
- Unread notifications count

### Dashboard
#### Client Dashboard
- Total projects
- Open projects
- Active projects
- Completed projects
- Total received bids
- Average rating

#### Freelancer Dashboard
- Total bids
- Pending bids
- Won projects
- Active projects
- Completed projects
- Average rating

### Admin
- View all users
- Promote user to admin
- View all admins

---

# Tech Stack

- Python 3
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT Authentication
- Passlib (bcrypt)
- Pytest

---

# Project Structure

```
app/
│
├── routers/
│   ├── users.py
│   ├── projects.py
│   ├── bids.py
│   ├── ratings.py
│   ├── notification.py
│   ├── dashboard.py
│   └── admins.py
│
├── auth.py
├── config.py
├── database.py
├── dependencies.py
├── enums.py
├── models.py
├── schemas.py
├── main.py
│
└── tests/
```

---

## API Docs

https://freelancercrib-production.up.railway.app/docs

## Run Locally

```bash
git clone https://github.com/danialdd2/FreelancerCrib.git
cd FreelancerCrib
pip install -r requirements.txt
uvicorn app.main:app --reload
```
> **Note:** The application uses **PostgreSQL** by default. The test suite is configured to use **SQLite**, so minor configuration changes may be required before running the tests.

## License

This project was created for learning and portfolio purposes.