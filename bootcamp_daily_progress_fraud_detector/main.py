from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from database import progress, fraud_updates
from schema import TodayUpdate
from websocket_manager import manager
from notify import check_missing_updates

from bson import ObjectId
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

app = FastAPI()

pakistan_tz = pytz.timezone("Asia/Karachi")
scheduler = AsyncIOScheduler(timezone=pakistan_tz)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket, role="admin")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)


@app.on_event("startup")
async def startup_event():
    scheduler.add_job(
        check_missing_updates,
        "cron",
        hour=14,       # ← Yahan apna hour likho (24hr format)
        minute=32,     # ← Yahan apna minute likho
        timezone=pakistan_tz
    )
    scheduler.start()
    print("✅ Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


@app.get("/test-notify")
async def test_notify():
    await check_missing_updates()  # ✅ Real function call karo test mein bhi
    return {"status": "sent"}


def serialize_doc(doc):
    return {
        key: str(value) if isinstance(value, ObjectId) else value
        for key, value in doc.items()
    }


@app.get("/")
def home():
    data = list(progress.find())
    return [serialize_doc(item) for item in data]


def check_similarity(new_text, old_texts):
    if not old_texts:
        return 0, None
    texts = [new_text] + old_texts
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(texts)
    similarity_matrix = cosine_similarity(vectors)
    scores = similarity_matrix[0][1:]
    max_index = scores.argmax()
    max_score = scores[max_index]
    return max_score, max_index


@app.post("/today_update")
def today_update(payload: TodayUpdate):
    student_obj_id = ObjectId(payload.student_id)
    current_date = datetime.utcnow()

    old_records = list(progress.find({
        "studentId": student_obj_id,
        "date": {"$lt": current_date}
    }))

    old_texts = [r.get("yesterdayWork", "") for r in old_records]
    similarity, match_index = check_similarity(payload.yesterdayWork, old_texts)
    is_fraud = bool(similarity >= 0.75)

    matched_record = None
    if match_index is not None and old_records:
        matched_record = old_records[match_index]

    new_progress = {
        "studentId": student_obj_id,
        "date": current_date,
        "yesterdayWork": payload.yesterdayWork,
        "todayPlan": payload.todayPlan,
        "blockers": payload.blockers,
        "githubLink": payload.githubLink,
        "hoursWorked": payload.hoursWorked,
        "needMentor": payload.needMentor,
        "similarity": round(similarity * 100, 2),
        "fraud": is_fraud,
        "matched_id": str(matched_record["_id"]) if matched_record else None,
        "createdAt": current_date,
        "updatedAt": current_date
    }

    progress.insert_one(new_progress)

    if is_fraud and matched_record:
        fraud_updates.insert_one({
            "studentId": student_obj_id,
            "yesterdayWork": payload.yesterdayWork,
            "similarity": round(similarity * 100, 2),
            "fraud": is_fraud,
            "matched_text": matched_record["yesterdayWork"],
            "matched_date": matched_record["date"],
            "date": current_date
        })

    return {
        "studentId": payload.student_id,
        "inputWork": payload.yesterdayWork,
        "similarity_percent": round(similarity * 100, 2),
        "fraud": is_fraud,
        "matched_data": matched_record["yesterdayWork"] if matched_record else None,
        "matched_date": matched_record["date"] if matched_record else None
    }
