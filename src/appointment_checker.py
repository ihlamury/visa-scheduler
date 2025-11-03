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

        # Take screenshot of the dashboard
        save_screenshot(driver, "logged_in_dashboard")

        # Wait for page to load
        time.sleep(2)

        # Scroll down to make sure buttons are visible
        logger.info("Scrolling down to find appointment buttons...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")
        time.sleep(1)

        wait = WebDriverWait(driver, 20)

        # Look for "Reschedule Appointment" link/button (or "Schedule Appointment" as fallback)
        schedule_selectors = [
            (By.XPATH, "//a[contains(text(), 'Reschedule Appointment')]"),
            (By.XPATH, "//button[contains(text(), 'Reschedule Appointment')]"),
            (By.LINK_TEXT, "Reschedule Appointment"),
            (By.PARTIAL_LINK_TEXT, "Reschedule"),
            # Try case-insensitive
            (By.XPATH, "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'reschedule')]"),
            # Fallback to Schedule Appointment
            (By.XPATH, "//a[contains(text(), 'Schedule Appointment')]"),
            (By.XPATH, "//button[contains(text(), 'Schedule Appointment')]"),
            (By.LINK_TEXT, "Schedule Appointment"),
            (By.PARTIAL_LINK_TEXT, "Schedule"),
            # Try continue/proceed buttons
            (By.XPATH, "//a[contains(text(), 'Continue')]"),
            (By.XPATH, "//button[contains(text(), 'Continue')]"),
        ]

        for by, selector in schedule_selectors:
            try:
                logger.info(f"Trying selector: {selector}")
                schedule_button = wait.until(
                    EC.element_to_be_clickable((by, selector))
                )
                logger.info(f"✓ Found button using: {selector}")

                # Scroll to the button to make sure it's visible
                driver.execute_script("arguments[0].scrollIntoView(true);", schedule_button)
                time.sleep(1)

                schedule_button.click()
                logger.info("Clicked appointment button")
                time.sleep(3)

                save_screenshot(driver, "after_clicking_appointment_button")
                logger.info("Successfully navigated to scheduling page")
                return True
            except TimeoutException:
                continue
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue

        logger.error("Could not find Schedule/Reschedule Appointment button")
        logger.info("Taking screenshot and dumping page source...")
        save_screenshot(driver, "schedule_button_not_found")

        # Log all links on the page for debugging
        try:
            all_links = driver.find_elements(By.TAG_NAME, "a")
            logger.info(f"Found {len(all_links)} links on page:")
            for link in all_links[:20]:  # Log first 20 links
                text = link.text.strip()
                if text:
                    logger.info(f"  Link: {text}")
        except:
            pass

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
    Navigate the calendar to the target month and year using dropdown selectors.

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

        # Month names for mapping
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        target_month_name = month_names[target_month - 1]

        # Method 1: Try to find month and year dropdowns
        try:
            logger.info("Looking for month dropdown...")
            # Find the month dropdown (usually a <select> element)
            month_dropdown = None
            month_selectors = [
                (By.XPATH, "//select[contains(@class, 'month') or contains(@id, 'month')]"),
                (By.XPATH, "//select[option[contains(text(), 'Jan') or contains(text(), 'Feb')]]"),
                (By.XPATH, "//select[1]"),  # First select element
            ]

            for by, selector in month_selectors:
                try:
                    month_dropdown = driver.find_element(by, selector)
                    logger.info(f"Found month dropdown with selector: {selector}")
                    break
                except:
                    continue

            if month_dropdown:
                # Select the target month
                month_select = Select(month_dropdown)
                logger.info(f"Selecting month: {target_month_name}")
                try:
                    month_select.select_by_visible_text(target_month_name)
                except:
                    # Try with full month name
                    full_month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                                       'July', 'August', 'September', 'October', 'November', 'December']
                    month_select.select_by_visible_text(full_month_names[target_month - 1])

                logger.info(f"✓ Month set to: {target_month_name}")
                time.sleep(1)

            # Find the year dropdown
            logger.info("Looking for year dropdown...")
            year_dropdown = None
            year_selectors = [
                (By.XPATH, "//select[contains(@class, 'year') or contains(@id, 'year')]"),
                (By.XPATH, "//select[option[contains(text(), '202')]]"),
                (By.XPATH, "//select[2]"),  # Second select element
            ]

            for by, selector in year_selectors:
                try:
                    year_dropdown = driver.find_element(by, selector)
                    logger.info(f"Found year dropdown with selector: {selector}")
                    break
                except:
                    continue

            if year_dropdown:
                # Select the target year
                year_select = Select(year_dropdown)
                logger.info(f"Selecting year: {target_year}")
                year_select.select_by_visible_text(str(target_year))
                logger.info(f"✓ Year set to: {target_year}")
                time.sleep(2)  # Wait for calendar to reload

                save_screenshot(driver, f"calendar_{target_month}_{target_year}")
                logger.info(f"✓ Successfully navigated to {target_month_name} {target_year}")
                return True
            else:
                logger.warning("Could not find year dropdown")

        except Exception as e:
            logger.warning(f"Dropdown method failed: {e}")

        # Method 2: Fallback to clicking next/previous buttons (old method)
        logger.info("Trying fallback method with next/previous buttons...")
        max_clicks = 24
        clicks = 0

        while clicks < max_clicks:
            current_month_text = get_current_calendar_month(driver)

            if not current_month_text:
                logger.error("Could not determine current calendar month")
                return False

            logger.info(f"Current calendar shows: {current_month_text}")

            if is_target_month(current_month_text, target_month, target_year):
                logger.info("Reached target month!")
                save_screenshot(driver, f"calendar_{target_month}_{target_year}")
                return True

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

        # Take a screenshot to see calendar state
        save_screenshot(driver, "checking_availability")

        # Look for date cells that are NOT disabled/grayed out
        # Available dates typically don't have 'disabled' class and are clickable
        date_selectors = [
            # Look for <td> or <a> elements that don't have 'disabled' class
            (By.XPATH, "//td[not(contains(@class, 'disabled')) and not(contains(@class, 'ui-state-disabled'))]//a"),
            (By.XPATH, "//td[contains(@class, 'available')]//a"),
            (By.XPATH, "//a[contains(@class, 'ui-state-default') and not(contains(@class, 'ui-state-disabled'))]"),
            # Try finding by data attributes
            (By.XPATH, "//td[@data-handler='selectDay' and not(contains(@class, 'disabled'))]"),
            # Generic clickable dates
            (By.XPATH, "//td[not(contains(@class, 'disabled'))]//a[contains(@href, '#')]"),
        ]

        for by, selector in date_selectors:
            try:
                date_elements = driver.find_elements(by, selector)
                logger.info(f"Found {len(date_elements)} date elements with selector: {selector}")

                for element in date_elements:
                    try:
                        # Check if visible and enabled
                        if not element.is_displayed():
                            continue

                        # Get date information
                        date_text = element.text.strip()
                        classes = element.get_attribute("class") or ""
                        parent_classes = ""

                        # Also check parent <td> classes
                        try:
                            parent = element.find_element(By.XPATH, "..")
                            parent_classes = parent.get_attribute("class") or ""
                        except:
                            pass

                        # Skip if disabled
                        if "disabled" in classes.lower() or "disabled" in parent_classes.lower():
                            continue
                        if "ui-state-disabled" in classes or "ui-state-disabled" in parent_classes:
                            continue

                        if date_text and date_text.isdigit():
                            appointments.append({
                                "date": date_text,
                                "element": element,
                                "classes": classes,
                                "parent_classes": parent_classes
                            })
                            logger.info(f"  Found available date: {date_text}")
                    except Exception as e:
                        logger.debug(f"Error processing date element: {e}")
                        continue

                if appointments:
                    break  # Found appointments with this selector

            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue

        if appointments:
            logger.info(f"✓ Found {len(appointments)} available dates")
            save_screenshot(driver, "appointments_found")
        else:
            logger.info("No available appointments found in December 2025")
            logger.info("All dates appear to be unavailable/grayed out")

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