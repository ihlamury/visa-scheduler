"""
Utility functions for the visa scheduler.
"""

import os
import logging
import random
from datetime import datetime
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from src.config import Config


def setup_logger(name: str = "visa_scheduler") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, Config.LOG_LEVEL))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    log_file = os.path.join(
        Config.LOG_DIR,
        f"visa_scheduler_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def setup_driver() -> webdriver.Chrome:
    """
    Set up and configure Chrome WebDriver.
    
    Returns:
        Configured Chrome WebDriver instance
    """
    chrome_options = Options()
    
    if Config.HEADLESS:
        chrome_options.add_argument("--headless")
    
    # Additional options for stability
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent to appear more like a real browser
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Initialize driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set timeouts
    driver.implicitly_wait(Config.IMPLICIT_WAIT)
    driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)
    
    return driver


def save_screenshot(driver: webdriver.Chrome, name: str) -> Optional[str]:
    """
    Save a screenshot of the current page.
    
    Args:
        driver: WebDriver instance
        name: Name for the screenshot file
        
    Returns:
        Path to saved screenshot or None if failed
    """
    if not Config.SAVE_SCREENSHOTS:
        return None
    
    try:
        os.makedirs(Config.SCREENSHOT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(Config.SCREENSHOT_DIR, filename)
        driver.save_screenshot(filepath)
        return filepath
    except Exception as e:
        logging.error(f"Failed to save screenshot: {e}")
        return None


def get_random_wait_time() -> int:
    """
    Get a random wait time between checks in seconds.
    
    Returns:
        Random number of seconds to wait
    """
    min_seconds = Config.CHECK_INTERVAL_MIN * 60
    max_seconds = Config.CHECK_INTERVAL_MAX * 60
    return random.randint(min_seconds, max_seconds)


def format_date(month: int, year: int) -> str:
    """
    Format month and year for display.
    
    Args:
        month: Month number (1-12)
        year: Year
        
    Returns:
        Formatted date string
    """
    return f"{datetime(year, month, 1).strftime('%B')} {year}"
