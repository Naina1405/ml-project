import sqlite3
import datetime
from pathlib import Path
from config.settings import settings

class NativeDBConnection:
    def __init__(self, db_path: Path):
        self.db_path = str(db_path)

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            goal_prompt TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_steps (
            step_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            step_number INTEGER NOT NULL,
            action TEXT NOT NULL,
            tool_used TEXT,
            tool_input TEXT,
            tool_output TEXT,
            status TEXT NOT NULL DEFAULT 'EXECUTING',
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            memory_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            memory_type TEXT NOT NULL DEFAULT 'preference',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        conn.commit()
        conn.close()

native_db = NativeDBConnection(settings.DB_PATH)

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base
    
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_db():
        import db.models
        Base.metadata.create_all(bind=engine)
        native_db.init_tables()

except ImportError:
    # Native SQLite fallback when SQLAlchemy is absent
    engine = None
    Base = object
    SessionLocal = None
    get_db = None
    
    def init_db():
        native_db.init_tables()
