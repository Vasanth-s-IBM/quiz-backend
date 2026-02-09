"""
Email service for sending certificates
Uses SMTP for email delivery
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from app.config import settings

def send_certificate_email(recipient_email: str, recipient_name: str, topic_name: str, pdf_path: str):
    """
    Send certificate via email
    Attaches PDF certificate
    """
    # Create message
    msg = MIMEMultipart()
    msg['From'] = settings.EMAIL_FROM
    msg['To'] = recipient_email
    msg['Subject'] = f"Your Certificate for {topic_name} Quiz"
    
    # Email body
    body = f"""
    Dear {recipient_name},
    
    Congratulations on completing the {topic_name} quiz!
    
    Please find your certificate attached to this email.
    
    Best regards,
    Quiz System Team
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach PDF
    try:
        with open(pdf_path, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=f'certificate.pdf')
            msg.attach(pdf_attachment)
    except Exception as e:
        print(f"Error attaching PDF: {e}")
        raise
    
    # Send email
    try:
        # Skip if SMTP not configured
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            print(f"SMTP not configured. Certificate would be sent to {recipient_email}")
            print(f"Certificate saved at: {pdf_path}")
            return
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Certificate sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise
