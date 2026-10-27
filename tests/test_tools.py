from tools.web_search import WebSearchTool
from tools.task_manager import TaskManagerTool
from tools.scheduler import SchedulerTool
from tools.calendar_tool import CalendarTool
from tools.email_tool import EmailTool
from tools.memory_tool import MemoryTool

def test_web_search_tool():
    tool = WebSearchTool()
    res = tool.execute(query="machine learning courses", num_results=2)
    assert res.success is True
    assert "results" in res.data
    assert len(res.data["results"]) > 0

def test_task_manager_tool():
    tool = TaskManagerTool()
    res = tool.execute(action="create", title="Test task creation", user_id="test_user")
    assert res.success is True
    task_id = res.data["task_id"]
    
    list_res = tool.execute(action="list", user_id="test_user")
    assert list_res.success is True
    assert list_res.data["count"] > 0

    del_res = tool.execute(action="delete", task_id=task_id)
    assert del_res.success is True

def test_scheduler_tool():
    tool = SchedulerTool()
    res = tool.execute(action="create", message="Review ML notes")
    assert res.success is True
    rem_id = res.data["reminder_id"]
    
    cancel_res = tool.execute(action="cancel", reminder_id=rem_id)
    assert cancel_res.success is True

def test_calendar_tool():
    tool = CalendarTool()
    res = tool.execute(action="create", title="Team Sync Meeting")
    assert res.success is True
    eid = res.data["event"]["event_id"]
    
    del_res = tool.execute(action="delete", event_id=eid)
    assert del_res.success is True

def test_email_tool():
    tool = EmailTool()
    draft_res = tool.execute(action="draft", recipient="prof@edu.com", subject="Test", body="Hello")
    assert draft_res.success is True
    assert tool.requires_approval is True

def test_memory_tool():
    tool = MemoryTool()
    save_res = tool.execute(action="save", content="User prefers python", user_id="test_user")
    assert save_res.success is True
    mid = save_res.data["memory_id"]
    
    ret_res = tool.execute(action="retrieve", content="python", user_id="test_user")
    assert ret_res.success is True
    
    del_res = tool.execute(action="delete", memory_id=mid)
    assert del_res.success is True
