from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
import bcrypt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = Flask(__name__)
CORS(app)

# -----------------------
# Database Configuration
# -----------------------

database_url = os.environ.get("DATABASE_URL")

if database_url is None:
    raise RuntimeError("DATABASE_URL is not set")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# -----------------------
# Task Model
# -----------------------

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    status = db.Column(
        db.Enum("pending", "completed", "missed", name="task_status"),
        nullable=False,
        default="pending"
    )

    reschedule_count = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "deadline": self.deadline.isoformat(),
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status,
            "reschedule_count": self.reschedule_count
        }

with app.app_context():
    db.create_all()

@app.route("/register", methods=["POST"])
def register():

    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "Email and password required"}, 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return {"error": "User already exists"}, 409

    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    user = User(
        email=email,
        password=hashed_password
    )

    db.session.add(user)
    db.session.commit()

    return {"message": "User registered successfully"}

@app.route("/login", methods=["POST"])
def login():

    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        return {"error": "Invalid credentials"}, 401

    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return {"error": "Invalid credentials"}, 401

    return {"user_id": user.id}

# -----------------------
# Routes
# -----------------------

@app.route("/")
def home():
    return "Smart Task Manager Backend Running 🚀"

@app.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id")
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json

    task = Task(
        title=data["title"],
        deadline=datetime.fromisoformat(data["deadline"]),
        user_id=data["user_id"]
    )

    db.session.add(task)
    db.session.commit()

    return jsonify(task.to_dict()), 201

@app.route("/tasks/<int:id>/complete", methods=["PATCH"])
def complete_task(id):

    task = Task.query.get(id)

    if not task:
        return {"error": "Task not found"}, 404

    if task.status == "completed":
        return {"error": "Task already completed"}, 409

    task.status = "completed"
    task.completed_at = datetime.utcnow()

    db.session.commit()

    return jsonify(task.to_dict())

@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):

    task = Task.query.get(id)

    if not task:
        return {"error": "Task not found"}, 404

    db.session.delete(task)
    db.session.commit()

    return {"message": "Task deleted"}

# -----------------------
# Analytics
# -----------------------

@app.route("/analytics", methods=["GET"])
def get_analytics():

    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter_by(status="completed").count()
    pending_tasks = Task.query.filter_by(status="pending").count()

    total_reschedules = db.session.query(
        db.func.sum(Task.reschedule_count)
    ).scalar() or 0

    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks else 0

    return jsonify({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": f"{completion_rate:.2f}%",
        "total_reschedules": total_reschedules
    })

# -----------------------
# Scheduler
# -----------------------

def reschedule_missed_tasks():

    with app.app_context():

        now = datetime.utcnow()

        missed_tasks = Task.query.filter(
            Task.status == "pending",
            Task.deadline < now
        ).all()

        for task in missed_tasks:
            task.deadline = now + timedelta(hours=24)
            task.reschedule_count += 1

        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(reschedule_missed_tasks, "interval", minutes=5)
scheduler.start()

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)