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
import undetected_chromedriver as uc
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
    Set up and configure Chrome WebDriver using undetected-chromedriver.
    This bypasses Cloudflare and other bot detection systems.

    Returns:
        Configured Chrome WebDriver instance
    """
    try:
        logging.info("Setting up undetected Chrome WebDriver...")

        # Configure options for undetected-chromedriver
        options = uc.ChromeOptions()

        if Config.HEADLESS:
            options.add_argument("--headless=new")  # Use new headless mode

        # Additional options for stability and stealth
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Create undetected Chrome driver
        # Specify version_main=141 to match your Chrome browser version
        driver = uc.Chrome(
            options=options,
            use_subprocess=False,  # Changed to False to prevent premature closure
            version_main=141,  # Match your Chrome version 141.x
            driver_executable_path=None,  # Let it auto-download
        )

        # Give the browser a moment to fully initialize
        import time
        time.sleep(2)

        # Set timeouts
        driver.implicitly_wait(Config.IMPLICIT_WAIT)
        driver.set_page_load_timeout(Config.PAGE_LOAD_TIMEOUT)

        logging.info("✓ Undetected Chrome WebDriver initialized successfully")
        return driver

    except Exception as e:
        error_msg = str(e)
        logging.error(f"Failed to initialize undetected Chrome: {error_msg}")

        # Check if it's a version mismatch in the error message
        if "version" in error_msg.lower() and "supports" in error_msg.lower():
            logging.error("ChromeDriver version mismatch detected!")
            logging.error("Please update Chrome browser: Open Chrome -> Settings -> About Chrome")

        raise Exception(f"Failed to initialize ChromeDriver: {error_msg}")


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
