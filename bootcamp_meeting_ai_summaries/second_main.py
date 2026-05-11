from database import meeting_notes_collection, meeting_details_collection, name, niaz_meeting_summaries
from bson import ObjectId
from fastapi import FastAPI
import json
from datetime import datetime
import uuid

from groq import Groq
from config import GROQ_API_KEY 

app = FastAPI()

# =========================
# GROQ CLIENT SETUP
# =========================
client = Groq(
    api_key=GROQ_API_KEY
)

def generate_with_groq(prompt: str):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content


# =========================
# HOME ROUTE
# =========================
@app.get("/")
def get_meeting_notes():
    meeting_notes = list(meeting_notes_collection.find())

    for note in meeting_notes:
        note["_id"] = str(note["_id"])
        note["user"] = str(note["user"])
        note["meeting"] = str(note["meeting"])
        note["scriber"] = str(note["scriber"])

    return meeting_notes


# =========================
# SPECIFIC MEETING
# =========================
@app.get("/specific_meeting/{meeting_id}")
def get_meeting_notes(meeting_id: str):

    meeting_notes = list(meeting_notes_collection.find({"meeting": ObjectId(meeting_id)}))
    meeting_details = meeting_details_collection.find_one({"_id": ObjectId(meeting_id)})

    for note in meeting_notes:
        note["_id"] = str(note["_id"])
        note["user"] = str(note["user"])
        note["meeting"] = str(note["meeting"])
        note["scriber"] = str(note["scriber"])

    return {
        "details": meeting_details["agenda"] if meeting_details else "No details found",
        "notes": meeting_notes
    }


def serialize(note):
    note["_id"] = str(note["_id"])
    note["user"] = str(note["user"])
    note["meeting"] = str(note["meeting"])
    note["scriber"] = str(note["scriber"])
    return note


# =========================
# MAIN GROQ SUMMARY ROUTE
# =========================
@app.get("/meetingsummary/{meeting_id}")
def get_meeting_data(meeting_id: str):

    summaries = list(niaz_meeting_summaries.find({
        "meeting_id": {"$ne": ObjectId(meeting_id)}
    }))

    previous_task = []
    previous_summaries = []

    if summaries:
        previous_summaries = [s.get("overall_summary", "") for s in summaries]

        for s in summaries:
            for t in s.get("key_insights", {}).get("action_items", []):
                previous_task.append({
                    "meeting_id": str(s.get("meeting_id")),
                    "agenda": s.get("agenda", "Unknown"),
                    "owner": t.get("owner", "Unknown"),
                    "task": t.get("task", ""),
                    "status": t.get("status", "Pending"),
                    "priority": t.get("priority", "High"),
                    "task_id": t.get("task_id", "")
                })

    data = list(meeting_notes_collection.find({"meeting": ObjectId(meeting_id)}))
    meeting_details = meeting_details_collection.find_one({"_id": ObjectId(meeting_id)})

    grouped = {}

    for item in data:
        item = serialize(item)

        topic = item["topic"]

        if topic not in grouped:
            grouped[topic] = {
                "topic": topic,
                "statements": []
            }

        user_data = name.find_one({"_id": ObjectId(item["user"])})
        user_name = user_data["name"] if user_data else "Unknown"

        grouped[topic]["statements"].append({
            "statement": item["statement"],
            "user": user_name
        })

    clean_meeting = {
        "details": meeting_details["agenda"] if meeting_details else "No details found",
        "topics": [
            {
                "topic": t["topic"],
                "statements": [
                    {
                        "text": s["statement"],
                        "speaker": s["user"]
                    }
                    for s in t["statements"]
                ]
            }
            for t in grouped.values()
        ]
    }

    # =========================
    # PROMPT
    # =========================
    prompt = f"""
You are a production-grade Meeting Intelligence System.

========================
CORE OBJECTIVE
========================
Generate:
1. Full structured current meeting summary
2. Short overall summary of current meeting
3. Return previous tasks unchanged
4. Generate final overall summary across all meetings

========================
HARD CONSTRAINTS
========================
1. Return ONLY valid JSON.
2. No explanations or markdown.
3. No hallucination.
4. Preserve meaning of statements.
5. If missing → empty arrays or "Unknown".

========================
CURRENT MEETING RULES
========================
- Extract ALL details (no loss of information)
- Maintain speaker statements
- Group by topics
- Extract key_points, decisions, action_items
- Action items must include:
    task, assigned_to, status, priority

========================
CURRENT SUMMARY RULE
========================
Generate a short summary of ONLY current meeting.

========================
PREVIOUS TASK RULE
========================
- Return previous_tasks EXACTLY as input
- Do NOT modify anything

========================
FINAL OVERALL SUMMARY RULE
========================
- Combine:
    → previous summaries
    → current meeting summary
- Remove duplication
- Keep concise
- Maintain continuity

========================
OUTPUT FORMAT (STRICT)
========================
{{
  "current_meeting": {{
    "meeting_info": {{
      "agenda": "string",
      "total_attendees": number,
      "attendees": []
    }},
    "topics": [
      {{
        "topic_title": "string",
        "discussion": [
          {{
            "speaker": "string",
            "statement": "string"
          }}
        ]
      }}
    ],
    "key_points": [],
    "decisions": [],
    "action_items": [
      {{
        "task": "string",
        "assigned_to": "string",
        "status": "Pending | In Progress | Completed",
        "priority": "High | Medium | Low"
      }}
    ],
    "speaker_summaries": [
      {{
        "speaker": "string",
        "summary": "string"
      }}
    ]
  }},

  "current_meeting_overall_summary": "",

  "previous_tasks": [],

  "final_overall_summary": ""
}}

========================
INPUT DATA
========================
{clean_meeting_json}

========================
PREVIOUS TASKS
========================
{previous_task}

========================
PREVIOUS SUMMARIES
========================
{previous_summaries}
"""

    try:
        response = generate_with_groq(prompt)

        result = json.loads(response)

        result["meeting_id"] = str(ObjectId(meeting_id))
        result["created_at"] = datetime.utcnow()

        # add task ids
        for task in result.get("key_insights", {}).get("action_items", []):
            task["task_id"] = str(uuid.uuid4())

        # save in DB
        niaz_meeting_summaries.insert_one({
            "meeting_id": ObjectId(meeting_id),
            "agenda": result.get("agenda"),
            "overall_summary": result.get("overall_summary"),
            "meeting_overview": result.get("meeting_overview"),
            "topic_wise_discussion": result.get("topic_wise_discussion"),
            "key_insights": result.get("key_insights"),
            "individual_speaker_summaries": result.get("individual_speaker_summaries"),
            "created_at": datetime.utcnow()
        })

        return result

    except Exception as e:
        return {
            "error": str(e)
        }


# =========================
# SUMMARY ROUTE
# =========================
@app.get("/summary")
def get_meeting_summary():

    summary = list(niaz_meeting_summaries.find())

    previous_task = []

    for s in summary:
        for t in s.get("key_insights", {}).get("action_items", []):
            previous_task.append({
                "meeting_id": str(s.get("meeting_id")),
                "agenda": s.get("agenda", "Unknown"),
                "owner": t.get("owner", "Unknown"),
                "task": t.get("task", ""),
                "status": t.get("status", "Pending"),
                "priority": t.get("priority", "High"),
                "task_id": t.get("task_id", "")
            })

    return previous_task