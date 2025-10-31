"""
Configuration management for the visa scheduler.
Loads settings from environment variables.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Optional

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for storing all settings."""
    
    # URLs
    BASE_URL = "https://www.usvisascheduling.com/"
    
    # Credentials
    USERNAME: str = os.getenv("VISA_USERNAME", "")
    PASSWORD: str = os.getenv("VISA_PASSWORD", "")
    
    # Security answers - store all three possible answers
    SECURITY_ANSWERS: Dict[str, str] = {
        "What was your first car?": os.getenv("SECURITY_ANSWER_1", ""),
        "Where did you meet your spouse?": os.getenv("SECURITY_ANSWER_2", ""),
        # Add the third question once you identify it
        "security_question_3": os.getenv("SECURITY_ANSWER_3", ""),
    }
    
    # Target date
    TARGET_MONTH: int = int(os.getenv("TARGET_MONTH", "12"))
    TARGET_YEAR: int = int(os.getenv("TARGET_YEAR", "2025"))
    
    # Consular post
    CONSULAR_POST: str = "ISTANBUL"
    
    # Check intervals (in minutes)
    CHECK_INTERVAL_MIN: int = int(os.getenv("CHECK_INTERVAL_MIN", "50"))
    CHECK_INTERVAL_MAX: int = int(os.getenv("CHECK_INTERVAL_MAX", "70"))
    
    # Notification settings
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    EMAIL_ADDRESS: Optional[str] = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    
    # Selenium settings
    HEADLESS: bool = os.getenv("HEADLESS", "True").lower() == "true"
    IMPLICIT_WAIT: int = 10
    PAGE_LOAD_TIMEOUT: int = 30
    
    # Screenshot settings
    SCREENSHOT_DIR: str = "screenshots"
    SAVE_SCREENSHOTS: bool = True
    
    # Logging
    LOG_DIR: str = "logs"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present."""
        if not cls.USERNAME or not cls.PASSWORD:
            raise ValueError("VISA_USERNAME and VISA_PASSWORD must be set")
        
        if not any(cls.SECURITY_ANSWERS.values()):
            raise ValueError("At least one security answer must be set")
        
        return True
    
    @classmethod
    def get_security_answer(cls, question: str) -> Optional[str]:
        """Get the answer for a specific security question."""
        # Try exact match first
        if question in cls.SECURITY_ANSWERS:
            return cls.SECURITY_ANSWERS[question]
        
        # Try partial match (case-insensitive)
        question_lower = question.lower()
        for q, answer in cls.SECURITY_ANSWERS.items():
            if q.lower() in question_lower or question_lower in q.lower():
                return answer
        
        return None
