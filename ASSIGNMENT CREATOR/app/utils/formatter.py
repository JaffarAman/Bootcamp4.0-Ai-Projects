def extract_title_description(ai_text):
    lines = ai_text.split("\n")

    title = "Assignment"
    description = ""

    for line in lines:
        if "Title:" in line:
            title = line.replace("Title:", "").strip()
        if "Description:" in line:
            description = line.replace("Description:", "").strip()

    return title, description