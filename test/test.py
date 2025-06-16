import undetected_chromedriver as uc
import os
import sys

def main():
    try:
        print("Configuring browser options ================...")
        options = uc.ChromeOptions()
        options.binary_location = '/usr/bin/chromium'
        
        # Required for Docker/ARM64
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        print("Initializing browser...==============")
        driver = uc.Chrome(
            options=options,
            driver_executable_path='/usr/bin/chromedriver',  # Using system chromedriver
            headless=True,
            use_subprocess=False  # Critical for ARM64
        )

        print("Navigating to google.com...")
        driver.get("https://www.google.com/")
        print(f"Page title: {driver.title}")
        
        return 0
        
    except Exception as e:
        print(f"Error occurred: {str(e)}", file=sys.stderr)
        return 1
        
    finally:
        if 'driver' in locals():
            print("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    sys.exit(main())
