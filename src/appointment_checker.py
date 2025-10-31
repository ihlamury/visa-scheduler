"""
Appointment checking module for US Visa Scheduler.
Handles navigation to scheduling page and checking availability.
"""

import time
import logging
from typing import List, Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.config import Config
from src.utils import save_screenshot

logger = logging.getLogger("visa_scheduler")


def navigate_to_scheduling(driver: webdriver.Chrome) -> bool:
    """
    Navigate to the appointment scheduling page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if navigation successful, False otherwise
    """
    try:
        logger.info("Navigating to appointment scheduling page...")
        
        wait = WebDriverWait(driver, 15)
        
        # Look for "Schedule Appointment" link/button
        schedule_selectors = [
            (By.XPATH, "//a[contains(text(), 'Schedule Appointment')]"),
            (By.XPATH, "//button[contains(text(), 'Schedule Appointment')]"),
            (By.LINK_TEXT, "Schedule Appointment"),
            (By.PARTIAL_LINK_TEXT, "Schedule"),
        ]
        
        for by, selector in schedule_selectors:
            try:
                schedule_button = wait.until(
                    EC.element_to_be_clickable((by, selector))
                )
                logger.info(f"Found Schedule Appointment button using: {selector}")
                schedule_button.click()
                time.sleep(2)
                
                save_screenshot(driver, "scheduling_page")
                logger.info("Successfully navigated to scheduling page")
                return True
            except TimeoutException:
                continue
        
        logger.error("Could not find Schedule Appointment button")
        save_screenshot(driver, "schedule_button_not_found")
        return False
        
    except Exception as e:
        logger.error(f"Error navigating to scheduling: {e}", exc_info=True)
        save_screenshot(driver, "navigation_error")
        return False


def select_consular_post(driver: webdriver.Chrome, post_name: str = "ISTANBUL") -> bool:
    """
    Select the consular post from the dropdown.
    
    Args:
        driver: Selenium WebDriver instance
        post_name: Name of the consular post (default: ISTANBUL)
        
    Returns:
        True if selection successful, False otherwise
    """
    try:
        logger.info(f"Selecting consular post: {post_name}")
        
        wait = WebDriverWait(driver, 15)
        
        # Look for the consular posts dropdown
        # Based on screenshots, it's likely a <select> element
        dropdown_selectors = [
            (By.XPATH, "//select[contains(@class, 'consular') or contains(@id, 'consular')]"),
            (By.XPATH, "//select"),  # Fallback to any select element
            (By.ID, "consularPost"),
            (By.NAME, "consularPost"),
        ]
        
        for by, selector in dropdown_selectors:
            try:
                dropdown_element = wait.until(
                    EC.presence_of_element_located((by, selector))
                )
                
                # Try to select using Select class
                select = Select(dropdown_element)
                
                # Try different methods to select Istanbul
                try:
                    select.select_by_visible_text(post_name)
                    logger.info(f"Selected {post_name} by visible text")
                except:
                    try:
                        select.select_by_value(post_name)
                        logger.info(f"Selected {post_name} by value")
                    except:
                        # Try case-insensitive match
                        for option in select.options:
                            if post_name.lower() in option.text.lower():
                                select.select_by_visible_text(option.text)
                                logger.info(f"Selected {post_name} by partial match: {option.text}")
                                break
                
                time.sleep(2)  # Wait for calendar to load
                
                save_screenshot(driver, "consular_post_selected")
                logger.info("Consular post selected successfully")
                return True
                
            except TimeoutException:
                continue
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {e}")
                continue
        
        logger.error("Could not find or select consular post dropdown")
        save_screenshot(driver, "consular_post_error")
        return False
        
    except Exception as e:
        logger.error(f"Error selecting consular post: {e}", exc_info=True)
        save_screenshot(driver, "consular_selection_error")
        return False


def navigate_to_target_month(driver: webdriver.Chrome, target_month: int, target_year: int) -> bool:
    """
    Navigate the calendar to the target month and year.
    
    Args:
        driver: Selenium WebDriver instance
        target_month: Target month (1-12)
        target_year: Target year
        
    Returns:
        True if navigation successful, False otherwise
    """
    try:
        logger.info(f"Navigating to {target_month}/{target_year}")
        
        wait = WebDriverWait(driver, 10)
        max_clicks = 24  # Don't click more than 24 times (2 years worth)
        clicks = 0
        
        while clicks < max_clicks:
            # Get current month/year displayed in calendar
            current_month_text = get_current_calendar_month(driver)
            
            if not current_month_text:
                logger.error("Could not determine current calendar month")
                return False
            
            logger.info(f"Current calendar shows: {current_month_text}")
            
            # Check if we're at the target month
            if is_target_month(current_month_text, target_month, target_year):
                logger.info("Reached target month!")
                save_screenshot(driver, f"calendar_{target_month}_{target_year}")
                return True
            
            # Click next month button
            if not click_next_month(driver):
                logger.error("Could not click next month button")
                return False
            
            clicks += 1
            time.sleep(1)
        
        logger.error(f"Could not reach target month after {clicks} attempts")
        return False
        
    except Exception as e:
        logger.error(f"Error navigating to target month: {e}", exc_info=True)
        save_screenshot(driver, "month_navigation_error")
        return False


