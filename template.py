import json
import datetime

import google.generativeai as genai
import config

# --- CONFIGURATION ---
API_KEY = config.gemini_api_key

# IMPORTANT: Change this to your actual backend URL where images are hosted
# If running locally, this allows the email preview to load images
BASE_IMAGE_URL = "http://127.0.0.1:8000/uploads/"

if API_KEY:
    genai.configure(api_key=API_KEY)

now = datetime.datetime.now()
current_year = now.year
current_date_str = now.strftime("%B %d, %Y")

HTML_HEAD = f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8"> 
    <meta name="viewport" content="width=device-width"> 
    <meta http-equiv="X-UA-Compatible" content="IE=edge"> 
    <meta name="x-apple-disable-message-reformatting"> 
    <title>Generative AI Newsletter</title>
    
    <style>
        html, body {{ margin: 0 auto !important; padding: 0 !important; height: 100% !important; width: 100% !important; font-family: Helvetica, Arial, sans-serif; background-color: #f4f4f4; }}
        * {{ -ms-text-size-adjust: 100%; -webkit-text-size-adjust: 100%; }}
        div[style*="margin: 16px 0"] {{ margin: 0 !important; }}
        table, td {{ mso-table-lspace: 0pt !important; mso-table-rspace: 0pt !important; }}
        table {{ border-spacing: 0 !important; border-collapse: collapse !important; table-layout: fixed !important; margin: 0 auto !important; }}
        img {{ -ms-interpolation-mode:bicubic; }}
        a {{ text-decoration: none; color: #1E88E5; }}
        a:hover {{ text-decoration: underline; color: #43A047; }}
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
                    <img src="https://raw.githubusercontent.com/Hari-var/RSS_feed/refs/heads/main/public/ValueMomentum_logo.png" width="200" height="auto" alt="ValueMomentum" border="0" style="height: auto; font-family: sans-serif; font-size: 15px; line-height: 15px; color: #555555; display: block; margin: 0 auto;">
                </td>
            </tr>
            <tr>
                <td style="background-color: #ffffff;">
                    <img src="https://raw.githubusercontent.com/Hari-var/RSS_backend/refs/heads/master/pexels-markus-winkler-1430818-30869149-1.jpg" width="600" height="" alt="Alt Text" border="0" style="width: 100%; max-width: 600px; height: auto; background: #dddddd; font-family: sans-serif; font-size: 15px; line-height: 15px; color: #555555; margin: auto; display: block;" class="fluid-img">
                </td>
            </tr>
"""

HTML_FOOTER_TOP = "" 

HTML_FOOTER_BOTTOM = f"""
            <tr>
                <td style="padding: 20px; background-color: #ffffff; text-align: center; border-top: 1px solid #eeeeee;">
                    <p style="margin: 0; font-family: Helvetica, Arial, sans-serif; font-size: 12px; color: #888;">&copy; {current_year} ValueMomentum. All rights reserved.</p>
                </td>
            </tr>
        </table>
        <br><br>
    </center>
</body>
</html>
"""

def generate_intro_text(updates):
    if not updates:
        return f"Welcome back! In today's edition for {current_date_str}, we are tracking significant moves in the industry."
    
    # FIX: Handle both 'title' (posts) and 'event_name' (events)
    # FIX: Filter out None values to prevent crash
    raw_topics = [u.get('title') or u.get('event_name', '') for u in updates]
    valid_topics = [t for t in raw_topics if t and t.strip()]
    
    topic_str = " and ".join(valid_topics) if valid_topics else "the latest AI developments"
    fallback_text = f"<b>Welcome back!</b> In today's edition for {current_date_str}, we are tracking significant moves in the industry, including {topic_str}."
    
    if not API_KEY:
        print("API Key not found, using fallback intro text.")
        return fallback_text

    try:
        # Create summaries specifically handling the different keys for Posts vs Events
        summaries_list = []
        for u in updates:
            if 'event_name' in u:
                 summaries_list.append(f"- Event: {u.get('event_name')} by {u.get('presenter')}")
            else:
                 summaries_list.append(f"- Article: {u.get('title')}: {u.get('description')}")
        
        news_summaries = "\n".join(summaries_list)
        
        prompt = f"""
        You are writing the introduction for a corporate AI newsletter. 
        Read these highlights: {news_summaries}. 
        
        Do not simply summarize the articles individually. Instead, analyze the collective intelligence of these updates.
        Write a cohesive paragraph starting with "Welcome back!".
        Focus on the broader industry trends, underlying themes, or the bigger picture narrative that connects these stories together.
        
        Output format: Plain text only (no markdown).
        """
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else fallback_text
    except Exception as e:
        print(f"Error in generating intro text: {e}")
        return fallback_text

def create_headline_list(updates):
    html = '<p style="margin: 0 0 10px 0;"><b>In today\'s Generative AI Newsletter:</b></p>'
    # Sort updates: posts first, then external events, then internal events
    sorted_updates = sorted(updates, key=lambda x: (
        0 if 'title' in x else
        1 if 'event_name' in x and x.get('is_external', False) else
        2
    ))
    
    for update in sorted_updates:
        # FIX: Check for 'event_name' key instead of 'Events' string
        if 'event_name' in update:
            event_label = "External Event" if update.get('is_external') else "Event"
            html += f'<div style="margin-bottom: 5px;">&bull; <b>{event_label}:</b> {update.get("event_name", "")}</div>'
        else:
            source = update.get("source", "Update")
            if source:
                source = source.replace("Feed: ", "")
            html += f'<div style="margin-bottom: 5px;">&bull; <b>{source}:</b> {update.get("title", "")}</div>'
    return html

def create_article_cards(updates):
    cards_html = ""
    # Sort updates: posts first, then external events, then internal events
    sorted_updates = sorted(updates, key=lambda x: (
        0 if 'title' in x else
        1 if 'event_name' in x and x.get('is_external', False) else
        2
    ))
    
    for update in sorted_updates:
        # FIX: Check for 'event_name' to identify events
        if 'event_name' in update:
            # --- HANDLE EVENT (Internal or External) ---
            is_external = update.get('is_external', False)
            title = update.get('event_name', '')
            description = f"Type: {update.get('event_type', '')}" # Events usually don't have descriptions in your JSON, using Type
            link = update.get('invite_link', '#')
            location = update.get('invite_location', 'Online')
            # Format datetime from ISO format to readable format
            raw_date_time = update.get('date_time', '')
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(raw_date_time.replace('T', ' '))
                date_time = dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                date_time = raw_date_time
            presenter = update.get('presenter', '')
            
            # Get image paths
            print("DEBUG: Processing event:", update)
            event_img_path = update.get('event_images')
            presenter_img_path = update.get('presenter_images')
            
            print(f"DEBUG: event_img_path = {event_img_path}")
            print(f"DEBUG: presenter_img_path = {presenter_img_path}")

            img_html = f'<div style="margin-bottom: 15px;"><img src="{event_img_path}" width="500" alt="Event Image" border="0" style="width: 100%; max-width: 100%; height: auto; display: block; border-radius: 4px;" class="fluid-img"></div>' if event_img_path else ''
            presenter_html = f'<img src="{presenter_img_path}" width="40" height="40" alt="Presenter" border="0" style="border-radius: 50%; vertical-align: middle; margin-right: 8px;">' if presenter_img_path else ''

            cards_html += f'''
        <tr>
            <td style="padding: 0 20px 20px 20px; background-color: #ffffff;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="border: 1px solid #e0e0e0; border-left: 4px solid {'#9C27B0' if is_external else '#FF9800'}; border-radius: 4px;">
                    <tr>
                        <td style="padding: 15px;">
                            <h2 style="margin: 0 0 10px 0; font-family: Helvetica, Arial, sans-serif; font-size: 18px; line-height: 22px; color: #333333;">
                                <a href="{link}" style="color: {'#9C27B0' if is_external else '#FF9800'}; text-decoration: none;">{title}</a>
                            </h2>
                            {img_html}
                            <p style="margin: 0 0 10px 0; font-family: Helvetica, Arial, sans-serif; font-size: 14px; line-height: 22px; color: #555555;">{description}</p>
                            <p style="margin: 0 0 5px 0; font-family: Helvetica, Arial, sans-serif; font-size: 13px; color: #666;"><b>Date & Time:</b> {date_time}</p>
                            <p style="margin: 0 0 5px 0; font-family: Helvetica, Arial, sans-serif; font-size: 13px; color: #666;">{presenter_html}<b>Presenter:</b> {presenter}</p>
                            <p style="margin: 0 0 15px 0; font-family: Helvetica, Arial, sans-serif; font-size: 13px; color: #666;"><b>Location:</b> {location}</p>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="border-radius: 4px; background: {'#9C27B0' if is_external else '#FF9800'};">
                                        <a href="{link}" style="background: {'#9C27B0' if is_external else '#FF9800'}; font-family: Helvetica, Arial, sans-serif; font-size: 12px; font-weight: bold; color: #ffffff; text-decoration: none; padding: 8px 12px; display: block; border-radius: 4px; text-transform: uppercase;">View Event &rarr;</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
            '''
        else:
            # --- HANDLE STANDARD POST ---
            img = update.get('image_url')
            # Handle case where image_url might be None
            img_html = f'<div style="margin-bottom: 15px;"><img src="{img}" width="500" alt="" border="0" style="width: 100%; max-width: 100%; height: auto; display: block; border-radius: 4px;" class="fluid-img"></div>' if img and isinstance(img, str) and len(img.strip()) > 10 else ''
            
            cards_html += f'''
        <tr>
            <td style="padding: 0 20px 20px 20px; background-color: #ffffff;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="border: 1px solid #e0e0e0; border-left: 4px solid #43A047; border-radius: 4px;">
                    <tr>
                        <td style="padding: 15px;">
                            <h2 style="margin: 0 0 10px 0; font-family: Helvetica, Arial, sans-serif; font-size: 18px; line-height: 22px; color: #333333;">
                                <a href="{update.get('link', '#')}" style="color: #1E88E5; text-decoration: none;">{update.get('title')}</a>
                            </h2>
                            {img_html}
                            <p style="margin: 0 0 15px 0; font-family: Helvetica, Arial, sans-serif; font-size: 14px; line-height: 22px; color: #555555;">{update.get('description', '')}</p>
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="border-radius: 4px; background: #ffffff; border: 1px solid #1E88E5;">
                                        <a href="{update.get('link', '#')}" style="background: #ffffff; font-family: Helvetica, Arial, sans-serif; font-size: 12px; font-weight: bold; color: #1E88E5; text-decoration: none; padding: 8px 12px; display: block; border-radius: 4px; text-transform: uppercase;">Read Story &rarr;</a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
            '''
    return cards_html

def create_footer_grid():
    return ""

def generate_newsletter(updates):
    if not updates:
        print("No updates to generate.")
        return ""
    
    intro_text = generate_intro_text(updates)
    headlines_html = create_headline_list(updates)
    cards_html = create_article_cards(updates)
    footer_grid_html = create_footer_grid()
    
    full_html = f"""
    {HTML_HEAD}
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
            {footer_grid_html}
            {HTML_FOOTER_BOTTOM}
    """
    with open("newsletter.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print("Success: newsletter.html generated based on custom template.")
    return full_html