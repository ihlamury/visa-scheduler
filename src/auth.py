"""
Authentication module for US Visa Scheduler.
Handles login and security questions.
"""

import time
import logging
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.config import Config
from src.utils import save_screenshot

logger = logging.getLogger("visa_scheduler")


def handle_cloudflare_challenge(driver: webdriver.Chrome, timeout: int = 30) -> bool:
    """
    Handle Cloudflare security challenge by automatically clicking the checkbox.

    Args:
        driver: Selenium WebDriver instance
        timeout: Maximum seconds to wait for challenge to complete

    Returns:
        True if challenge passed, False otherwise
    """
    try:
        logger.info("Checking for Cloudflare challenge...")

        # Check if we're on Cloudflare challenge page
        if "verify you are human" in driver.page_source.lower() or "cloudflare" in driver.page_source.lower():
            logger.info("Cloudflare challenge detected! Attempting to solve automatically...")
            save_screenshot(driver, "cloudflare_challenge_detected")

            # Try to find and click the Cloudflare checkbox
            import time
            time.sleep(2)  # Wait for iframe to load

            try:
                # Cloudflare checkbox is usually in an iframe
                logger.info("Looking for Cloudflare iframe...")

                # Find all iframes
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                logger.info(f"Found {len(iframes)} iframes")

                for idx, iframe in enumerate(iframes):
                    try:
                        # Switch to iframe
                        driver.switch_to.frame(iframe)
                        logger.info(f"Switched to iframe {idx}")

                        # Try to find the checkbox
                        checkbox_selectors = [
                            (By.CSS_SELECTOR, "input[type='checkbox']"),
                            (By.CSS_SELECTOR, "#challenge-stage input"),
                            (By.XPATH, "//input[@type='checkbox']"),
                            (By.CSS_SELECTOR, "label input"),
                        ]

                        for by, selector in checkbox_selectors:
                            try:
                                checkbox = driver.find_element(by, selector)
                                if checkbox.is_displayed():
                                    logger.info(f"Found checkbox with selector: {selector}")
                                    # Click it
                                    checkbox.click()
                                    logger.info("✓ Clicked Cloudflare checkbox!")
                                    save_screenshot(driver, "cloudflare_checkbox_clicked")

                                    # Switch back to main content
                                    driver.switch_to.default_content()
                                    break
                            except:
                                continue

                        # Switch back to main content
                        driver.switch_to.default_content()

                    except Exception as e:
                        logger.debug(f"Error checking iframe {idx}: {e}")
                        driver.switch_to.default_content()
                        continue

            except Exception as e:
                logger.warning(f"Could not find/click checkbox automatically: {e}")

            # Now wait for the challenge to complete
            logger.info(f"Waiting up to {timeout} seconds for challenge to resolve...")

            for i in range(timeout):
                time.sleep(1)

                # Check if we're past the challenge (login page loaded)
                if "signInName" in driver.page_source or "password" in driver.page_source:
                    logger.info("✓ Cloudflare challenge passed!")
                    save_screenshot(driver, "cloudflare_passed")
                    return True

                # Check if still on Cloudflare page
                if i % 5 == 0 and i > 0:
                    logger.info(f"Still waiting for challenge to complete... {timeout - i}s remaining")

            # Timeout
            logger.error("Cloudflare challenge not completed in time")
            save_screenshot(driver, "cloudflare_timeout")
            return False
        else:
            logger.info("No Cloudflare challenge detected")
            return True

    except Exception as e:
        logger.error(f"Error handling Cloudflare challenge: {e}", exc_info=True)
        return False


