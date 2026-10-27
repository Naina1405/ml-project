import json
import random
from pathlib import Path
from config.settings import settings

INTENTS = [
    "create_task", "update_task", "delete_task",
    "create_reminder", "cancel_task",
    "search_information", "summarize_information", "compare_information",
    "create_calendar_event", "send_email",
    "retrieve_memory", "save_memory",
    "multi_step_task", "conditional_task", "unknown_request"
]

TOOL_MAPPING = {
    "create_task": ["task_manager"],
    "update_task": ["task_manager"],
    "delete_task": ["task_manager"],
    "create_reminder": ["scheduler"],
    "cancel_task": ["scheduler"],
    "search_information": ["web_search"],
    "summarize_information": ["web_search"],
    "compare_information": ["web_search"],
    "create_calendar_event": ["calendar"],
    "send_email": ["email"],
    "retrieve_memory": ["memory"],
    "save_memory": ["memory"],
    "multi_step_task": ["web_search", "memory", "scheduler"],
    "conditional_task": ["web_search", "scheduler"],
    "unknown_request": []
}

TEMPLATES = {
    "create_task": [
        "Add '{task}' to my task list",
        "Create a new task to {task} by {time}",
        "I need a task created: {task}",
        "Track this task for me: {task}",
        "Put '{task}' on my TODO list with priority {priority}"
    ],
    "update_task": [
        "Mark task {task_id} as completed",
        "Update the status of task '{task}' to high priority",
        "Change deadline of task {task_id} to tomorrow",
        "Set task {task_id} as done",
        "Update task '{task}' to in progress"
    ],
    "delete_task": [
        "Delete task {task_id} from my list",
        "Remove the task '{task}'",
        "Clear task {task_id}",
        "Erase task '{task}' from my database",
        "Get rid of task {task_id}"
    ],
    "create_reminder": [
        "Remind me to {task} tomorrow at {time}",
        "Set a reminder for {task} at {time}",
        "Don't let me forget to {task} on {day}",
        "Notify me at {time} to {task}",
        "Schedule a reminder: {task} at {time}"
    ],
    "cancel_task": [
        "Cancel my reminder for {task}",
        "Remove the reminder scheduled for {time}",
        "Delete reminder {task_id}",
        "Cancel the notification for {task}"
    ],
    "search_information": [
        "Find information about {topic}",
        "Search the web for {topic}",
        "Look up top courses for {topic}",
        "Search online for latest news on {topic}",
        "What are the best resources to learn {topic}?"
    ],
    "summarize_information": [
        "Summarize recent articles about {topic}",
        "Give me a short summary of {topic}",
        "Provide a quick brief on {topic}",
        "Summarize the key points of {topic}"
    ],
    "compare_information": [
        "Find 3 good {topic} courses and compare their prices",
        "Compare top 3 options for {topic}",
        "Search for {topic} tools and compare their features",
        "Which is better: {topic} option A or option B?"
    ],
    "create_calendar_event": [
        "Schedule a meeting with {person} tomorrow at {time}",
        "Add event '{task}' to my calendar for {day} at {time}",
        "Create a calendar event for {task} on {day}",
        "Book a time slot for {task} at {time}"
    ],
    "send_email": [
        "Send an email to {person} with subject '{subject}'",
        "Email {person} about {subject}",
        "Draft and send an email to {email_addr} regarding {subject}",
        "Send this update report to my professor at {email_addr}"
    ],
    "retrieve_memory": [
        "What are my saved preferences for {topic}?",
        "Recall what I noted about {topic}",
        "Search my memory for {topic}",
        "Do I prefer morning or evening reminders?"
    ],
    "save_memory": [
        "Remember that I prefer {preference} for {topic}",
        "Save to my memory: I like {preference}",
        "Note down that my preferred email style is {preference}",
        "Save this preference: {preference}"
    ],
    "multi_step_task": [
        "Find 3 good {topic} courses, compare them, save the best one to my notes, and remind me tomorrow to enroll",
        "Search for top {topic} tutorials, summarize the best one, and draft an email to {person} about it",
        "Research {topic}, save my favorite option to memory, and schedule a calendar event for next week",
        "Look up {topic} prices, select the cheapest, save it, and notify me tomorrow"
    ],
    "conditional_task": [
        "If tomorrow's weather has rain, remind me to carry an umbrella",
        "Check if {topic} price drops below $50 and notify me",
        "If my email from {person} arrives, alert me immediately",
        "Search for {topic} updates and if found, save them to my notes"
    ],
    "unknown_request": [
        "Blah blah random nonsense 12345",
        "Asdffghjkl zxcvbnm",
        "Can you do a backflip?",
        "What is the airspeed velocity of an unladen swallow?"
    ]
}

TOPICS = ["Machine Learning", "Python Programming", "SQL Database", "Deep Learning", "FastAPI Web Apps", "React UI", "Data Engineering", "Cloud Computing"]
TASKS = ["submit assignment", "review pull request", "buy groceries", "pay electric bill", "call doctor", "finish project report"]
PERSONS = ["Professor Smith", "Manager John", "Team Lead Sarah", "Alex", "Dr. Davis"]
PREFERENCES = ["concise emails", "morning reminders", "Python based courses", "dark mode UI", "detailed markdown notes"]
TIMES = ["9:00 AM", "2:30 PM", "10:00 AM", "4:00 PM", "8:00 PM"]
DAYS = ["Monday", "Tuesday", "Friday", "tomorrow", "next week"]
PRIORITIES = ["high", "normal", "low"]

def generate_sample(sample_id: int) -> dict:
    intent = random.choice(INTENTS)
    tmpl = random.choice(TEMPLATES[intent])
    
    prompt = tmpl.format(
        topic=random.choice(TOPICS),
        task=random.choice(TASKS),
        person=random.choice(PERSONS),
        preference=random.choice(PREFERENCES),
        time=random.choice(TIMES),
        day=random.choice(DAYS),
        priority=random.choice(PRIORITIES),
        task_id=f"TSK-{random.randint(100, 999)}",
        subject="Project Progress Update",
        email_addr="prof.smith@university.edu"
    )
    
    tools = TOOL_MAPPING[intent]
    requires_approval = (intent == "send_email") or ("email" in tools and intent in ["multi_step_task", "send_email"])
    
    difficulty = "simple"
    if intent in ["multi_step_task", "conditional_task"]:
        difficulty = "complex"
    elif intent in ["compare_information", "summarize_information"]:
        difficulty = "medium"

    return {
        "task_id": f"GEN-{sample_id:04d}",
        "user_prompt": prompt,
        "intent": intent,
        "required_tools": tools,
        "requires_approval": requires_approval,
        "difficulty": difficulty,
        "expected_output": f"Successfully handled intent '{intent}' with tools {tools}"
    }

def generate_dataset(num_samples: int = 1500, output_file: str = "dataset_raw.json"):
    data = []
    for i in range(1, num_samples + 1):
        data.append(generate_sample(i))
    
    out_path = settings.DATA_DIR / output_file
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[Dataset Generator] Successfully generated {len(data)} dataset samples at: {out_path}")

if __name__ == "__main__":
    generate_dataset()
