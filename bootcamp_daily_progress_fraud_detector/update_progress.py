from database import progress
import random



data = list(progress.find())

yesterday_tasks = [
    "Fixed MongoDB indexing issue and optimized query performance",
    "Debugged backend API authentication error",
    "Improved database schema for better scalability",
    "Resolved React state management bug in dashboard",
    "Refactored Node.js API routes for cleaner structure",
    "Implemented caching for faster response time",
]

today_tasks = [
    "Working on JWT authentication system integration",
    "Building file upload feature with validation",
    "Developing analytics dashboard charts using React",
    "Integrating third-party payment gateway API",
    "Improving API security with rate limiting",
    "Setting up CI/CD pipeline for deployment",
]

for i, doc in enumerate(data):
    new_yesterday = random.choice(yesterday_tasks)
    new_today = random.choice(today_tasks)

    progress.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "yesterdayWork": new_yesterday,
                "todayPlan": new_today
            }
        }
    )

print("✅ Database successfully updated with diverse tasks")