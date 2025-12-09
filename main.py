"""
Bytez API Key Scraper
A tool to automate the generation of API keys from bytez.com

Usage:
    python main.py [NUM_KEYS_TO_SCRAPE]
"""

import asyncio
import sys
from core import BytezAPIKeyScraper
from config import settings


async def main():
    """Main entry point for the scraper."""
    
    print("=" * 60)
    print("Bytez API Key Scraper")
    print("=" * 60)
    print(f"Configuration:")
    print(f"  - Mode: Infinite Loop (Press Ctrl+C to stop)")
    print(f"  - Browser type: {settings.BROWSER_TYPE}")
    if settings.BROWSER_EXECUTABLE_PATH:
        print(f"  - Browser path: {settings.BROWSER_EXECUTABLE_PATH}")
    print(f"  - Headless mode: {settings.HEADLESS_MODE}")
    print(f"  - Accounts file: {settings.ACCOUNTS_FILE}")
    print(f"  - Error images directory: {settings.ERROR_IMAGES_DIR}")
    print("=" * 60)
    print()

    scraper = BytezAPIKeyScraper()
    try:
        await scraper.scrape_keys()
    except KeyboardInterrupt:
        # This catches the interrupt if it bubbles up from scraper
        print("\nOperation cancelled by user.")
    
    print()
    print("=" * 60)
    print("Scraping session completed!")
    print(f"Check {settings.ACCOUNTS_FILE} for generated accounts")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