def get_current_calendar_month(driver: webdriver.Chrome) -> Optional[str]:
    """
    Get the current month/year displayed in the calendar.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        String with month/year or None if not found
    """
    try:
        # Look for month/year display element
        month_selectors = [
            (By.XPATH, "//*[contains(@class, 'month')]"),
            (By.XPATH, "//*[contains(@class, 'calendar-header')]"),
            (By.XPATH, "//select[@name='month']"),
            (By.XPATH, "//h3 | //h4 | //h5"),  # Headers often show month
        ]
        
        for by, selector in month_selectors:
            try:
                elements = driver.find_elements(by, selector)
                for element in elements:
                    text = element.text.strip()
                    if text and (len(text) < 50):  # Reasonable length for month display
                        # Check if it contains month name or number
                        if any(month in text.lower() for month in 
                              ['january', 'february', 'march', 'april', 'may', 'june',
                               'july', 'august', 'september', 'october', 'november', 'december']) or \
                           any(str(year) in text for year in range(2024, 2027)):
                            return text
            except:
                continue
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting current month: {e}")
        return None


def is_target_month(month_text: str, target_month: int, target_year: int) -> bool:
    """
    Check if the displayed month matches our target.
    
    Args:
        month_text: Text showing current month
        target_month: Target month number (1-12)
        target_year: Target year
        
    Returns:
        True if this is the target month
    """
    try:
        month_text_lower = month_text.lower()
        
        # Month names
        month_names = ['january', 'february', 'march', 'april', 'may', 'june',
                      'july', 'august', 'september', 'october', 'november', 'december']
        
        target_month_name = month_names[target_month - 1]
        
        # Check if target month name and year are in the text
        has_month = target_month_name in month_text_lower
        has_year = str(target_year) in month_text
        
        return has_month and has_year
        
    except Exception as e:
        logger.error(f"Error checking target month: {e}")
        return False


def click_next_month(driver: webdriver.Chrome) -> bool:
    """
    Click the next month button in the calendar.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if clicked successfully
    """
    try:
        # Look for next month button
        next_selectors = [
            (By.XPATH, "//button[contains(@class, 'next')]"),
            (By.XPATH, "//button[contains(@aria-label, 'next')]"),
            (By.XPATH, "//button[contains(text(), '›')] | //button[contains(text(), '>')]"),
            (By.CLASS_NAME, "ui-datepicker-next"),
            (By.XPATH, "//a[contains(@class, 'next')]"),
        ]
        
        for by, selector in next_selectors:
            try:
                button = driver.find_element(by, selector)
                if button.is_displayed() and button.is_enabled():
                    button.click()
                    return True
            except:
                continue
        
        return False
        
    except Exception as e:
        logger.error(f"Error clicking next month: {e}")
        return False


def check_availability(driver: webdriver.Chrome) -> List[Dict[str, str]]:
    """
    Check for available appointment slots in the current calendar view.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        List of available appointments with date and time info
    """
    try:
        logger.info("Checking for available appointments...")
        
        appointments = []
        
        # Look for clickable date cells
        date_selectors = [
            (By.XPATH, "//td[contains(@class, 'available')] | //td[not(contains(@class, 'disabled'))]"),
            (By.XPATH, "//button[contains(@class, 'day')]"),
            (By.XPATH, "//a[contains(@class, 'date')]"),
        ]
        
        for by, selector in date_selectors:
            try:
                date_elements = driver.find_elements(by, selector)
                
                for element in date_elements:
                    # Check if the element is clickable (not disabled/grayed out)
                    if element.is_displayed() and element.is_enabled():
                        try:
                            # Get date information
                            date_text = element.text.strip()
                            classes = element.get_attribute("class")
                            
                            # Skip if it looks disabled
                            if "disabled" in classes.lower() or "unavailable" in classes.lower():
                                continue
                            
                            if date_text:
                                appointments.append({
                                    "date": date_text,
                                    "element": element,
                                    "classes": classes
                                })
                        except:
                            continue
                            
                if appointments:
                    break  # Found appointments with this selector
                    
            except:
                continue
        
        if appointments:
            logger.info(f"Found {len(appointments)} potentially available dates")
            save_screenshot(driver, "appointments_found")
        else:
            logger.info("No available appointments found")
        
        return appointments
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}", exc_info=True)
        return []


def check_target_month_appointments(driver: webdriver.Chrome) -> Dict[str, any]:
    """
    Complete flow: navigate to target month and check for appointments.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        Dictionary with results
    """
    result = {
        "success": False,
        "appointments_found": False,
        "appointments": [],
        "message": ""
    }
    
    try:
        # Navigate to scheduling page
        if not navigate_to_scheduling(driver):
            result["message"] = "Failed to navigate to scheduling page"
            return result
        
        # Select consular post
        if not select_consular_post(driver, Config.CONSULAR_POST):
            result["message"] = "Failed to select consular post"
            return result
        
        # Navigate to target month
        if not navigate_to_target_month(driver, Config.TARGET_MONTH, Config.TARGET_YEAR):
            result["message"] = "Failed to navigate to target month"
            return result
        
        # Check availability
        appointments = check_availability(driver)
        
        result["success"] = True
        result["appointments"] = appointments
        result["appointments_found"] = len(appointments) > 0
        result["message"] = f"Found {len(appointments)} available appointments" if appointments else "No appointments available"
        
        return result
        
    except Exception as e:
        logger.error(f"Error in check_target_month_appointments: {e}", exc_info=True)
        result["message"] = f"Error: {str(e)}"
        return result