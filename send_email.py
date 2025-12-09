import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

smtp_host = "smtp.office365.com"
smtp_port = 587
smtp_user = "mvp@valuemomentum.club"
smtp_password = "X)722941733478oc"
sender_email = "mvp@valuemomentum.club"

def send_email(html_content, receiver_email, subject="Generative AI Newsletter"):
    plain_text = "Please view this email in an HTML-compatible email client."
    
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Reply-To"] = sender_email
    msg["Subject"] = subject
    
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, [receiver_email], msg.as_string())
        server.quit()
        return {"status": "success", "message": "Email sent successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}