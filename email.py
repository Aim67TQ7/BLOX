import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Validate environment variables
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
APP_URL = os.getenv("APP_URL")

if not EMAIL_USER or not EMAIL_PASSWORD or not APP_URL:
    raise ValueError("Missing necessary environment variables for email configuration")

def send_password_reset_email(email: str, reset_token: str):
    """
    Sends a password reset email to the specified recipient.
    
    Args:
        email (str): Recipient's email address.
        reset_token (str): Unique token for password reset.
    """
    if not email or not reset_token:
        raise ValueError("Email and reset token are required")

    # Create the password reset URL
    reset_url = f"{APP_URL}/reset-password?token={reset_token}"

    # Create the email content
    subject = "Password Reset Request"
    html_content = f"""
    <h1>Password Reset Request</h1>
    <p>Click the link below to reset your password:</p>
    <a href="{reset_url}">Reset Password</a>
    <p>If you didn't request this, please ignore this email.</p>
    """

    # Setup the email message
    message = MIMEMultipart("alternative")
    message["From"] = EMAIL_USER
    message["To"] = email
    message["Subject"] = subject

    # Attach the HTML content
    message.attach(MIMEText(html_content, "html"))

    try:
        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, email, message.as_string())
            print(f"Password reset email sent to {email}")
    except Exception as e:
        print(f"Failed to send email to {email}: {e}")
        raise RuntimeError("Error sending password reset email") from e
