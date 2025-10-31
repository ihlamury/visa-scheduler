"""
Notification module for US Visa Scheduler.
Handles sending alerts when appointments are found.
"""

import logging
import requests
from typing import List, Dict
from datetime import datetime
from src.config import Config

logger = logging.getLogger("visa_scheduler")


class BaseNotifier:
    """Base class for all notifiers."""
    
    def send(self, message: str, appointments: List[Dict] = None) -> bool:
        """Send notification. Must be implemented by subclasses."""
        raise NotImplementedError


class LogNotifier(BaseNotifier):
    """Log-based notifier (always active)."""
    
    def send(self, message: str, appointments: List[Dict] = None) -> bool:
        """Log the notification message."""
        try:
            logger.info("=" * 70)
            logger.info("🎉 APPOINTMENT NOTIFICATION 🎉")
            logger.info("=" * 70)
            logger.info(message)
            
            if appointments:
                logger.info(f"\nAvailable appointments: {len(appointments)}")
                for i, apt in enumerate(appointments, 1):
                    logger.info(f"  {i}. Date: {apt.get('date', 'Unknown')}")
            
            logger.info("=" * 70)
            return True
        except Exception as e:
            logger.error(f"Error in LogNotifier: {e}")
            return False


class TelegramNotifier(BaseNotifier):
    """Telegram bot notifier."""
    
    def __init__(self):
        self.bot_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            logger.info("Telegram notifications disabled (no credentials)")
    
    def send(self, message: str, appointments: List[Dict] = None) -> bool:
        """Send notification via Telegram."""
        if not self.enabled:
            return False
        
        try:
            # Format the message
            telegram_message = f"🎉 *US Visa Appointment Alert* 🎉\n\n"
            telegram_message += f"{message}\n\n"
            
            if appointments:
                telegram_message += f"*Available Dates ({len(appointments)}):*\n"
                for i, apt in enumerate(appointments[:10], 1):  # Limit to 10
                    telegram_message += f"{i}. {apt.get('date', 'Unknown')}\n"
                
                if len(appointments) > 10:
                    telegram_message += f"\n... and {len(appointments) - 10} more\n"
            
            telegram_message += f"\n🕒 Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            telegram_message += f"\n📍 Location: {Config.CONSULAR_POST}"
            telegram_message += f"\n📅 Target: {Config.TARGET_MONTH}/{Config.TARGET_YEAR}"
            
            # Send via Telegram API
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": telegram_message,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}", exc_info=True)
            return False


class EmailNotifier(BaseNotifier):
    """Email notifier using SMTP."""
    
    def __init__(self):
        self.email = Config.EMAIL_ADDRESS
        self.password = Config.EMAIL_PASSWORD
        self.enabled = bool(self.email and self.password)
        
        if not self.enabled:
            logger.info("Email notifications disabled (no credentials)")
    
    def send(self, message: str, appointments: List[Dict] = None) -> bool:
        """Send notification via email."""
        if not self.enabled:
            return False
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = self.email
            msg['Subject'] = f"🎉 US Visa Appointment Available - {Config.CONSULAR_POST}"
            
            # Email body
            body = f"<h2>US Visa Appointment Alert</h2>\n"
            body += f"<p>{message}</p>\n"
            
            if appointments:
                body += f"<h3>Available Dates ({len(appointments)}):</h3>\n<ul>\n"
                for apt in appointments[:20]:  # Limit to 20
                    body += f"<li>{apt.get('date', 'Unknown')}</li>\n"
                body += "</ul>\n"
                
                if len(appointments) > 20:
                    body += f"<p>... and {len(appointments) - 20} more</p>\n"
            
            body += f"<p><strong>Checked at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>\n"
            body += f"<p><strong>Location:</strong> {Config.CONSULAR_POST}</p>\n"
            body += f"<p><strong>Target:</strong> {Config.TARGET_MONTH}/{Config.TARGET_YEAR}</p>\n"
            
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            # Try Gmail SMTP (most common)
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
                server.quit()
                logger.info("Email notification sent successfully")
                return True
            except Exception as gmail_error:
                logger.warning(f"Gmail SMTP failed: {gmail_error}, trying generic SMTP...")
                
                # Try generic SMTP on port 587
                server = smtplib.SMTP('smtp.mail.yahoo.com', 587)  # Fallback
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
                server.quit()
                logger.info("Email notification sent successfully (fallback)")
                return True
                
        except Exception as e:
            logger.error(f"Error sending email notification: {e}", exc_info=True)
            return False


class NotificationManager:
    """Manages all notification channels."""
    
    def __init__(self):
        self.notifiers = [
            LogNotifier(),  # Always enabled
            TelegramNotifier(),
            EmailNotifier(),
        ]
        
        # Count enabled notifiers
        enabled_count = sum(1 for n in self.notifiers if getattr(n, 'enabled', True))
        logger.info(f"Initialized {enabled_count} notification channels")
    
    def notify(self, message: str, appointments: List[Dict] = None) -> Dict[str, bool]:
        """
        Send notifications through all enabled channels.
        
        Args:
            message: Notification message
            appointments: List of appointment dictionaries
            
        Returns:
            Dictionary with results for each notifier
        """
        results = {}
        
        for notifier in self.notifiers:
            notifier_name = notifier.__class__.__name__
            
            try:
                # Skip if notifier is disabled
                if hasattr(notifier, 'enabled') and not notifier.enabled:
                    results[notifier_name] = False
                    continue
                
                success = notifier.send(message, appointments)
                results[notifier_name] = success
                
            except Exception as e:
                logger.error(f"Error with {notifier_name}: {e}")
                results[notifier_name] = False
        
        return results
    
    def notify_appointments_found(self, appointments: List[Dict]) -> bool:
        """
        Send notification that appointments were found.
        
        Args:
            appointments: List of available appointments
            
        Returns:
            True if at least one notification sent successfully
        """
        message = f"Found {len(appointments)} available appointment(s) for {Config.CONSULAR_POST} in {Config.TARGET_MONTH}/{Config.TARGET_YEAR}!"
        
        results = self.notify(message, appointments)
        
        # Return True if at least one notifier succeeded
        return any(results.values())
    
    def notify_error(self, error_message: str) -> bool:
        """
        Send notification about an error.
        
        Args:
            error_message: Description of the error
            
        Returns:
            True if notification sent successfully
        """
        message = f"⚠️ Visa Scheduler Error: {error_message}"
        
        results = self.notify(message)
        
        return any(results.values())