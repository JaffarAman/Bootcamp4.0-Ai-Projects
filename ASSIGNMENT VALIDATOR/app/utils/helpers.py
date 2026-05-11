from urllib.parse import urlparse

def detect_platform(url: str):
    domain = urlparse(url).netloc.lower()

    if "github" in domain:
        return "github"
    if "vercel" in domain:
        return "vercel"
    if "streamlit" in domain:
        return "streamlit"
    if "figma" in domain:
        return "figma"

    return "unknown"