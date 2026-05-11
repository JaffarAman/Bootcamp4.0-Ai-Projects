from datetime import datetime, timedelta
import pytz
import os
from database import progress, users
from websocket_manager import manager

QUEUE_FILE = "notification_queue.txt"
NOTIFIED_FLAG_FILE = "notified_today.txt"
pakistan_tz = pytz.timezone("Asia/Karachi")


def already_notified_today() -> bool:
    """Aaj notification bheji ja chuki hai ya nahi"""
    pk_today = datetime.now(pakistan_tz).strftime("%Y-%m-%d")
    if not os.path.exists(NOTIFIED_FLAG_FILE):
        return False
    with open(NOTIFIED_FLAG_FILE, "r") as f:
        return f.read().strip() == pk_today


def mark_notified_today():
    """Aaj ki date flag file mein likho"""
    pk_today = datetime.now(pakistan_tz).strftime("%Y-%m-%d")
    with open(NOTIFIED_FLAG_FILE, "w") as f:
        f.write(pk_today)


def write_to_file(message: str):
    """Admin offline ho to fallback file mein save karo"""
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")
    print(f"📁 File mein save hua: {message}")


async def check_missing_updates():
    print("⏰ check_missing_updates chali!")

    # ✅ Guard: aaj pehle hi notify ho chuka hai
    if already_notified_today():
        print("⚠️ Aaj notification pehle hi bheji ja chuki hai. Skip.")
        return

    # ✅ Pakistan time se aaj ka din calculate karo
    now_pk = datetime.now(pakistan_tz)
    start_pk = now_pk.replace(hour=0, minute=0, second=0, microsecond=0)
    end_pk = start_pk + timedelta(days=1)

    # MongoDB mein UTC naive format mein dates hain — convert karo
    start_utc = start_pk.astimezone(pytz.utc).replace(tzinfo=None)
    end_utc = end_pk.astimezone(pytz.utc).replace(tzinfo=None)

    print(f"📅 PKT range: {start_pk.strftime('%Y-%m-%d')} 00:00 → 23:59")
    print(f"📅 UTC range: {start_utc} → {end_utc}")

    all_students = list(users.find({"role": "student"}))
    print(f"👥 Total students: {len(all_students)}")

    missing_students = []
    for student in all_students:
        record = progress.find_one({
            "studentId": student["_id"],
            "date": {"$gte": start_utc, "$lt": end_utc}
        })
        if not record:
            missing_students.append(student.get("rollNo", "Unknown"))

    print("❌ Missing:", missing_students)

    if missing_students:
        message = f"⚠️ Aaj update nahi ki: {', '.join(missing_students)}"
    else:
        message = "✅ Sab students ne aaj update kar di!"

    # ✅ Pehle flag set karo — phir bhejo (double call safe)
    mark_notified_today()

    if manager.admin_connections:
        await manager.notify_admins(message)
        print(f"📡 WebSocket se bheji: {message}")
    else:
        write_to_file(message)
        print(f"📁 Admin offline tha, file mein save: {message}")
