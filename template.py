import json
import datetime
import google.generativeai as genai
import os

# --- CONFIGURATION ---
API_KEY = os.getenv("GEMINI_API_KEY", "") 

if API_KEY:
    genai.configure(api_key=API_KEY)

# --- DYNAMIC DATE SETUP ---
now = datetime.datetime.now()
current_year = now.year
current_date_str = now.strftime("%B %d, %Y")

# --- EMAIL HTML HEAD (CLIENT RESETS) ---
HTML_HEAD = f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8"> 
    <meta name="viewport" content="width=device-width"> 
    <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
    <meta name="x-apple-disable-message-reformatting"> 
    <title>Generative AI Newsletter</title>
    
    <style>
        /* RESET STYLES */
        html, body {{ margin: 0 auto !important; padding: 0 !important; height: 100% !important; width: 100% !important; font-family: Helvetica, Arial, sans-serif; background-color: #f4f4f4; }}
        * {{ -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; }}
        div[style*="margin: 16px 0"] {{ margin: 0 !important; }}
        table, td {{ mso-table-lspace: 0pt !important; mso-table-rspace: 0pt !important; }}
        table {{ border-spacing: 0 !important; border-collapse: collapse !important; table-layout: fixed !important; margin: 0 auto !important; }}
        img {{ -ms-interpolation-mode:bicubic; }}
        
        /* CLIENT SPECIFIC STYLES */
        a {{ text-decoration: none; color: #1E88E5; }}
        a:hover {{ text-decoration: underline; color: #43A047; }}
        
        /* RESPONSIVE STYLES */
        @media screen and (max-width: 600px) {{
            .email-container {{ width: 100% !important; margin: auto !important; }}
            .fluid-img {{ width: 100% !important; max-width: 100% !important; height: auto !important; }}
            .stack-column, .stack-column-center {{ display: block !important; width: 100% !important; max-width: 100% !important; direction: ltr !important; }}
            .stack-column-center {{ text-align: center !important; }}
            .center-on-mobile {{ text-align: center !important; display: block !important; margin-left: auto !important; margin-right: auto !important; }}
            .mobile-pad {{ padding: 20px !important; }}
        }}
    </style>
</head>
<body width="100%" style="margin: 0; padding: 0 !important; mso-line-height-rule: exactly; background-color: #f4f4f4;">
    <center style="width: 100%; background-color: #f4f4f4;">
    
        <div style="display: none; font-size: 1px; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden; mso-hide: all; font-family: sans-serif;">
            Latest Generative AI updates for {current_date_str}.
        </div>

        <table align="center" role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 0 auto;" class="email-container">
            
            <tr>
                <td style="padding: 20px 0; text-align: center;">
                    <img src="https://valuemomentum.club/wp-content/uploads/2025/10/ValueMomentum_logo.png" width="200" height="auto" alt="ValueMomentum" border="0" style="height: auto; font-family: sans-serif; font-size: 15px; line-height: 15px; color: #555555; display: block; margin: 0 auto;">
                </td>
            </tr>

            <tr>
                <td style="background-color: #ffffff;">
                    <img src="https://raw.githubusercontent.com/Hari-var/RSS_backend/refs/heads/master/pexels-markus-winkler-1430818-30869149-1.jpg" width="600" height="" alt="Alt Text" border="0" style="width: 100%; max-width: 600px; height: auto; background: #dddddd; font-family: sans-serif; font-size: 15px; line-height: 15px; color: #555555; margin: auto; display: block;" class="fluid-img">
                </td>
            </tr>
"""

HTML_FOOTER_TOP = """
            <tr>
                <td style="padding: 30px 20px 10px 20px; background-color: #ffffff; border-top: 3px solid #1E88E5;">
                    <h3 style="margin: 0 0 20px 0; font-family: Helvetica, Arial, sans-serif; font-size: 18px; color: #1E88E5;">Looking for something specific?</h3>
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                        <tr>
                            <td style="padding: 0;">
"""

# The footer items need to be generated carefully for Outlook columns
# We will use a 2-column layout that works in Outlook
def create_footer_grid():
    items = [
        ("Posts", "https://valuemomentum.club/blog/"),
        ("Questions", "https://valuemomentum.club/questions/"),
        ("Podcasts", "https://valuemomentum.club/podcasts/"),
        ("Events", "https://valuemomentum.club/events/"),
        ("IdeaAI", "https://valuemomentum.club/ideaai/"),
        ("Leaderboard", "https://valuemomentum.club/users/")
    ]
    
    html = ""
    # We will do rows of 2 for simplicity and stability in Outlook
    for i in range(0, len(items), 2):
        item1 = items[i]
        item2 = items[i+1] if i+1 < len(items) else None
        
        html += '<tr>'
        # Column 1
        html += f"""
            <td width="48%" valign="top" class="stack-column" style="padding-bottom: 20px;">
                <table role="presentation" cellspacing="0" cellpadding="15" border="0" width="100%" style="border: 1px solid #e0e0e0; border-radius: 8px;">
                    <tr>
                        <td style="text-align: left; background-color: #fafafa;">
                            <p style="margin: 0 0 5px 0; font-weight: bold; font-size: 14px; color: #333;">{item1[0]}</p>
                            <a href="{item1[1]}" style="font-size: 12px; font-weight: bold; text-transform: uppercase;">Explore &rsaquo;</a>
                        </td>
                    </tr>
                </table>
            </td>
        """
        
        # Spacer
        html += '<td width="4%" class="stack-column" style="padding-bottom: 20px;">&nbsp;</td>'
        
        # Column 2
        if item2:
            html += f"""
                <td width="48%" valign="top" class="stack-column" style="padding-bottom: 20px;">
                    <table role="presentation" cellspacing="0" cellpadding="15" border="0" width="100%" style="border: 1px solid #e0e0e0; border-radius: 8px;">
                        <tr>
                            <td style="text-align: left; background-color: #fafafa;">
                                <p style="margin: 0 0 5px 0; font-weight: bold; font-size: 14px; color: #333;">{item2[0]}</p>
                                <a href="{item2[1]}" style="font-size: 12px; font-weight: bold; text-transform: uppercase;">Explore &rsaquo;</a>
                            </td>
                        </tr>
                    </table>
                </td>
            """
        else:
            html += '<td width="48%" class="stack-column">&nbsp;</td>'
            
        html += '</tr>'
        
    return html

HTML_FOOTER_BOTTOM = f"""
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <tr>
                <td style="padding: 20px; background-color: #ffffff;">
                    <div style="background-color: #f5f5f5; border-radius: 8px; padding: 20px; text-align: center;">
                        <p style="margin: 0 0 15px 0; font-family: Helvetica, Arial, sans-serif; font-size: 14px; color: #444;">
                            Total Posts: <b>289</b> | Total Questions: <b>124</b>
                        </p>
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
                            <tr>
                                <td style="border-radius: 6px; background: #43A047;">
                                    <a href="https://valuemomentum.club/add-post/" style="background: #43A047; border: 1px solid #43A047; font-family: Helvetica, Arial, sans-serif; font-size: 14px; font-weight: bold; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 6px; display: inline-block;">Publish your Post</a>
                                </td>
                            </tr>
                        </table>
                        <p style="margin-top: 20px; font-size: 12px; color: #888;">&copy; {current_year} ValueMomentum. All rights reserved.</p>
                    </div>
                </td>
            </tr>

        </table>
        <br><br>
    </center>
</body>
</html>
"""

# --- FUNCTIONS ---

def generate_intro_text(updates):
    # (Same logic as before, just kept compact for this snippet)
    if not updates:
        return "Welcome back! Here are the latest updates."
    
    # Fallback
    topics = [u.get('title') for u in updates[:2]]
    topic_str = " and ".join(topics) if topics else "the latest AI developments"
    
    fallback_text = (
        f"<b>Welcome back!</b> In today's edition for {current_date_str}, we are tracking significant moves in the industry, "
        f"including {topic_str}."
    )
    
    if not API_KEY:
        return fallback_text
        
    try:
        news_summaries = "\n".join([f"- {u.get('title')}: {u.get('description')}" for u in updates])
        prompt = f"""You are writing the introduction for a corporate AI newsletter. Read these highlights: {news_summaries}. 
        Write a short (3 sentences), engaging paragraph starting with "Welcome back!". Professional tone. No markdown."""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else fallback_text
    except:
        return fallback_text

def create_headline_list(updates):
    html = '<p style="margin: 0 0 10px 0;"><b>In today’s Generative AI Newsletter:</b></p>'
    for update in updates[:4]: 
        source = update.get('source', 'Update').replace('Feed: ', '')
        title = update.get('title', '')
        # Using a table row for bullets in Outlook is safer, but <br> is acceptable for simple lists
        html += f'<div style="margin-bottom: 5px;">&bull; <b>{source}:</b> {title}</div>'
    return html

def create_article_cards(updates):
    cards_html = ""
    
    for update in updates:
        title = update.get('title')
        desc = update.get('description', '')
        link = update.get('link', '#')
        img_url = update.get('image_url')
        has_image = img_url and isinstance(img_url, str) and len(img_url.strip()) > 10 

        # We use a Table for the card to enforce layout in Outlook
        cards_html += f"""
        <tr>
            <td style="padding: 0 20px 20px 20px; background-color: #ffffff;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="border: 1px solid #e0e0e0; border-left: 4px solid #43A047; border-radius: 4px;">
                    <tr>
                        <td style="padding: 15px;">
                            <h2 style="margin: 0 0 10px 0; font-family: Helvetica, Arial, sans-serif; font-size: 18px; line-height: 22px; color: #333333;">
                                <a href="{link}" style="color: #1E88E5; text-decoration: none;">{title}</a>
                            </h2>
        """
        
        if has_image:
            cards_html += f"""
                            <div style="margin-bottom: 15px;">
                                <img src="{img_url}" width="500" alt="" border="0" style="width: 100%; max-width: 100%; height: auto; display: block; border-radius: 4px;" class="fluid-img">
                            </div>
            """
            
        cards_html += f"""
                            <p style="margin: 0 0 15px 0; font-family: Helvetica, Arial, sans-serif; font-size: 14px; line-height: 22px; color: #555555;">
                                {desc}
                            </p>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="border-radius: 4px; background: #ffffff; border: 1px solid #1E88E5;">
                                        <a href="{link}" style="background: #ffffff; font-family: Helvetica, Arial, sans-serif; font-size: 12px; font-weight: bold; color: #1E88E5; text-decoration: none; padding: 8px 12px; display: block; border-radius: 4px; text-transform: uppercase;">Read Story &rarr;</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        """
    return cards_html

# --- MAIN EXECUTION ---

def generate_newsletter(updates):
    if not updates: return ""

    intro_text = generate_intro_text(updates)
    headlines_html = create_headline_list(updates)
    cards_html = create_article_cards(updates)
    footer_grid = create_footer_grid()

    # Construct the body
    # We inject the dynamic parts into the main Table structure
    
    body_content = f"""
            <tr>
                <td style="padding: 20px; background-color: #ffffff;">
                    <table role="presentation" cellspacing="0" cellpadding="20" border="0" width="100%" style="background-color: #f6fbf7; border: 1px solid #43A047; border-radius: 8px;">
                        <tr>
                            <td style="font-family: Helvetica, Arial, sans-serif; font-size: 15px; line-height: 22px; color: #333333;">
                                {intro_text}
                                <div style="height: 1px; background-color: #43A047; width: 100%; margin: 15px 0; opacity: 0.3;"></div>
                                {headlines_html}
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <tr>
                <td style="padding: 0 20px 10px 20px; background-color: #ffffff;">
                     <table role="presentation" cellspacing="0" cellpadding="10" border="0" width="100%" style="background-color: #1E88E5; border-radius: 4px;">
                        <tr>
                            <td style="font-family: Helvetica, Arial, sans-serif; font-size: 16px; font-weight: bold; color: #ffffff; text-align: center;">
                                Latest Developments
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            {cards_html}

            {HTML_FOOTER_TOP}
            {footer_grid}
            {HTML_FOOTER_BOTTOM}
    """

    full_html = HTML_HEAD + body_content
    
    with open("newsletter.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Newsletter generated.")
    return full_html

if __name__ == "__main__":
    dummy_updates = [
        {
            "title": "OpenAI Releases New Reasoning Model",
            "description": "The new model demonstrates advanced capabilities in math and coding.",
            "link": "https://example.com",
            "source": "TechCrunch",
            "image_url": "https://placehold.co/600x300/png"
        },
        {
            "title": "Google DeepMind Update",
            "description": "AlphaGeometry system reaches gold-medalist level performance.",
            "link": "https://example.com",
            "source": "The Verge",
            "image_url": "" 
        }
    ]
    generate_newsletter(dummy_updates)