"""
Certificate PDF generation service — landscape A4, in-memory, no disk storage
"""
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white
from datetime import datetime
import io

# Brand colors
GOLD       = HexColor("#C9A84C")
GOLD_LIGHT = HexColor("#F0D080")
GOLD_DARK  = HexColor("#8B6914")
NAVY       = HexColor("#1A2B4A")
NAVY_LIGHT = HexColor("#2E4070")
CREAM      = HexColor("#FDFAF3")
GRAY       = HexColor("#555555")
LIGHT_GRAY = HexColor("#888888")


def _background(c, width, height):
    c.setFillColor(CREAM)
    c.rect(0, 0, width, height, fill=1, stroke=0)


def _border(c, width, height):
    m1, m2 = 0.35 * inch, 0.52 * inch
    c.setStrokeColor(GOLD)
    c.setLineWidth(5)
    c.rect(m1, m1, width - 2 * m1, height - 2 * m1)
    c.setStrokeColor(GOLD_DARK)
    c.setLineWidth(1.2)
    c.rect(m2, m2, width - 2 * m2, height - 2 * m2)
    sq = 0.13 * inch
    for x in [m1 - sq / 2, width - m1 - sq / 2]:
        for y in [m1 - sq / 2, height - m1 - sq / 2]:
            c.setFillColor(GOLD)
            c.rect(x, y, sq, sq, fill=1, stroke=0)


def _header_band(c, width, height):
    band_h = 1.4 * inch
    c.setFillColor(NAVY)
    c.rect(0.52 * inch, height - 0.52 * inch - band_h,
           width - 1.04 * inch, band_h, fill=1, stroke=0)
    return height - 0.52 * inch - band_h  # returns band bottom y


def _footer_band(c, width):
    c.setFillColor(NAVY)
    c.rect(0.52 * inch, 0.52 * inch, width - 1.04 * inch, 0.34 * inch, fill=1, stroke=0)


def _divider(c, y, width):
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.8)
    c.line(1.2 * inch, y, width - 1.2 * inch, y)


def generate_certificate_pdf(
    user_name: str,
    topic_name: str,
    score: int,
    total: int,
    grade: str
) -> bytes:
    """Generate certificate PDF in-memory and return as bytes."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)  # 841.9 x 595.3 pt

    _background(c, width, height)
    _border(c, width, height)
    band_bottom = _header_band(c, width, height)
    _footer_band(c, width)

    cx = width / 2  # horizontal center

    # ── Header band content ──────────────────────────────────
    band_mid = band_bottom + 0.7 * inch

    c.setFillColor(GOLD_LIGHT)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(cx, band_mid + 0.42 * inch, "✦   QUIZ PLATFORM   ✦")

    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(cx, band_mid + 0.08 * inch, "CERTIFICATE OF ACHIEVEMENT")

    c.setFillColor(GOLD_LIGHT)
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(cx, band_mid - 0.28 * inch, "Excellence in Knowledge Assessment")

    # ── Body — evenly spaced in remaining area ───────────────
    # Available vertical space: band_bottom down to footer top (0.86 inch)
    body_top = band_bottom - 0.45 * inch
    body_bot = 0.52 * inch + 0.34 * inch + 0.3 * inch  # just above footer

    # "This is to certify that"
    y = body_top
    c.setFillColor(LIGHT_GRAY)
    c.setFont("Helvetica", 12)
    c.drawCentredString(cx, y, "This is to proudly certify that")

    # Recipient name
    y -= 0.58 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 34)
    c.drawCentredString(cx, y, user_name)

    # Gold underline under name
    nw = c.stringWidth(user_name, "Helvetica-Bold", 34)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.8)
    c.line(cx - nw / 2, y - 7, cx + nw / 2, y - 7)

    # "has successfully completed"
    y -= 0.6 * inch
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 12)
    c.drawCentredString(cx, y, "has successfully completed the assessment on")

    # Topic name
    y -= 0.45 * inch
    c.setFillColor(NAVY_LIGHT)
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(cx, y, topic_name)

    # Divider
    y -= 0.45 * inch
    _divider(c, y, width)

    # Grade block — centered
    y -= 0.38 * inch
    c.setFillColor(GOLD_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(cx, y, "GRADE")

    y -= 0.3 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 26)
    c.drawCentredString(cx, y, grade)

    # Divider
    y -= 0.35 * inch
    _divider(c, y, width)

    # Date & Certificate ID
    date_str = datetime.now().strftime("%B %d, %Y")
    cert_id  = f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    y -= 0.32 * inch
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 9)
    c.drawCentredString(cx, y, f"Date of Issue: {date_str}   |   Certificate ID: {cert_id}")

    # ── Footer text ───────────────────────────────────────────
    c.setFillColor(GOLD_LIGHT)
    c.setFont("Helvetica", 8)
    c.drawCentredString(cx, 0.52 * inch + 0.09 * inch,
                        "This certificate is issued by Quiz Platform  •  quizplatform.example.com")

    c.save()
    buffer.seek(0)
    return buffer.read()
