# app/resources.py
import os

def emergency_lines(country_code: str | None):
    cc = (country_code or "GLOBAL").upper()
    # Keep this conservative and editable. Phone numbers and orgs change;
    # update before real deployment.
    general = [
        "If you are in immediate danger or thinking about harming yourself or others, call your local emergency number now (e.g., 112 in India, 999 in the UK, 911 in the US) or go to the nearest emergency department.",
        "Consider reaching out to a trusted friend, family member, or school counselor right away.",
    ]
    country = {
        "IN": [
            "India: You can contact your local emergency services by dialing 112.",
            "For counseling support, check government or university mental health services in your area.",
        ],
        "IE": [
            "Ireland: In an emergency, dial 112 or 999.",
            "HSE and university counseling services provide support; verify local numbers on official sites.",
        ],
        "DE": [
            "Germany: For emergencies, dial 112.",
            "Consider local crisis lines or university counseling centers (numbers vary by region).",
        ],
    }
    return general + country.get(cc, [])
