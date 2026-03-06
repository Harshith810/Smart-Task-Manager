from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os

# -----------------------
# Logging Setup
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

app = Flask(__name__)
CORS(app)

# MySQL Configuration

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("postgresql://harshu:BXl2cZAhRYNHVQLCk5CVFKfsFlEjCyYe@dpg-d6l79hrh46gs73dlpslg-a/smart_task_manager_4w8t")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------
# Task Model
# -----------------------
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(255),
        nullable=False
    )

    deadline = db.Column(
        db.DateTime,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    completed_at = db.Column(
        db.DateTime,
        nullable=True
    )

    status = db.Column(
        db.Enum('pending', 'completed', 'missed'),
        nullable=False,
        default='pending'
    )

    reschedule_count = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "deadline": self.deadline,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "reschedule_count": self.reschedule_count
        }

# -----------------------
# Create Tables
# -----------------------
with app.app_context():
    db.create_all()

# -----------------------
# Routes
# -----------------------

@app.route("/")
def home():
    return "Backend is working!"

@app.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    logging.info("Fetched all tasks")
    return jsonify([task.to_dict() for task in tasks])


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.json

    task = Task(
        title=data["title"],
        deadline=datetime.fromisoformat(data["deadline"])
    )

    db.session.add(task)
    db.session.commit()

    logging.info(f"Task created | id={task.id} | title='{task.title}' | deadline={task.deadline}")

    return jsonify(task.to_dict()), 201


@app.route("/tasks/<int:id>/complete", methods=["PATCH"])
def complete_task(id):

    task = Task.query.get(id)

    if not task:
        logging.warning(f"Task completion failed | id={id} not found")
        return {"error": "Task not found"}, 404

    if task.status == "completed":
        logging.warning(f"Task already completed | id={id}")
        return {"error": "Task already completed"}, 409

    task.status = "completed"
    task.completed_at = datetime.utcnow()

    db.session.commit()

    logging.info(f"Task completed | id={task.id}")

    return jsonify(task.to_dict())


@app.route("/tasks/<int:id>", methods=["DELETE"])
def delete_task(id):

    task = Task.query.get(id)

    if not task:
        logging.warning(f"Delete failed | task id={id} not found")
        return {"error": "Task not found"}, 404

    db.session.delete(task)
    db.session.commit()

    logging.info(f"Task deleted | id={id}")

    return {"message": "Task deleted"}

# -----------------------
# Productivity Analytics
# -----------------------

@app.route("/analytics", methods=["GET"])
def get_analytics():

    total_tasks = Task.query.count()

    completed_tasks = Task.query.filter_by(status="completed").count()

    pending_tasks = Task.query.filter_by(status="pending").count()

    total_reschedules = db.session.query(
        db.func.sum(Task.reschedule_count)
    ).scalar() or 0

    if total_tasks > 0:
        completion_rate = (completed_tasks / total_tasks) * 100
    else:
        completion_rate = 0

    logging.info("Analytics calculated")

    return jsonify({
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "completion_rate": f"{completion_rate:.2f}%",
        "total_reschedules": total_reschedules
    })


# -----------------------
# Adaptive Rescheduling Engine
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

            task.status = "pending"

        db.session.commit()

        logging.info(f"Scheduler executed | rescheduled_tasks={len(missed_tasks)}")


# -----------------------
# Start Scheduler
# -----------------------

scheduler = BackgroundScheduler()
scheduler.add_job(reschedule_missed_tasks, "interval", minutes=5)
scheduler.start()


if __name__ == "__main__":
    logging.info("Smart Task Manager backend started")

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)