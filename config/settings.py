"""
Configuration file for Bytez API Key Scraper
Update these settings as needed for your scraping requirements
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== MONGODB CONFIGURATION ====================

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "bytez_keys_manager")
MONGODB_COLLECTION = "api_keys"

# ==================== SCRAPER CONFIGURATION ====================

# Scraper name - used to identify this scraper instance
SCRAPER_NAME = os.getenv("SCRAPER_NAME", "bytez_api_keys_scraper")

# Optional: Scraper ID to reuse an existing scraper
# If not provided or scraper doesn't exist, a new one will be created
SCRAPER_ID = os.getenv("SCRAPER_ID", None)

# ==================== TOR Configuration ====================

USE_TOR = False  # Set to False to disable TOR
TOR_PROXIES = {
    "server": "socks5://127.0.0.1:9150"
}
TOR_CONTROL_PORT = 9151  # Default TOR control port
TOR_RENEWAL_WAIT = 5  # Seconds to wait after renewing TOR IP

# ==================== SCRAPER SETTINGS ====================

# Number of API keys to generate per run
NUM_KEYS_TO_SCRAPE = 50

# Run browser in headless mode (True = invisible, False = visible)
HEADLESS_MODE = True

# Output directory and files
OUTPUT_DIR = BASE_DIR / "output"
ACCOUNTS_FILE = OUTPUT_DIR / "accounts.json"
ERROR_IMAGES_DIR = OUTPUT_DIR / "error_images"

# Browser window size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600


# ==================== URL CONFIGURATION ====================

BASE_URL = "https://bytez.com"
AUTH_URL = f"{BASE_URL}/auth"
API_URL = f"{BASE_URL}/api"


# ==================== TIMEOUT SETTINGS ====================

# Timeout for waiting for elements to appear (in milliseconds)
ELEMENT_TIMEOUT = 1000 * 60

# Timeout for page redirects (in milliseconds)
REDIRECT_TIMEOUT = 1000 * 15

# Delay after dialog operations (in seconds)
DIALOG_CLOSE_DELAY = 2

# Delay between key generation attempts (in seconds)
DELAY_BETWEEN_REQUESTS = 5

# Pause duration when rate limit/error occurs (in seconds)
# Default: 10 minutes = 600 seconds
RATE_LIMIT_PAUSE_DURATION = 600


# ==================== CSS SELECTORS ====================
# Update these if the website structure changes

SELECTORS = {
    # Authentication page
    "email_field": "input[type='email']",
    "password_field": "input[type='password']",
    "signin_button": "body > div.MuiBox-root.mui-k008qs > div.MuiContainer-root.MuiContainer-maxWidthMedium.mui-115wm5w > div > div.MuiStack-root.mui-1i4rabj > span > button",
    
    # API page
    "select_button": "body > div.MuiBox-root.mui-k008qs > div.MuiStack-root.mui-wmvkia > div.MuiStack-root.mui-1ytwwlm > div > div > div:nth-child(1) > span > button",
    "api_key_display": "body > div.MuiBox-root.mui-k008qs > div.MuiStack-root.mui-wmvkia > div.MuiStack-root.mui-1ytwwlm > div.MuiContainer-root.MuiContainer-maxWidthExpanded.mui-1oaggd7 > div > div.MuiStack-root.mui-pg091t > div > div > div",
    
    # Dialog elements
    "radio_button": "body > div.MuiDialog-root.MuiModal-root.mui-ttaiqw > div.MuiDialog-container.MuiDialog-scrollPaper.mui-1dujj47 > div > div > div.MuiContainer-root.MuiContainer-maxWidthExpanded.mui-1oaggd7 > div > div.MuiStack-root.mui-1il9m9e > div:nth-child(1) > div > label:nth-child(1) > span.MuiButtonBase-root.MuiRadio-root.MuiRadio-colorPrimary.PrivateSwitchBase-root.MuiRadio-root.MuiRadio-colorPrimary.MuiRadio-root.MuiRadio-colorPrimary.mui-jy7gkk > input",
    "checkbox": "body > div.MuiDialog-root.MuiModal-root.mui-ttaiqw > div.MuiDialog-container.MuiDialog-scrollPaper.mui-1dujj47 > div > div > div.MuiContainer-root.MuiContainer-maxWidthExpanded.mui-1oaggd7 > div > div.MuiStack-root.mui-1il9m9e > div:nth-child(2) > div > label:nth-child(1) > span.MuiButtonBase-root.MuiCheckbox-root.MuiCheckbox-colorPrimary.MuiCheckbox-sizeMedium.PrivateSwitchBase-root.MuiCheckbox-root.MuiCheckbox-colorPrimary.MuiCheckbox-sizeMedium.MuiCheckbox-root.MuiCheckbox-colorPrimary.MuiCheckbox-sizeMedium.mui-19w30dm > input",
    "continue_button_1": "body > div.MuiDialog-root.MuiModal-root.mui-ttaiqw > div.MuiDialog-container.MuiDialog-scrollPaper.mui-1dujj47 > div > div > div.MuiContainer-root.MuiContainer-maxWidthExpanded.mui-1oaggd7 > div > button",
    "continue_button_2": "body > div.MuiDialog-root.MuiModal-root.mui-ttaiqw > div.MuiDialog-container.MuiDialog-scrollPaper.mui-1dujj47 > div > div > div.MuiContainer-root.MuiContainer-maxWidthExpanded.mui-1i9y3xm > div.MuiStack-root.mui-12rj22n > button",
}


# ==================== RANDOM GENERATION SETTINGS ====================

# Email username length range
EMAIL_USERNAME_MIN_LENGTH = 8
EMAIL_USERNAME_MAX_LENGTH = 12

# Password length range
PASSWORD_MIN_LENGTH = 12
PASSWORD_MAX_LENGTH = 16

# Password character set
PASSWORD_CHARACTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"


# ==================== BROWSER CONFIGURATION ====================

# Browser type to use: 'chromium', 'firefox', or 'webkit'
# Note: Some websites may work better with specific browsers
BROWSER_TYPE = 'chromium'

# Custom browser executable path (optional)
# If specified, Playwright will use this browser executable instead of the default
# Examples:
#   - Brave: r'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
#   - Chrome: r'C:\Program Files\Google\Chrome\Application\chrome.exe'
#   - Edge: r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
# Set to None to use Playwright's default browser
BROWSER_EXECUTABLE_PATH = None

# Arguments for browser launch to avoid detection and crashes
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--disable-gpu',
]

# User agent to mimic a real browser
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
