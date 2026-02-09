"""
Certificate PDF generation service
Uses reportlab for PDF creation
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import os

def generate_certificate_pdf(user_name: str, topic_name: str, score: int, total: int, grade: str) -> str:
    """
    Generate a certificate PDF
    Returns the file path of generated PDF
    """
    # Create certificates directory if not exists
    cert_dir = "certificates"
    os.makedirs(cert_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{cert_dir}/certificate_{user_name.replace(' ', '_')}_{timestamp}.pdf"
    
    # Create PDF
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # Title
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width / 2, height - 2 * inch, "CERTIFICATE OF ACHIEVEMENT")
    
    # Subtitle
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 2.8 * inch, "This is to certify that")
    
    # User name
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 3.5 * inch, user_name)
    
    # Achievement text
    c.setFont("Helvetica", 16)
    c.drawCentredString(width / 2, height - 4.2 * inch, "has successfully completed the quiz on")
    
    # Topic name
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 4.9 * inch, topic_name)
    
    # Score details
    c.setFont("Helvetica", 14)
    score_text = f"Score: {score}/{total} | Grade: {grade}"
    c.drawCentredString(width / 2, height - 5.6 * inch, score_text)
    
    # Date
    c.setFont("Helvetica", 12)
    date_text = f"Date: {datetime.now().strftime('%B %d, %Y')}"
    c.drawCentredString(width / 2, height - 6.3 * inch, date_text)
    
    # Border
    c.setLineWidth(3)
    c.rect(0.5 * inch, 0.5 * inch, width - inch, height - inch)
    
    c.save()
    return filename