def login(driver: webdriver.Chrome, username: str, password: str) -> bool:
    """
    Perform login on the visa scheduling website.
    
    Args:
        driver: Selenium WebDriver instance
        username: Login username
        password: Login password
        
    Returns:
        True if login successful, False otherwise
    """
    try:
        logger.info("Navigating to login page...")
        driver.get(Config.BASE_URL)

        # Wait for initial page load
        time.sleep(3)

        # Handle Cloudflare challenge if present (should be bypassed with undetected-chromedriver)
        if not handle_cloudflare_challenge(driver, timeout=20):
            logger.error("Failed to pass Cloudflare challenge")
            save_screenshot(driver, "cloudflare_failed")
            return False

        # Wait for page to load
        wait = WebDriverWait(driver, 15)

        # Wait for username field
        logger.info("Waiting for login form...")
        username_field = wait.until(
            EC.presence_of_element_located((By.ID, "signInName"))
        )
        
        # Fill in username
        logger.info(f"Entering username: {username}")
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(0.5)
        
        # Fill in password
        logger.info("Entering password...")
        password_field = driver.find_element(By.ID, "password")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(0.5)
        
        # Handle captcha
        captcha_solved = handle_captcha(driver)
        if not captcha_solved:
            logger.warning("Captcha not solved, but continuing...")
        
        # Take screenshot before submitting
        save_screenshot(driver, "before_login_submit")
        
        # Click sign in button
        logger.info("Clicking Sign In button...")
        sign_in_button = driver.find_element(By.ID, "continue")
        sign_in_button.click()
        
        # Wait a bit for the page to process
        time.sleep(3)
        
        # Check if login was successful by looking for security questions or error
        try:
            # If we see security questions, login was successful
            wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Security Question')]"))
            )
            logger.info("Login successful! Security questions page loaded.")
            save_screenshot(driver, "login_success")
            return True
        except TimeoutException:
            # Check if we're still on login page (error)
            try:
                error_msg = driver.find_element(By.CLASS_NAME, "error")
                logger.error(f"Login failed: {error_msg.text}")
                save_screenshot(driver, "login_failed")
                return False
            except NoSuchElementException:
                # No error message, might have logged in successfully
                logger.info("Login appears successful (no error message)")
                save_screenshot(driver, "after_login")
                return True
                
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        save_screenshot(driver, "login_error")
        return False


def handle_captcha(driver: webdriver.Chrome) -> bool:
    """
    Handle the captcha on the login page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if captcha was solved, False otherwise
    """
    try:
        # Look for captcha input field
        captcha_field = driver.find_element(By.ID, "extension_atlasCaptchaResponse")
        
        if captcha_field.is_displayed():
            logger.info("Captcha detected!")
            
            # Try to get the captcha image for reference
            try:
                captcha_img = driver.find_element(By.ID, "captchaImage")
                logger.info("Captcha image found")
                save_screenshot(driver, "captcha_to_solve")
            except NoSuchElementException:
                logger.warning("Could not find captcha image element")
            
            # For now, we'll do manual captcha entry
            logger.warning("=" * 60)
            logger.warning("CAPTCHA DETECTED - MANUAL ENTRY REQUIRED")
            logger.warning("Please look at the browser window and enter the captcha")
            logger.warning("Waiting 60 seconds for manual entry...")
            logger.warning("=" * 60)
            
            # Wait for user to enter captcha
            time.sleep(60)
            
            # Check if captcha was filled
            captcha_value = captcha_field.get_attribute("value")
            if captcha_value:
                logger.info("Captcha appears to be filled")
                return True
            else:
                logger.warning("Captcha field still empty after wait")
                return False
        else:
            logger.info("No captcha required")
            return True
            
    except NoSuchElementException:
        logger.info("No captcha field found")
        return True
    except Exception as e:
        logger.error(f"Error handling captcha: {e}")
        return False


