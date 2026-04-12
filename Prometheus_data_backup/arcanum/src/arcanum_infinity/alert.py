import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

from .xeno_config import XenoConfig

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

def send_alert(subject: str, body: str, config: Optional[XenoConfig] = None):
    """
    Sends an alert notification via console and email (if configured).
    """
    # 1. Console Broadcast (High Visibility)
    print_visual_separator("!", 80, f"ALERT: {subject}")
    print(f"{body}")
    print_visual_separator("!", 80)
    
    logging.warning(f"ALERT: {subject} - {body}")

    # 2. Email Notification
    if config and hasattr(config, "email_alerts") and config.email_alerts and config.email_alerts.email_to and config.email_alerts.smtp_server:
        try:
            alerts_config = config.email_alerts
            msg = EmailMessage()
            msg.set_content(body)
            msg['Subject'] = f"[Xenolexicon Pipeline] {subject}"
            msg['From'] = alerts_config.smtp_user or "xenolexicon-pipeline@localhost"
            msg['To'] = alerts_config.email_to

            # Connect to SMTP Server
            with smtplib.SMTP(alerts_config.smtp_server, alerts_config.smtp_port) as server:
                server.starttls()
                if alerts_config.smtp_user and alerts_config.smtp_password:
                    server.login(alerts_config.smtp_user, alerts_config.smtp_password)
                server.send_message(msg)
            
            logging.info(f"Email alert sent to {alerts_config.email_to}")
            
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")
            print(f"Error sending email: {e}")
