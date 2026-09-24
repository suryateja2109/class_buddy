# File: modules/email_service.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import ssl
import html

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- CONFIGURATION (LOADED SECURELY VIA ENVIRONMENT / .ENV) ---
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")
# --------------------------------------------------------------


def send_email(receiver_email, subject, body):
    """Generic function to handle the actual SMTP connection and sending."""
    if not SENDER_PASSWORD or not SENDER_EMAIL:
        print("[EMAIL ERROR] Configuration missing. Cannot send real email.")
        return False

    if not receiver_email or not str(receiver_email).strip():
        print("[EMAIL ERROR] Missing receiver email.")
        return False

    clean_receiver = str(receiver_email).strip()
    clean_password = SENDER_PASSWORD.replace(" ", "")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = SENDER_EMAIL
    message["To"] = clean_receiver

    # Attach HTML content
    part1 = MIMEText(body, "html")
    message.attach(part1)

    # Use context manager for secure SMTP connection with timeout
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SENDER_EMAIL, clean_password)
            server.sendmail(SENDER_EMAIL, clean_receiver, message.as_string())

        print(f"[REAL EMAIL] Successfully sent email to {clean_receiver}.")
        return True

    except Exception as e:
        print(f"[EMAIL FAILED] Could not send to {clean_receiver}. Error: {e}")
        return False


def send_absence_alert(student_name, student_email, subject, day):
    """Sends a predictive absence alert."""
    safe_name = html.escape(str(student_name))
    safe_subj = html.escape(str(subject))
    safe_day = html.escape(str(day))

    email_subject = f"🚨 URGENT: Predicted Absence Alert for {subject} Class"
    email_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h3 style="color: #e74c3c;">ClassBuddy Attendance Alert</h3>
        <p>Dear {safe_name},</p>
        <p>This is an automated predictive alert from <strong>ClassBuddy</strong>. Our predictive model indicates a high probability that you may miss your scheduled 
        <strong>{safe_subj}</strong> class today, <strong>{safe_day}</strong>.</p>
        <p>Please ensure you are present and on time. Maintaining regular attendance is critical for your academic performance.</p>
        <br>
        <p style="color: #7f8c8d; font-size: 0.9em;">ClassBuddy Automated Academic Assistant</p>
      </body>
    </html>
    """
    return send_email(student_email, email_subject, email_body)


def send_manual_reminder(student_name, student_email, subject, message):
    """Sends a manual reminder email."""
    safe_name = html.escape(str(student_name))
    safe_subj = html.escape(str(subject))
    safe_msg = html.escape(str(message)).replace("\n", "<br>")

    email_subject = f"❗ Class Reminder: {subject}"
    email_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h3 style="color: #1abc9c;">Message Regarding {safe_subj}</h3>
        <p>Dear {safe_name},</p>
        <p>Your instructor has sent the following notification regarding <strong>{safe_subj}</strong>:</p>
        <div style="border-left: 4px solid #1abc9c; padding: 12px 18px; margin: 15px 0; background-color: #f8f9fa; border-radius: 4px;">
            {safe_msg}
        </div>
        <p>Please take the necessary action accordingly.</p>
        <br>
        <p style="color: #7f8c8d; font-size: 0.9em;">ClassBuddy Notification System</p>
      </body>
    </html>
    """
    return send_email(student_email, email_subject, email_body)

