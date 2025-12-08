import json
import datetime
import google.generativeai as genai

# --- CONFIGURATION ---
API_KEY = "" 
if API_KEY:
    genai.configure(api_key=API_KEY)

# --- DYNAMIC DATE SETUP ---
now = datetime.datetime.now()
current_year = now.year
current_date_str = now.strftime("%B %d, %Y") 

# --- THE HTML TEMPLATE ---
HTML_HEAD = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generative AI Newsletter - {current_date_str}</title>
    <style>
        /* --- GLOBAL RESETS --- */
        /* UPDATED FONT: Standard Sans-Serif Stack */
        body {{ 
            font-family: Helvetica, Arial, sans-serif; 
            background-color: #ffffff; 
            margin: 0; 
            padding: 20px; 
            color: #424242; 
            line-height: 1.5; 
        }}
        .container {{ max-width: 670px; margin: 0 auto; }}
        a {{ color: #1E88E5; text-decoration: none; font-weight: 700; }}
        a:hover {{ text-decoration: underline; color: #43A047; }}
        img {{ max-width: 100%; height: auto; display: block; border-radius: 6px; }}

        /* --- BOXES --- */
        .intro-box {{ border: 1px solid #43A047; border-radius: 12px; padding: 16px; margin-bottom: 20px; background-color: #f6fbf7; }}
        .divider {{ border-top: 1px solid #43A047; width: 90%; margin: 20px auto; opacity: 0.3; }}
        .section-header {{ background-color: #1E88E5; color: white; border-radius: 12px; padding: 12px; text-align: center; font-weight: 600; font-size: 18px; margin-bottom: 20px; }}

        /* --- ARTICLES --- */
        .article-box {{ border: 1px solid #e0e0e0; border-left: 4px solid #43A047; border-radius: 12px; padding: 16px; margin-bottom: 20px; background-color: #fff; }}
        .article-content p {{ margin: 12px 0; }}

        /* --- NO IMAGE LAYOUT --- */
        .no-image-layout {{ display: flex; flex-direction: column; justify-content: center; }}
        .no-image-title {{ font-size: 20px; color: #1E88E5; margin-bottom: 10px; }}

        /* --- FOOTER STYLES --- */
        .vm-footer {{ margin-top: 50px; border-top: 3px solid #1E88E5; padding-top: 30px; }}
        .vm-section-title {{ color: #1E88E5; font-size: 18px; font-weight: 700; margin-bottom: 20px; }}
        .vm-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 30px; }}
        .vm-card {{ background-color: #ffffff; border: 1px solid #e0e0e0; padding: 15px; border-radius: 12px; transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease; }}
        .vm-card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(30, 136, 229, 0.15); border-color: #1E88E5; }}
        .vm-card-title {{ font-weight: 700; margin: 0 0 8px 0; color: #424242; font-size: 14px; }}
        .vm-link {{ font-size: 12px; color: #1E88E5; text-decoration: none; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }}
        .vm-arrow {{ color: #43A047; font-weight: bold; font-size: 14px; }}
        .vm-upcoming-box {{ padding: 20px; border: 1px dashed #1E88E5; border-radius: 12px; margin-bottom: 30px; background-color: #f0f7fd; text-align: center; }}
        .vm-stats {{ text-align: center; font-size: 14px; color: #424242; margin-bottom: 15px; padding: 20px; background: #f5f5f5; border-radius: 12px; }}
        .vm-cta-btn {{ background-color: #43A047; color: white !important; padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: 600; text-decoration: none; display: inline-block; margin-left: 5px; transition: background-color 0.2s; }}
        .vm-cta-btn:hover {{ background-color: #2e7d32; text-decoration: none; }}
        
        @media (max-width: 600px) {{
            .vm-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
<div class="container">
    <div style="text-align: center; padding-bottom: 25px;">
        <img src="https://valuemomentum.club/wp-content/uploads/2025/10/ValueMomentum_logo.png" style="height: 60px; width: auto; margin: 0 auto;">
    </div>
    <div style="margin-bottom: 20px;">
        <img src="img/pexels-markus-winkler-1430818-30869149-1.jpg" alt="Cover">
    </div>
"""

# --- COMPLEX FOOTER TEMPLATE ---
HTML_FOOTER = f"""
    <div class="vm-footer">
        
        <h3 class="vm-section-title">Looking for something specific?</h3>
        
        <div class="vm-grid">
            
            <div class="vm-card">
                <p class="vm-card-title">Posts</p>
                <a href="https://valuemomentum.club/blog/" class="vm-link">Explore all posts</a> <span class="vm-arrow">›</span>
            </div>

            <div class="vm-card">
                <p class="vm-card-title">Questions</p>
                <a href="https://valuemomentum.club/questions/" class="vm-link">Explore all Questions</a> <span class="vm-arrow">›</span>
            </div>

            <div class="vm-card">
                <p class="vm-card-title">Podcasts</p>
                <a href="https://valuemomentum.club/podcasts/" class="vm-link">Explore all podcasts</a> <span class="vm-arrow">›</span>
            </div>

            <div class="vm-card">
                <p class="vm-card-title">Events</p>
                <a href="https://valuemomentum.club/events/" class="vm-link">Explore all events</a> <span class="vm-arrow">›</span>
            </div>

            <div class="vm-card">
                <p class="vm-card-title">IdeaAI</p>
                <a href="https://valuemomentum.club/ideaai/" class="vm-link">Access our IdeaAI</a> <span class="vm-arrow">›</span>
            </div>

            <div class="vm-card">
                <p class="vm-card-title">Leaderboard</p>
                <a href="https://valuemomentum.club/users/" class="vm-link">Access our leaderboard</a> <span class="vm-arrow">›</span>
            </div>

        </div>

        <div class="vm-upcoming-box">
            <h3 class="vm-section-title" style="margin-bottom:5px;">Upcoming Sessions & Events</h3>
            <p style="color:#666; font-size:14px; margin-top:0;">Don't miss these learning opportunities</p>
            <p style="text-align:center; color:#666; font-style: italic; margin-top:20px;">No upcoming events found.</p>
        </div>

        <div class="vm-stats">
            <p>Total Posts: <b>289</b> | Total Questions: <b>124</b> | Codeclub Sessions: <b>22</b></p>
            <div style="margin-top:15px;">
                <b>Click here to</b> <a href="https://valuemomentum.club/add-post/" class="vm-cta-btn">Publish your Post</a>
            </div>
            <p style="margin-top: 20px; font-size: 12px; color: #888;">&copy; {current_year} ValueMomentum. All rights reserved.</p>
        </div>

    </div>
</div>
</body>
</html>
"""

# --- FUNCTIONS ---

def generate_intro_text(updates):
    """
    Attempts to generate an intro via Gemini API.
    If API_KEY is missing or fails, uses a 'Smart Fallback'.
    """
    
    # 1. Prepare Fallback Text
    topics = [u.get('title') for u in updates[:2]]
    topic_str = " and ".join(topics) if topics else "the latest AI developments"
    
    fallback_text = (
        f"<b>Welcome back!</b> In today's edition for {current_date_str}, we are tracking significant moves in the industry, "
        f"including {topic_str}. As the landscape shifts, we bring you the essential updates you need to stay ahead."
    )

    # 2. Check if API is configured
    if not API_KEY:
        print("No API Key detected. Using fallback intro.")
        return fallback_text

    try:
        # 3. API Call
        print("Contacting Gemini API...")
        news_summaries = "\n".join([f"- {u.get('title')}: {u.get('description')}" for u in updates])
        
        prompt = f"""
        You are writing the introduction for a corporate AI newsletter. 
        Read the following news highlights:
        {news_summaries}

        Write a short, engaging paragraph (approx 3-4 sentences) starting with "Welcome back!".
        Summarize the key themes of this week's news. 
        The tone should be professional, insightful, and optimistic.
        Do not use markdown or bullet points.
        """

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        if response.text:
            return response.text.strip()
        else:
            return fallback_text

    except Exception as e:
        print(f"API Error ({e}). Switching to fallback.")
        return fallback_text

def create_headline_list(updates):
    """
    Creates the 'In today's newsletter' HTML section.
    """
    html_output = "<p><b>In today’s Generative AI Newsletter:</b></p><p>"
    
    for update in updates[:4]: 
        source = update.get('source', 'Update').replace('Feed: ', '')
        title = update.get('title', '')
        html_output += f"<b>{source}</b> {title}<br>"
    
    html_output += "</p>"
    return html_output

def create_article_cards(updates):
    """
    Generates HTML for each article card.
    """
    cards_html = ""
    
    for update in updates:
        title = update.get('title')
        desc = update.get('description')
        link = update.get('link', '#')
        img_url = update.get('image_url')
        
        has_image = img_url and len(str(img_url)) > 10 
        
        cards_html += '<div class="article-box">'
        
        if has_image:
            cards_html += f"""
            <div style="margin-bottom:12px;">
                <img src="{img_url}" alt="{title}">
            </div>
            <div class="article-content">
                <p><b><a href="{link}">{title}</a></b></p>
                <p>{desc}</p>
            </div>
            """
        else:
            cards_html += f"""
            <div class="no-image-layout">
                <div class="no-image-title">
                    <a href="{link}">{title}</a>
                </div>
                <div class="article-content">
                    <p>{desc}</p>
                    <p style="margin-top: 15px;">
                        <a href="{link}" style="font-size: 14px; text-transform: uppercase; letter-spacing: 0.5px;">Read full story &rarr;</a>
                    </p>
                </div>
            </div>
            """
            
        cards_html += '</div>'
        
    return cards_html

# --- MAIN EXECUTION ---

def generate_newsletter(updates):
    """
    Generates newsletter HTML from updates JSON.
    """
    intro_text = generate_intro_text(updates)
    headlines_html = create_headline_list(updates)
    cards_html = create_article_cards(updates)

    full_html = f"""
    {HTML_HEAD}
    
    <div class="intro-box">
        <p>{intro_text}</p>
        <div class="divider"></div>
        {headlines_html}
    </div>

    <div class="section-header">
        <span>Latest Developments</span>
    </div>

    {cards_html}

    {HTML_FOOTER}
    """
    #open file and writhe the html in it
    with open("newsletter.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    return full_html