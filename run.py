"""
run.py — Master CLI Launcher for the Autonomous Personal Task Agent
===================================================================

Usage
-----
  python run.py --ui      Start the Streamlit frontend (http://localhost:8501)
  python run.py --api     Start the FastAPI backend  (http://localhost:8000)
  python run.py --test    Run the automated test suite
  python run.py --train   Generate dataset and train ML intent classifiers
  python run.py --eval    Run benchmark evaluation & research experiments
  python run.py --all     Start both API and UI simultaneously
"""

import argparse
import subprocess
import sys
import time
import logging
from threading import Thread

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║    🤖  Autonomous Personal Task Agent  v2.0.0               ║
║    LangGraph · ChromaDB · FastAPI · Streamlit                ║
╚══════════════════════════════════════════════════════════════╝
"""


def _run_ui():
    logger.info("Starting Streamlit UI → http://localhost:8501")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "ui/app.py",
         "--server.port", "8501",
         "--server.headless", "false"],
        check=False,
    )


def _run_api():
    logger.info("Starting FastAPI backend → http://localhost:8000")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "api.main:app",
         "--port", "8000",
         "--reload",
         "--log-level", "info"],
        check=False,
    )


def main():
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="Autonomous Personal Task Agent Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--api",   action="store_true", help="Start FastAPI backend server")
    parser.add_argument("--ui",    action="store_true", help="Start Streamlit frontend UI")
    parser.add_argument("--all",   action="store_true", help="Start both API and UI")
    parser.add_argument("--test",  action="store_true", help="Run the full test suite")
    parser.add_argument("--train", action="store_true", help="Generate dataset and train ML models")
    parser.add_argument("--eval",  action="store_true", help="Run benchmark evaluation & research experiments")

    args = parser.parse_args()

    if args.train:
        logger.info("Starting dataset generation and model training …")
        from data.dataset_generator import generate_dataset
        from data.clean_dataset import clean_dataset
        from data.split_dataset import split_dataset
        from models.train import train_models
        generate_dataset()
        clean_dataset()
        split_dataset()
        train_models()

    elif args.test:
        logger.info("Executing automated test suite …")
        from run_tests import run_all_tests
        run_all_tests()

    elif args.eval:
        logger.info("Executing evaluation benchmark and research experiments …")
        from evaluation.run_experiments import run_all_experiments
        run_all_experiments()

    elif args.all:
        logger.info("Launching API and UI concurrently …")
        api_thread = Thread(target=_run_api, daemon=True)
        api_thread.start()
        time.sleep(2)  # Give API a head start
        _run_ui()

    elif args.api:
        _run_api()

    elif args.ui:
        _run_ui()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
