"""
US Visa Appointment Scheduler - Main Entry Point
"""

import sys
import time
from src.config import Config
from src.utils import setup_logger, get_random_wait_time, setup_driver
from src.auth import full_authentication
from src.appointment_checker import check_target_month_appointments
from src.notifier import NotificationManager

# Initialize logger
logger = setup_logger()


def check_appointments_once() -> bool:
    """
    Perform one complete check for appointments.
    
    Returns:
        True if check completed successfully, False otherwise
    """
    driver = None
    
    try:
        logger.info("Initializing Chrome WebDriver...")
        driver = setup_driver()
        
        # Step 1: Authenticate
        logger.info("Step 1/3: Authenticating...")
        if not full_authentication(driver):
            logger.error("Authentication failed")
            return False
        
        logger.info("Authentication successful!")
        time.sleep(2)
        
        # Step 2: Check appointments
        logger.info("Step 2/3: Checking appointments...")
        result = check_target_month_appointments(driver)
        
        if not result["success"]:
            logger.error(f"Appointment check failed: {result['message']}")
            return False
        
        # Step 3: Handle results
        logger.info("Step 3/3: Processing results...")
        
        if result["appointments_found"]:
            logger.info("🎉 " + "=" * 56 + " 🎉")
            logger.info("🎉 APPOINTMENTS AVAILABLE! 🎉")
            logger.info("🎉 " + "=" * 56 + " 🎉")
            
            # Send notifications
            notifier = NotificationManager()
            notifier.notify_appointments_found(result["appointments"])
            
            logger.info(f"Found {len(result['appointments'])} available appointment(s)")
        else:
            logger.info("No appointments available at this time")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during check: {e}", exc_info=True)
        return False
        
    finally:
        # Always clean up the driver
        if driver:
            try:
                logger.info("Closing browser...")
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing driver: {e}")


def run_continuous_monitoring():
    """Run the scheduler in continuous monitoring mode."""
    logger.info("Starting continuous monitoring mode...")
    logger.info(f"Target: {Config.CONSULAR_POST} - {Config.TARGET_MONTH}/{Config.TARGET_YEAR}")
    logger.info(f"Check interval: {Config.CHECK_INTERVAL_MIN}-{Config.CHECK_INTERVAL_MAX} minutes")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    check_count = 0
    
    while True:
        try:
            check_count += 1
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"Starting check #{check_count}")
            logger.info("=" * 60)
            
            # Perform the check
            success = check_appointments_once()
            
            if success:
                logger.info(f"Check #{check_count} completed successfully")
            else:
                logger.warning(f"Check #{check_count} completed with errors")
            
            # Calculate wait time
            wait_seconds = get_random_wait_time()
            wait_minutes = wait_seconds // 60
            
            logger.info("")
            logger.info("=" * 60)
            logger.info(f"Next check in {wait_minutes} minutes ({wait_seconds} seconds)")
            logger.info(f"Next check will be check #{check_count + 1}")
            logger.info("=" * 60)
            
            # Wait
            time.sleep(wait_seconds)
            
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 60)
            logger.info("Monitoring stopped by user")
            logger.info(f"Total checks performed: {check_count}")
            logger.info("=" * 60)
            break
        except Exception as e:
            logger.error(f"Unexpected error in monitoring loop: {e}", exc_info=True)
            logger.info("Waiting 5 minutes before retry...")
            time.sleep(300)  # Wait 5 minutes on error


def main():
    """Main execution function."""
    try:
        logger.info("=" * 60)
        logger.info("US Visa Appointment Scheduler")
        logger.info("=" * 60)
        
        # Validate configuration
        Config.validate()
        logger.info("✓ Configuration validated successfully")
        logger.info(f"✓ Target: {Config.CONSULAR_POST} - {Config.TARGET_MONTH}/{Config.TARGET_YEAR}")
        logger.info(f"✓ Check interval: {Config.CHECK_INTERVAL_MIN}-{Config.CHECK_INTERVAL_MAX} minutes")
        logger.info(f"✓ Browser mode: {'Headless' if Config.HEADLESS else 'Visible'}")
        
        # Ask user for mode
        print("\n" + "=" * 60)
        print("Select mode:")
        print("1. Single check (run once)")
        print("2. Continuous monitoring (run every 50-70 minutes)")
        print("=" * 60)
        
        choice = input("Enter choice (1 or 2) [default: 2]: ").strip() or "2"
        
        if choice == "1":
            logger.info("Running single check mode...")
            success = check_appointments_once()
            if success:
                logger.info("Check completed successfully!")
            else:
                logger.error("Check failed. See logs for details.")
                sys.exit(1)
        else:
            run_continuous_monitoring()
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required values are set")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()