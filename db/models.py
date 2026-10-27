import datetime
import uuid

try:
    from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, JSON
    from sqlalchemy.orm import relationship
    from db.database import Base

    def generate_uuid():
        return str(uuid.uuid4())

    class User(Base):
        __tablename__ = "users"
        
        user_id = Column(String, primary_key=True, default=generate_uuid)
        name = Column(String, nullable=False, default="Default User")
        created_at = Column(DateTime, default=datetime.datetime.utcnow)

        tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
        memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")

    class Task(Base):
        __tablename__ = "tasks"

        task_id = Column(String, primary_key=True, default=generate_uuid)
        user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
        goal_prompt = Column(Text, nullable=False)
        status = Column(String, nullable=False, default="PENDING")
        created_at = Column(DateTime, default=datetime.datetime.utcnow)
        completed_at = Column(DateTime, nullable=True)

        user = relationship("User", back_populates="tasks")
        steps = relationship("TaskStep", back_populates="task", cascade="all, delete-orphan", order_by="TaskStep.step_number")

    class TaskStep(Base):
        __tablename__ = "task_steps"

        step_id = Column(String, primary_key=True, default=generate_uuid)
        task_id = Column(String, ForeignKey("tasks.task_id"), nullable=False)
        step_number = Column(Integer, nullable=False)
        action = Column(String, nullable=False)
        tool_used = Column(String, nullable=True)
        tool_input = Column(JSON, nullable=True)
        tool_output = Column(JSON, nullable=True)
        status = Column(String, nullable=False, default="EXECUTING")
        error_message = Column(Text, nullable=True)
        created_at = Column(DateTime, default=datetime.datetime.utcnow)

        task = relationship("Task", back_populates="steps")

    class Memory(Base):
        __tablename__ = "memories"

        memory_id = Column(String, primary_key=True, default=generate_uuid)
        user_id = Column(String, ForeignKey("users.user_id"), nullable=False)
        content = Column(Text, nullable=False)
        memory_type = Column(String, nullable=False, default="preference")
        created_at = Column(DateTime, default=datetime.datetime.utcnow)

        user = relationship("User", back_populates="memories")

except ImportError:
    User = None
    Task = None
    TaskStep = None
    Memory = None
