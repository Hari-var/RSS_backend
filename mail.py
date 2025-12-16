import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ---------------------------
# Configuration (change me)
# ---------------------------
smtp_host = "smtp.office365.com"
smtp_port = 587            # 587 for TLS, 465 for SSL
smtp_user = "mvp@valuemomentum.club"
smtp_password = "X)722941733478oc"

sender_email = "mvp@valuemomentum.club"
receiver_email = "shashank.tudum@valuemomentum.com"
subject = "Styled HTML Email Example"

# A plain-text fallback for email clients that don't render HTML
plain_text = """Hi there,
This is a fallback plain-text message. The rich HTML version has been sent as well.
If you can't see the HTML email, contact support@example.com.
"""

# Insert your HTML email body here. You can keep it as a multi-line string.
# For maintainability, put the HTML template in a separate file and read it in.
html_body = """<!doctype html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,sans-serif;color:#333;">
  <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:20px;">
    <table width="600" style="max-width:600px;background:#fff;border-radius:8px;overflow:hidden;">
      <tr><td style="padding:20px;background:linear-gradient(90deg,#2b6cb0,#4c9ef5);color:#fff;">
        <h1 style="margin:0;font-size:20px;">Company / App Name</h1>
      </td></tr>
      <tr><td style="padding:24px;">
        <p style="margin:0 0 12px;">Hi <strong>Recipient</strong>,</p>
        <p style="margin:0 0 12px;">This is a demo of a styled HTML email with inline-friendly CSS.</p>
        <p style="margin:0;">— Example content here.</p>
      </td></tr>
      <tr><td style="padding:16px;background:#fafbfc;font-size:12px;color:#666;">
        © 2025 Company Name
      </td></tr>
    </table>
  </td></tr></table>
</body>
</html>
"""

# ---------------------------
# Build message
# ---------------------------
msg = MIMEMultipart("alternative")
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Reply-To"] = sender_email
msg["Subject"] = subject

# Attach the plain-text and HTML versions (order: plain, then html)
part1 = MIMEText(plain_text, "plain")
part2 = MIMEText(html_body, "html")

msg.attach(part1)
msg.attach(part2)

# ---------------------------
# Send (TLS)
# ---------------------------
try:
    print(f"Connecting to {smtp_host}:{smtp_port}...")
    server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
    # server.set_debuglevel(1)  # Enable debug output
    
    print("Starting TLS...")
    server.starttls()
    
    print(f"Logging in as {smtp_user}...")
    server.login(smtp_user, smtp_password)
    
    print(f"Sending email from {sender_email} to {receiver_email}...")
    result = server.sendmail(sender_email, [receiver_email], msg.as_string())
    
    server.quit()
    print("Email sent successfully!")
    print(f"Server response: {result}")

except smtplib.SMTPAuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Check username/password or enable app passwords")
except smtplib.SMTPRecipientsRefused as e:
    print(f"Recipient refused: {e}")
except smtplib.SMTPException as e:
    print(f"SMTP error: {e}")
except Exception as e:
    print(f"Failed to send email: {e}")

 