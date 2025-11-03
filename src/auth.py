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
                                    # Wait 2 seconds before clicking to appear more human
                                    logger.info("Waiting 2 seconds before clicking...")
                                    time.sleep(2)
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
            
            # Wait for user to enter captcha, but check periodically if we moved forward
            for i in range(60):
                time.sleep(1)

                # Check if we've moved to security questions page
                if "security question" in driver.page_source.lower():
                    logger.info("✓ Detected security questions page - captcha was solved!")
                    return True

                # Check if captcha was filled
                captcha_value = captcha_field.get_attribute("value")
                if captcha_value and len(captcha_value) > 0:
                    if i % 10 == 0 and i > 0:
                        logger.info(f"Captcha filled, waiting for page transition... ({60-i}s remaining)")

            # After 60 seconds, check one more time
            if "security question" in driver.page_source.lower():
                logger.info("✓ Captcha solved - moved to security questions")
                return True

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
        time.sleep(3)

        # Take a screenshot to see what we're working with
        save_screenshot(driver, "security_questions_page")

        # Log the page source to help debug
        logger.info("Checking page content for security questions...")
        page_text = driver.page_source.lower()

        if "security question" in page_text:
            logger.info("✓ Security questions page detected")
        else:
            logger.warning("Security questions text not found in page")

        # Try multiple methods to find questions and answers

        # Method 1: Find all text with question marks (actual questions)
        logger.info("Method 1: Looking for text with question marks...")

        # IMPORTANT: Find only input fields that are NOT the username field
        # The username field is typically the first one and is disabled after login
        # Security question inputs are usually not disabled
        all_inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='password']")
        logger.info(f"Found {len(all_inputs)} total input fields")

        # Filter out disabled/readonly inputs (like username after login)
        inputs = []
        for inp in all_inputs:
            is_disabled = inp.get_attribute("disabled")
            is_readonly = inp.get_attribute("readonly")
            if not is_disabled and not is_readonly:
                inputs.append(inp)

        logger.info(f"Found {len(inputs)} enabled input fields (excluding username)")

        # Look for ALL text containing "?" which indicates actual questions
        all_text_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '?')]")
        logger.info(f"Found {len(all_text_elements)} elements with question marks")

        questions_found = []
        seen_questions = set()

        for elem in all_text_elements:
            text = elem.text.strip()
            # Look for text that looks like a complete question
            # Skip very long text (>200 chars) - likely instructional text
            if text and 10 < len(text) < 200 and text not in seen_questions:
                # Skip navigation or unrelated text
                if not any(skip in text.lower() for skip in ['terms and', 'registered users', 'new users', 'logging in here', 'forgot your password']):
                    # Extract lines with "?"
                    for line in text.split('\n'):
                        line = line.strip()
                        if '?' in line and 10 < len(line) < 200 and line not in seen_questions:
                            # Skip label-only text like "Security Question 1*"
                            if not (line.startswith("Security Question") and line.count(' ') < 3):
                                questions_found.append(line)
                                seen_questions.add(line)
                                logger.info(f"Found question: {line}")

        if not questions_found:
            logger.info("Method 2: Looking for all labels...")
            # Get all labels (questions might be in labels)
            labels = driver.find_elements(By.TAG_NAME, "label")
            logger.info(f"Found {len(labels)} label elements")

            for label in labels:
                text = label.text.strip()
                if text and len(text) > 10:
                    questions_found.append(text)
                    logger.info(f"Found potential question from label: {text}")

        if not questions_found:
            logger.error("Could not find any security questions on the page")
            save_screenshot(driver, "no_questions_found")
            return False

        # Now match questions with answers
        logger.info(f"Processing {len(questions_found)} questions...")
        questions_answered = 0
        unanswerable_questions = []

        for idx, question_text in enumerate(questions_found):
            logger.info(f"Question {idx+1}: {question_text}")

            # Get the answer for this question
            answer = Config.get_security_answer(question_text)

            if answer:
                logger.info(f"✓ Found matching answer for question {idx+1}")

                # Fill the corresponding input field
                if questions_answered < len(inputs):
                    try:
                        input_field = inputs[questions_answered]
                        input_field.clear()
                        input_field.send_keys(answer)
                        logger.info(f"✓ Filled answer for question {idx+1}")
                        questions_answered += 1
                        time.sleep(0.5)
                    except Exception as e:
                        logger.error(f"Error filling answer {idx+1}: {e}")
                else:
                    logger.warning(f"No input field available for question {idx+1}")
            else:
                logger.warning(f"⚠️  No matching answer found for: {question_text}")
                unanswerable_questions.append(question_text)

        # Check if we have unanswerable questions - need to retry
        if len(unanswerable_questions) > 0 and questions_answered < 2:
            logger.warning("=" * 60)
            logger.warning("Got security questions we don't have answers for:")
            for q in unanswerable_questions:
                logger.warning(f"  - {q}")
            logger.warning("Clicking Cancel to retry with different questions...")
            logger.warning("=" * 60)

            # Click Cancel button to go back
            cancel_selectors = [
                (By.XPATH, "//button[contains(text(), 'Cancel')]"),
                (By.XPATH, "//a[contains(text(), 'Cancel')]"),
                (By.ID, "cancel"),
                (By.NAME, "cancel"),
                (By.XPATH, "//button[@type='button' and not(contains(text(), 'Continue'))]"),
            ]

            for by, selector in cancel_selectors:
                try:
                    cancel_button = driver.find_element(by, selector)
                    if cancel_button.is_displayed():
                        logger.info(f"Found Cancel button with: {selector}")
                        cancel_button.click()
                        logger.info("Clicked Cancel - going back to retry")
                        time.sleep(2)
                        save_screenshot(driver, "clicked_cancel_retry")
                        return "RETRY"  # Special return code for retry
                except:
                    continue

            logger.error("Could not find Cancel button to retry")
            save_screenshot(driver, "no_cancel_button")
            return False

        if questions_answered >= 2:
            logger.info(f"✓ Successfully filled {questions_answered} security answers")

            # Take screenshot before submitting
            save_screenshot(driver, "security_questions_filled")

            # Find and click the Continue button
            logger.info("Looking for Continue button...")

            continue_selectors = [
                (By.XPATH, "//button[contains(text(), 'Continue')]"),
                (By.XPATH, "//input[@value='Continue']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.ID, "continue"),
                (By.NAME, "continue"),
            ]

            continue_button = None
            for by, selector in continue_selectors:
                try:
                    continue_button = driver.find_element(by, selector)
                    if continue_button.is_displayed():
                        logger.info(f"Found Continue button with: {selector}")
                        break
                except:
                    continue

            if continue_button:
                logger.info("Clicking Continue button...")
                continue_button.click()
                time.sleep(3)

                # Verify we moved to the next page
                save_screenshot(driver, "after_security_questions")
                logger.info("✓ Security questions submitted successfully")
                return True
            else:
                logger.error("Could not find Continue button")
                save_screenshot(driver, "no_continue_button")
                return False
        else:
            logger.error(f"⚠️  Only answered {questions_answered} questions, need at least 2")
            save_screenshot(driver, "security_questions_incomplete")
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
    Will retry if security questions we don't know appear.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        True if fully authenticated, False otherwise
    """
    logger.info("Starting full authentication process...")

    max_retries = 10  # Maximum retries for getting answerable security questions
    attempt = 0

    while attempt < max_retries:
        attempt += 1

        if attempt > 1:
            logger.info(f"Retry attempt {attempt}/{max_retries} for answerable security questions...")

        # Step 1: Login
        if not login(driver, Config.USERNAME, Config.PASSWORD):
            logger.error("Login failed")
            return False

        # Step 2: Answer security questions
        result = answer_security_questions(driver)

        if result == "RETRY":
            # Got unanswerable questions, need to retry
            logger.warning(f"Attempt {attempt}: Got unanswerable questions, retrying...")
            time.sleep(2)
            # Loop will retry login from the beginning
            continue
        elif result:
            # Successfully answered questions
            logger.info(f"✓ Security questions answered on attempt {attempt}")
            break
        else:
            # Error occurred
            logger.error("Failed to answer security questions")
            return False

    if attempt >= max_retries:
        logger.error(f"Failed to get answerable security questions after {max_retries} attempts")
        return False

    # Step 3: Verify we're logged in
    if not verify_logged_in(driver):
        logger.warning("Could not verify login status, but continuing...")

    logger.info("Full authentication complete!")
    return True