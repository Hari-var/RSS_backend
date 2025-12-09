import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import config

smtp_host = config.smtp_host
smtp_port = config.smtp_port
smtp_user = config.smtp_user
smtp_password = config.smtp_password
sender_email = config.sender_email

def send_email(html_content, receiver_emails, subject="Generative AI Newsletter"):
    plain_text = "Please view this email in an HTML-compatible email client."
    
    if isinstance(receiver_emails, str):
        receiver_emails = [receiver_emails]
    
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = ", ".join(receiver_emails)
    msg["Reply-To"] = sender_email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, receiver_emails, msg.as_string())
        server.quit()
        return {"status": "success", "message": f"Email sent to {len(receiver_emails)} recipient(s)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}