import json
import uuid
import datetime
from typing import Optional, List, Dict, Any
from db.database import native_db, SessionLocal

def db_init():
    native_db.init_tables()
    try:
        from db.database import init_db
        init_db()
    except Exception:
        pass

def db_create_task(user_id: str, goal_prompt: str, task_id: Optional[str] = None, status: str = "PENDING") -> Dict[str, Any]:
    db_init()
    tid = task_id or str(uuid.uuid4())[:8]
    conn = native_db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (task_id, user_id, goal_prompt, status) VALUES (?, ?, ?, ?)",
        (tid, user_id, goal_prompt, status)
    )
    conn.commit()
    conn.close()
    return {"task_id": tid, "user_id": user_id, "goal_prompt": goal_prompt, "status": status}

def db_update_task_status(task_id: str, status: str) -> bool:
    conn = native_db.get_connection()
    cursor = conn.cursor()
    comp_at = str(datetime.datetime.utcnow()) if status in ["COMPLETED", "FAILED"] else None
    cursor.execute(
        "UPDATE tasks SET status = ?, completed_at = ? WHERE task_id = ?",
        (status, comp_at, task_id)
    )
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

def db_list_tasks(user_id: str = "user_default") -> List[Dict[str, Any]]:
    db_init()
    conn = native_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_delete_task(task_id: str) -> bool:
    conn = native_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

def db_create_step(task_id: str, step_number: int, action: str, tool_used: Optional[str], 
                   tool_input: Optional[dict], tool_output: Optional[dict], 
                   status: str = "SUCCESS", error_message: Optional[str] = None) -> str:
    db_init()
    sid = str(uuid.uuid4())[:8]
    conn = native_db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO task_steps (step_id, task_id, step_number, action, tool_used, tool_input, tool_output, status, error_message)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (sid, task_id, step_number, action, tool_used, json.dumps(tool_input or {}), json.dumps(tool_output or {}), status, error_message)
    )
    conn.commit()
    conn.close()
    return sid

def db_add_memory(user_id: str, content: str, memory_type: str = "preference") -> str:
    db_init()
    mid = str(uuid.uuid4())[:8]
    conn = native_db.get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO memories (memory_id, user_id, content, memory_type) VALUES (?, ?, ?, ?)",
        (mid, user_id, content, memory_type)
    )
    conn.commit()
    conn.close()
    return mid

def db_list_memories(user_id: str = "user_default") -> List[Dict[str, Any]]:
    db_init()
    conn = native_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memories WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_delete_memory(memory_id: str) -> bool:
    conn = native_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0
