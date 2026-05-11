import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.services.playwright_scraper import scrape_vercel_playwright

# ----------------------------
# PLATFORM DETECTION
# ----------------------------

def detect_platform(url: str):
    domain = urlparse(url).netloc.lower()

    if "github.com" in domain:
        return "github"
    elif "vercel.app" in domain:
        return "vercel"
    elif "streamlit.app" in domain:
        return "streamlit"
    elif "figma.com" in domain:
        return "figma"
    else:
        return "generic"

# ----------------------------
# GITHUB SCRAPER (ADVANCED 🔥)
# ----------------------------

def scrape_github(url: str):
    try:
        parts = urlparse(url).path.strip("/").split("/")
        owner, repo = parts[0], parts[1]

        base_api = f"https://api.github.com/repos/{owner}/{repo}"

        # Repo info
        repo_data = requests.get(base_api).json()

        # README
        readme_api = f"{base_api}/readme"
        readme_data = requests.get(readme_api).json()
        readme_content = readme_data.get("content", "")

        # File structure
        contents_api = f"{base_api}/contents"
        contents = requests.get(contents_api).json()

        file_names = [item["name"] for item in contents if "name" in item]

        # Combine all data
        final_text = f"""
        Repo: {repo_data.get('name')}
        Description: {repo_data.get('description')}
        Files: {' '.join(file_names)}
        README: {readme_content}
        """

        return final_text

    except Exception as e:
        return ""

# ----------------------------
# VERCEL / STREAMLIT SCRAPER
# ----------------------------

def scrape_dynamic(url: str):
    try:
        response = requests.get(url, timeout=10)

        soup = BeautifulSoup(response.text, "lxml")

        # Remove scripts/styles
        for tag in soup(["script", "style"]):
            tag.extract()

        text = soup.get_text(separator=" ", strip=True)

        # Extract JS (for API hints)
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string:
                text += " " + script.string

        return text

    except:
        return ""

# ----------------------------
# GENERIC SCRAPER
# ----------------------------

def scrape_generic(url: str):
    try:
        response = requests.get(url, timeout=10)

        # JSON API detection
        if "application/json" in response.headers.get("Content-Type", ""):
            return str(response.json())

        soup = BeautifulSoup(response.text, "lxml")

        for tag in soup(["script", "style"]):
            tag.extract()

        return soup.get_text(separator=" ", strip=True)

    except:
        return ""

# ----------------------------
# MAIN SCRAPER FUNCTION
# ----------------------------

def scrape_content(url: str):
    url = str(url)
    platform = detect_platform(url)

    if platform == "github":
        return scrape_github(url)

    elif platform == "vercel":
        return scrape_vercel_playwright(url)   # 🔥 PLAYWRIGHT

    elif platform == "streamlit":
        return scrape_dynamic(url)

    else:
        return scrape_generic(url)