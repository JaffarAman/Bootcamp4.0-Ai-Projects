import subprocess
import sys
import os
import time
import signal

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT, "backend")
FRONTEND_DIR = os.path.join(ROOT, "frontend")

processes = []

def cleanup(signum=None, frame=None):
    print("\n[STOP] Shutting down all services...")
    for p in processes:
        try:
            p.terminate()
            p.wait(timeout=5)
        except Exception:
            p.kill()
    print("[DONE] All services stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

if __name__ == "__main__":
    print("=" * 50)
    print("  Finance Agent - Starting All Services")
    print("=" * 50)

    # Start FastAPI backend
    print("\n[1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND_DIR
    )
    processes.append(backend)
    time.sleep(3)

    # Start Streamlit frontend
    print("[2/2] Starting Streamlit frontend on http://localhost:8501 ...")
    frontend = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"],
        cwd=FRONTEND_DIR
    )
    processes.append(frontend)

    print("\n" + "=" * 50)
    print("  Backend:  http://127.0.0.1:8000")
    print("  Frontend: http://localhost:8501")
    print("  Press Ctrl+C to stop all services")
    print("=" * 50 + "\n")

    try:
        while True:
            if backend.poll() is not None:
                print("[WARN] Backend process exited. Shutting down...")
                cleanup()
            if frontend.poll() is not None:
                print("[WARN] Frontend process exited. Shutting down...")
                cleanup()
            time.sleep(1)
    except KeyboardInterrupt:
        cleanup()
