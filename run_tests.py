import traceback
from tests.test_tools import (
    test_web_search_tool, test_task_manager_tool, test_scheduler_tool,
    test_calendar_tool, test_email_tool, test_memory_tool
)
from tests.test_agent import test_agent_simple_flow, test_agent_sensitive_action_approval
from tests.test_ml import test_baseline_ml_classifier

def run_all_tests():
    tests = [
        ("Web Search Tool", test_web_search_tool),
        ("Task Manager Tool", test_task_manager_tool),
        ("Scheduler Tool", test_scheduler_tool),
        ("Calendar Tool", test_calendar_tool),
        ("Email Tool", test_email_tool),
        ("Memory Tool", test_memory_tool),
        ("Agent Simple Flow Integration", test_agent_simple_flow),
        ("Agent Human Approval Integration", test_agent_sensitive_action_approval),
        ("ML Intent Classifier Baseline", test_baseline_ml_classifier)
    ]

    print("==================================================")
    print("        AUTONOMOUS AGENT SUITE VERIFICATION       ")
    print("==================================================")
    passed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            print(f"  [PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            traceback.print_exc()

    print("==================================================")
    print(f"Test Summary: {passed}/{len(tests)} tests passed successfully.")
    print("==================================================")

if __name__ == "__main__":
    run_all_tests()