def answer_security_questions(driver: webdriver.Chrome) -> bool:
    """
    Answer the security questions on the login page.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if questions answered successfully, False otherwise
    """
    try:
        logger.info("Handling security questions...")
        wait = WebDriverWait(driver, 15)
        
        # Wait for the security questions page to load
        time.sleep(2)
        
        # Find all question labels and input fields
        # The structure varies, so we'll try multiple approaches
        
        # Method 1: Look for labels with "Security Question" text
        try:
            # Find all text elements that might contain questions
            question_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'question') or contains(@id, 'question')]")
            
            if not question_elements:
                # Try finding by label tags
                question_elements = driver.find_elements(By.TAG_NAME, "label")
            
            logger.info(f"Found {len(question_elements)} potential question elements")
            
            # Find all text input fields (these are likely the answer fields)
            input_fields = driver.find_elements(By.XPATH, "//input[@type='text' or @type='password']")
            logger.info(f"Found {len(input_fields)} input fields")
            
            # Process each question
            questions_answered = 0
            
            for i, question_elem in enumerate(question_elements):
                question_text = question_elem.text.strip()
                
                if not question_text or len(question_text) < 5:
                    continue
                
                logger.info(f"Question {i+1}: {question_text}")
                
                # Get the answer for this question
                answer = Config.get_security_answer(question_text)
                
                if answer:
                    logger.info(f"Found answer for question {i+1}")
                    
                    # Try to find the associated input field
                    # Usually it's the next input field after the question
                    if questions_answered < len(input_fields):
                        input_field = input_fields[questions_answered]
                        input_field.clear()
                        input_field.send_keys(answer)
                        logger.info(f"Filled answer for question {i+1}")
                        questions_answered += 1
                        time.sleep(0.5)
                else:
                    logger.warning(f"No answer configured for question: {question_text}")
            
            if questions_answered >= 2:
                logger.info(f"Successfully filled {questions_answered} security answers")
                
                # Take screenshot before submitting
                save_screenshot(driver, "security_questions_filled")
                
                # Find and click the Continue button
                logger.info("Looking for Continue button...")
                continue_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')] | //input[@value='Continue']"))
                )
                
                logger.info("Clicking Continue button...")
                continue_button.click()
                time.sleep(3)
                
                # Verify we moved to the next page
                save_screenshot(driver, "after_security_questions")
                logger.info("Security questions submitted successfully")
                return True
            else:
                logger.error(f"Only answered {questions_answered} questions, need at least 2")
                save_screenshot(driver, "security_questions_incomplete")
                return False
                
        except TimeoutException:
            logger.error("Timeout waiting for security questions elements")
            save_screenshot(driver, "security_questions_timeout")
            return False
            
    except Exception as e:
        logger.error(f"Error answering security questions: {e}", exc_info=True)
        save_screenshot(driver, "security_questions_error")
        return False


def verify_logged_in(driver: webdriver.Chrome) -> bool:
    """
    Verify that we are successfully logged in.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if logged in, False otherwise
    """
    try:
        # Check for elements that indicate we're logged in
        # Could be user profile, schedule appointment button, etc.
        wait = WebDriverWait(driver, 10)
        
        # Look for common logged-in indicators
        indicators = [
            (By.XPATH, "//*[contains(text(), 'Schedule Appointment')]"),
            (By.XPATH, "//*[contains(text(), 'Visa Application Home')]"),
            (By.XPATH, "//*[contains(text(), 'Manage Applications')]"),
        ]
        
        for by, selector in indicators:
            try:
                element = wait.until(EC.presence_of_element_located((by, selector)))
                logger.info(f"Found logged-in indicator: {element.text}")
                return True
            except TimeoutException:
                continue
        
        logger.warning("Could not find definitive logged-in indicator")
        return False
        
    except Exception as e:
        logger.error(f"Error verifying login status: {e}")
        return False


def full_authentication(driver: webdriver.Chrome) -> bool:
    """
    Perform complete authentication flow: login + security questions.
    
    Args:
        driver: Selenium WebDriver instance
        
    Returns:
        True if fully authenticated, False otherwise
    """
    logger.info("Starting full authentication process...")
    
    # Step 1: Login
    if not login(driver, Config.USERNAME, Config.PASSWORD):
        logger.error("Login failed")
        return False
    
    # Step 2: Answer security questions
    if not answer_security_questions(driver):
        logger.error("Failed to answer security questions")
        return False
    
    # Step 3: Verify we're logged in
    if not verify_logged_in(driver):
        logger.warning("Could not verify login status, but continuing...")
    
    logger.info("Full authentication complete!")
    return True