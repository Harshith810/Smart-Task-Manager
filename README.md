<<<<<<< HEAD
# Smart Task Manager

### Adaptive Rescheduling & Productivity Analytics

Smart Task Manager is a backend-driven productivity system that helps
users organize tasks efficiently. Unlike traditional to‑do applications,
this system introduces **automatic task rescheduling** and
**productivity analytics** to help users understand their work patterns.

------------------------------------------------------------------------

# Project Overview

The Smart Task Manager backend provides:

-   REST APIs for task management
-   Automatic rescheduling for missed deadlines
-   Productivity analytics based on task data
-   Background job automation

The system is built using **Flask, MySQL, SQLAlchemy, and APScheduler**.

------------------------------------------------------------------------

# Key Features

## Task Creation

Users can create tasks with a title and deadline.

## Task Retrieval

Retrieve all tasks or specific tasks through REST APIs.

## Task Status Tracking

Each task can have one of the following statuses:

-   pending
-   completed
-   missed

## Adaptive Rescheduling

If a task deadline passes without completion, the system automatically
reschedules it to a new future deadline.

## Productivity Analytics

The system generates insights such as:

-   total tasks
-   completion rate
-   missed tasks
-   average delay
-   peak productivity hour

------------------------------------------------------------------------

# Technology Stack

  Layer               Technology
  ------------------- -----------------------
  Backend             Python Flask
  Database            MySQL
  ORM                 Flask-SQLAlchemy
  DB Connector        PyMySQL
  Scheduler           APScheduler
  Environment         python-dotenv
  Frontend (Future)   HTML, CSS, JavaScript
  Charts              Chart.js

------------------------------------------------------------------------

# System Architecture

The application follows a **three-tier architecture**:

Client Layer\
REST API consumers such as Postman or frontend applications.

Application Layer\
Flask backend responsible for business logic and API routing.

Data Layer\
MySQL database accessed through SQLAlchemy ORM.

A background scheduler continuously checks for missed tasks and
reschedules them.

------------------------------------------------------------------------

# Project Structure

    smart_task_manager/
    │
    ├── app/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── routes/
    │   │   ├── tasks.py
    │   │   └── analytics.py
    │   ├── services/
    │   │   ├── task_service.py
    │   │   ├── analytics_service.py
    │   │   └── scheduler_service.py
    │   └── utils/
    │       └── validators.py
    │
    ├── tests/
    ├── config.py
    ├── run.py
    ├── requirements.txt
    └── README.md

------------------------------------------------------------------------

# Database Schema

tasks table

  Column             Description
  ------------------ ------------------------------
  id                 unique identifier
  title              task name
  deadline           deadline timestamp
  created_at         task creation time
  completed_at       task completion time
  status             pending / completed / missed
  reschedule_count   number of reschedules

------------------------------------------------------------------------

# API Endpoints

## Create Task

POST /api/v1/tasks

Example:

``` json
{
"title": "Finish project report",
"deadline": "2026-03-10T18:00:00"
}
```

## Get All Tasks

GET /api/v1/tasks

## Get Single Task

GET /api/v1/tasks/{id}

## Complete Task

PATCH /api/v1/tasks/{id}/complete

## Productivity Analytics

GET /api/v1/analytics

------------------------------------------------------------------------

# Installation

## Clone Repository

    git clone https://github.com/yourusername/smart-task-manager.git
    cd smart-task-manager

## Create Virtual Environment

    python -m venv venv

Activate

Windows

    venv\Scripts\activate

Linux / Mac

    source venv/bin/activate

## Install Dependencies

    pip install -r requirements.txt

## Run Application

    python run.py

Server runs at

    http://localhost:5000

------------------------------------------------------------------------

# Future Enhancements

-   User authentication
-   Multi-user support
-   ML based task priority prediction
-   Mobile application
-   Calendar integrations
-   Email notifications

------------------------------------------------------------------------

# License

MIT License
=======
# Smart-Task-Manager
>>>>>>> c05c5611a0daff528efc66873589cad24e23d4e8
