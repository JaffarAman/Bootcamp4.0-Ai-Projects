import requests
from app.constants import DOMAIN_MAP, SIMILARITY_THRESHOLD
from app.utils.helpers import detect_platform
from app.services.scraper import scrape_content
from app.services.similarity import calculate_similarity
from app.crud import save_submission

def is_url_working(url):
    try:
        return requests.get(url, timeout=5).status_code == 200
    except:
        return False

def map_domain(domain_id):
    domain_id = str(domain_id)

    mapping = {
        "69c538969d2f7dcce6f2df26": "AI",
        "69c538969d2f7dcce6f2df24": "Web",   # 👈 ADD YOUR REAL IDs
        "69c2304ccfe658657f11a4fd": "UI/UX"
    }

    return mapping.get(domain_id)

def validate_submission(user, assignment, link):

    # 1. Detect platform
    platform = detect_platform(link)

    # 2. Get domain
    student_domain = map_domain(user.get("domainId"))

    allowed = DOMAIN_MAP.get(student_domain, [])

    if platform not in allowed:
        return False, "Invalid platform for your domain", 0

    # 3. URL working check
    if not is_url_working(link):
        return False, "Link not working", 0

    # 4. Scrape content
    content = scrape_content(link)

    if not content:
        return False, "Unable to scrape content", 0

    # 5. Similarity check (ONLY SAME STUDENT)
    similarity = calculate_similarity(content, user["_id"])

    if similarity >= SIMILARITY_THRESHOLD:
        return False, f"Similarity too high ({similarity:.2f})", similarity

    # 6. Save
    save_submission(user["_id"], assignment["_id"], link, content, similarity)

    return True, "Submission accepted", similarity