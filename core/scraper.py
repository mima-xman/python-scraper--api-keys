import asyncio
import json
import random
import string
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from playwright.async_api import async_playwright, Page, Browser
from stem import Signal
from stem.control import Controller

# Import configuration
from config import settings
from core.database import MongoDBManager


def renew_tor_ip(logger=None):
    """Renew TOR IP address by requesting a new circuit."""
    logger = logger if logger else print
    try:
        with Controller.from_port(port=settings.TOR_CONTROL_PORT) as controller:
            controller.authenticate()  # If needed, provide your control password here
            controller.signal(Signal.NEWNYM)
            logger("-> Tor IP renewed.")
            return True
    except Exception as e:
        logger(f"-> Failed to renew Tor IP: {str(e)}")
        return False


class BytezAPIKeyScraper:
    """
    A scraper class to automate the process of creating accounts and
    generating API keys from bytez.com
    """

    def __init__(self, headless: bool = None, accounts_file: str = None):
        """
        Initialize the scraper.

        Args:
            headless: Whether to run browser in headless mode (defaults to settings.HEADLESS_MODE)
            accounts_file: Path to the JSON file to store accounts (defaults to settings.ACCOUNTS_FILE, kept for backward compatibility)
        """
        self.headless = headless if headless is not None else settings.HEADLESS_MODE
        self.accounts_file = Path(accounts_file if accounts_file is not None else settings.ACCOUNTS_FILE)
        self.base_url = settings.BASE_URL
        self.auth_url = settings.AUTH_URL
        self.api_url = settings.API_URL
        self.selectors = settings.SELECTORS
        self.error_images_dir = Path(settings.ERROR_IMAGES_DIR)
        self.use_tor = settings.USE_TOR
        
        # Initialize MongoDB manager
        try:
            self.db_manager = MongoDBManager()
        except Exception as e:
            print(f"\n{'=' * 60}")
            print(f"CRITICAL ERROR: Failed to connect to MongoDB")
            print(f"Error: {str(e)}")
            print(f"{'=' * 60}")
            raise
        
        # Ensure output directories exist
        self.accounts_file.parent.mkdir(parents=True, exist_ok=True)
        self.error_images_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def generate_random_email() -> str:
        """Generate a random email address."""
        username_length = random.randint(settings.EMAIL_USERNAME_MIN_LENGTH, settings.EMAIL_USERNAME_MAX_LENGTH)
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
        return f"{username}@gmail.com"

    @staticmethod
    def generate_random_password() -> str:
        """Generate a random password."""
        length = random.randint(settings.PASSWORD_MIN_LENGTH, settings.PASSWORD_MAX_LENGTH)
        return ''.join(random.choices(settings.PASSWORD_CHARACTERS, k=length))

    async def create_account_and_get_key(self, page: Page) -> Dict[str, str]:
        """
        Create a new account and generate an API key.

        Args:
            page: Playwright page object

        Returns:
            Dictionary containing email, password, and api_key
        """
        email = self.generate_random_email()
        password = self.generate_random_password()

        print(f"Creating account with email: {email}")
        print(f"Password: {password}")

        # Navigate to auth page
        print(f"\n[1/10] Navigating to auth page: {self.auth_url}")
        await page.goto(self.auth_url, wait_until="domcontentloaded")
        current_url = page.url
        print(f"       Current URL: {current_url}")
        
        print(f"[2/10] Waiting for email field selector: {self.selectors['email_field']}")
        await page.wait_for_selector(self.selectors["email_field"], timeout=settings.ELEMENT_TIMEOUT)
        print(f"       ✓ Email field found")

        # Fill in email and password using Playwright methods
        print(f"[3/10] Filling email field")
        await page.fill(self.selectors["email_field"], email)
        print(f"       ✓ Email filled: {email}")
        
        print(f"[4/10] Filling password field")
        await page.fill(self.selectors["password_field"], password)
        print(f"       ✓ Password filled")

        # Click sign in button
        print(f"[5/10] Clicking sign up button")
        await page.click(self.selectors["signin_button"])
        print(f"       ✓ Button clicked")

        # Wait for redirect to dashboard
        print(f"[6/10] Waiting for redirect to dashboard...")
        await page.wait_for_url(self.base_url + "/", timeout=settings.REDIRECT_TIMEOUT)
        current_url = page.url
        print(f"       ✓ Redirected to: {current_url}")

        # Navigate to API page
        print(f"[7/10] Navigating to API page: {self.api_url}")
        await page.goto(self.api_url, wait_until="domcontentloaded")
        current_url = page.url
        print(f"       Current URL: {current_url}")
        
        print(f"[7/10] Waiting for select button")
        await page.wait_for_selector(self.selectors["select_button"], timeout=settings.ELEMENT_TIMEOUT)
        print(f"       ✓ Select button found")

        # Click "Select" button
        print(f"[8/10] Clicking select button")
        await page.click(self.selectors["select_button"])
        print(f"       ✓ Select button clicked")

        # Wait for dialog to appear
        print(f"[8/10] Waiting for radio button in dialog")
        await page.wait_for_selector(self.selectors["radio_button"], timeout=settings.ELEMENT_TIMEOUT)
        print(f"       ✓ Dialog appeared with radio button")

        # Click radio button
        print(f"[8/10] Clicking radio button")
        await page.click(self.selectors["radio_button"])
        print(f"       ✓ Radio button clicked")

        # Click checkbox
        print(f"[8/10] Clicking checkbox")
        await page.click(self.selectors["checkbox"])
        print(f"       ✓ Checkbox clicked")

        # Click first continue button
        print(f"[9/10] Clicking first continue button")
        await page.click(self.selectors["continue_button_1"])
        print(f"       ✓ First continue clicked")

        # Wait for second continue button to appear
        print(f"[9/10] Waiting for second continue button")
        await page.wait_for_selector(self.selectors["continue_button_2"], timeout=settings.ELEMENT_TIMEOUT)
        print(f"       ✓ Second continue button appeared")

        # Click second continue button
        print(f"[9/10] Clicking second continue button")
        await page.click(self.selectors["continue_button_2"])
        print(f"       ✓ Second continue clicked")

        # Wait for dialog to close and page to update
        print(f"[9/10] Waiting for dialog to close...")
        await asyncio.sleep(settings.DIALOG_CLOSE_DELAY)
        print(f"       ✓ Dialog closed")

        # Navigate back to API page to ensure key is displayed
        print(f"[10/10] Navigating back to API page")
        await page.goto(self.api_url, wait_until="domcontentloaded")
        current_url = page.url
        print(f"        Current URL: {current_url}")
        
        print(f"[10/10] Waiting for API key display element")
        await page.wait_for_selector(self.selectors["api_key_display"], timeout=settings.ELEMENT_TIMEOUT)
        print(f"        ✓ API key element found")

        # Extract API key using text_content
        print(f"[10/10] Extracting API key text")
        api_key = await page.text_content(self.selectors["api_key_display"])

        print(f"Successfully generated API key: {api_key[:20]}...")

        return {
            "email": email,
            "password": password,
            "api_key": api_key,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def save_api_key_to_db(self, account: Dict[str, str]):
        """
        Save API key to MongoDB.
        CRITICAL: If save fails, raises exception to stop the scraper.

        Args:
            account: Dictionary containing email, password, api_key, and scraped_at
            
        Raises:
            Exception: If MongoDB save operation fails
        """
        try:
            success = self.db_manager.save_api_key(account)
            if not success:
                raise Exception("MongoDB save operation returned False")
        except Exception as e:
            print(f"\n{'=' * 60}")
            print(f"CRITICAL ERROR: Failed to save API key to MongoDB")
            print(f"Error: {str(e)}")
            print(f"Stopping scraper to prevent data loss...")
            print(f"{'=' * 60}")
            raise

    async def display_countdown(self, seconds: int):
        """
        Display a countdown timer in HH:MM:SS format.
        
        Args:
            seconds: Number of seconds to count down
        """
        print(f"\nPausing for {seconds} seconds due to error/rate limit...")
        try:
            for remaining in range(seconds, 0, -1):
                m, s = divmod(remaining, 60)
                h, m = divmod(m, 60)
                time_str = "{:02d}:{:02d}:{:02d}".format(h, m, s)
                print(f"\rResuming in: {time_str}", end="", flush=True)
                await asyncio.sleep(1)
            print("\rResuming scraping...                    ")  # Clear the line
        except asyncio.CancelledError:
            raise

    async def handle_error_recovery(self):
        """
        Handle error recovery - either renew TOR IP or use countdown timer.
        """
        if self.use_tor:
            print("\n" + "=" * 50)
            print("Renewing TOR IP address...")
            print("=" * 50)
            
            if renew_tor_ip(print):
                # Wait a bit for the new circuit to establish
                print("Waiting for new TOR circuit to establish...")
                await asyncio.sleep(settings.TOR_RENEWAL_WAIT)
                print("Ready to continue.")
            else:
                print("Failed to renew TOR IP, falling back to countdown...")
                await self.display_countdown(settings.RATE_LIMIT_PAUSE_DURATION)
        else:
            # Use countdown timer if TOR is not enabled
            await self.display_countdown(settings.RATE_LIMIT_PAUSE_DURATION)

    async def scrape_keys(self):
        """
        Scrape API keys indefinitely until stopped by user (Ctrl+C).
        """
        async with async_playwright() as p:
            # Select browser based on settings
            browser_type = settings.BROWSER_TYPE.lower()
            if browser_type == 'firefox':
                browser_launcher = p.firefox
            elif browser_type == 'webkit':
                browser_launcher = p.webkit
            else:  # default to chromium
                browser_launcher = p.chromium
            
            # Prepare launch options
            launch_options = {
                'headless': self.headless,
                'args': settings.BROWSER_ARGS
            }
            
            # Add custom executable path if specified
            if settings.BROWSER_EXECUTABLE_PATH:
                launch_options['executable_path'] = settings.BROWSER_EXECUTABLE_PATH
            
            # Add TOR proxy if enabled
            if self.use_tor:
                launch_options['proxy'] = settings.TOR_PROXIES
                print(f"\n{'=' * 50}")
                print(f"TOR Proxy enabled: {settings.TOR_PROXIES['server']}")
                print(f"{'=' * 50}")
            
            browser: Browser = await browser_launcher.launch(**launch_options)

            print(f"\n{'=' * 50}")
            print(f"Starting infinite scraping loop...")
            print(f"Press Ctrl+C to stop the scraper safely")
            print(f"{'=' * 50}")

            i = 0
            try:
                while True:
                    i += 1
                    print(f"\n{'=' * 50}")
                    print(f"Generating API key #{i}")
                    print(f"{'=' * 50}")
                    sys.stdout.flush()  # Ensure logs appear immediately

                    # Create a fresh browser context for each account to ensure isolation
                    context_options = {
                        'viewport': {'width': settings.WINDOW_WIDTH, 'height': settings.WINDOW_HEIGHT},
                        'user_agent': settings.USER_AGENT
                    }
                    
                    # Add proxy to context if using TOR
                    if self.use_tor:
                        context_options['proxy'] = settings.TOR_PROXIES
                    
                    context = await browser.new_context(**context_options)
                    page = await context.new_page()

                    error_occurred = False

                    try:
                        account = await self.create_account_and_get_key(page)
                        self.save_api_key_to_db(account)  # This will raise exception if save fails
                        print(f"\n{'=' * 50}")
                        print(f"✓ Successfully generated and saved API key #{i}")
                        print(f"{'=' * 50}")
                        sys.stdout.flush()  # Ensure success message appears immediately
                    except Exception as e:
                        error_occurred = True
                        print(f"\n{'=' * 50}")
                        print(f"✗ Error generating API key #{i}")
                        print(f"Error type: {type(e).__name__}")
                        print(f"Error message: {str(e)}")
                        try:
                            print(f"Current URL: {page.url}")
                        except:
                            pass
                        
                        # Take screenshot on error for debugging
                        try:
                            screenshot_filename = f"error_screenshot_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                            screenshot_path = self.error_images_dir / screenshot_filename
                            await page.screenshot(path=str(screenshot_path))
                            print(f"Screenshot saved: {screenshot_path}")
                        except:
                            pass
                        
                        print(f"{'=' * 50}")
                        
                        # Handle error recovery (TOR renewal or countdown)
                        await self.handle_error_recovery()
                        
                    finally:
                        # Close context to clear all cookies and session data
                        await context.close()

                    # Small delay between requests (if no error occurred)
                    # If error occurred, we already waited heavily
                    if not error_occurred:
                        await asyncio.sleep(settings.DELAY_BETWEEN_REQUESTS)

            except KeyboardInterrupt:
                print("\n\nStopping scraper due to KeyboardInterrupt...")
            finally:
                await browser.close()

        print(f"\n{'=' * 50}")
        print(f"Scraping session ended. Total attempts: {i}")
        print(f"{'=' * 50}")