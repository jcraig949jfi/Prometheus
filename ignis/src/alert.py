import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

# Import locally to avoid circular import if needed, but passing config object is better
# from ignis_config import IgnisConfig

def print_visual_separator(char="=", length=80, text=None):
    if text:
        # Center the text
        padding = (length - len(text) - 2) // 2
        line = f"{char * padding} {text} {char * padding}"
        # Adjust for odd lengths
        if len(line) < length:
            line += char
        print("\n" + line + "\n")
    else:
        print("\n" + (char * length) + "\n")

def send_alert(subject: str, body: str, config=None):
    """
    Sends an alert notification via console and email (if configured).
    """
    # 1. Console Broadcast (High Visibility)
    print_visual_separator("!", 80, f"ALERT: {subject}")
    print(f"{body}")
    print_visual_separator("!", 80)
    
    logging.warning(f"ALERT: {subject} - {body}")

    # 2. Email Notification
    if config and config.email_to and config.smtp_server:
        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = f"[Ignis Pipeline] {subject}"
            msg['From'] = config.smtp_user or "ignis-pipeline@localhost"
            msg['To'] = config.email_to

            # Connect to SMTP Server
            with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
                server.starttls()
                if config.smtp_user and config.smtp_password:
                    server.login(config.smtp_user, config.smtp_password)
                server.send_message(msg)
            
            logging.info(f"Email alert sent to {config.email_to}")
            
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")
            print(f"Error sending email: {e}")
