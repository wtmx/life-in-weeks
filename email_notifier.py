import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_notifier.log'),
        logging.StreamHandler()
    ]
)

def send_notification(subject, message, log_content=None):
    """Send email notification about the upload status."""
    try:
        # Email configuration
        sender_email = os.environ.get('NOTIFICATION_EMAIL')
        sender_password = os.environ.get('NOTIFICATION_PASSWORD')
        receiver_email = os.environ.get('NOTIFICATION_EMAIL')  # Same as sender for now
        
        if not all([sender_email, sender_password, receiver_email]):
            logging.error("Email credentials not found in environment variables")
            return False

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"Life in Weeks Update: {subject}"

        # Add message body
        body = f"""
Life in Weeks Update Status

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {subject}

Details:
{message}
"""
        
        # Add log content if provided
        if log_content:
            body += f"\nLog Details:\n{log_content}"

        msg.attach(MIMEText(body, 'plain'))

        # Create server connection
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login and send email
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Email notification sent successfully: {subject}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to send email notification: {str(e)}")
        return False 