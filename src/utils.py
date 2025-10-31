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

    # User agent
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Initialize driver with ChromeDriverManager
    # This automatically downloads the correct version matching your Chrome browser
    try:
        # Get the chromedriver path from ChromeDriverManager
        driver_path = ChromeDriverManager().install()
        logging.info(f"ChromeDriverManager returned: {driver_path}")

        # Fix for the path issue: ChromeDriverManager returns wrong file
        # Always look for the actual "chromedriver" file in the parent directory
        parent_dir = os.path.dirname(driver_path)
        correct_driver_path = os.path.join(parent_dir, "chromedriver")

        if os.path.exists(correct_driver_path):
            driver_path = correct_driver_path
            logging.info(f"Found correct chromedriver at: {driver_path}")
        else:
            logging.warning(f"Could not find chromedriver at {correct_driver_path}, using original path")

        # Make sure it's executable
        if os.path.exists(driver_path):
            os.chmod(driver_path, 0o755)
            logging.info(f"✓ Using chromedriver at: {driver_path}")
        else:
            raise FileNotFoundError(f"Could not find chromedriver at {driver_path}")

        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        error_msg = str(e)
        logging.error(f"ChromeDriverManager failed: {error_msg}")

        # Check if it's a version mismatch in the error message
        if "version" in error_msg.lower() and "supports" in error_msg.lower():
            logging.error("ChromeDriver version mismatch detected!")
            logging.error("Please update Chrome browser: Open Chrome -> Settings -> About Chrome")
            logging.error("Or install matching chromedriver version")

        raise Exception(f"Failed to initialize ChromeDriver: {error_msg}")

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
