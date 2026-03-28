"""
Reusable grade calculation service
"""

def calculate_grade(score: int, total: int) -> str:
    """
    Calculate letter grade from score and total.
    Returns grade string based on percentage thresholds.
    """
    if total == 0:
        return "C-"
    percentage = (score / total) * 100
    if percentage >= 90:
        return "A+"
    if percentage >= 80:
        return "A"
    if percentage >= 70:
        return "B"
    if percentage >= 60:
        return "C"
    return "C-"


def calculate_percentage(score: int, total: int) -> float:
    """Returns rounded percentage, 0.0 if total is zero."""
    if total == 0:
        return 0.0
    return round((score / total) * 100, 2)
