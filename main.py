import json
import os
import random
import shutil
import time
import traceback
from typing import Dict, Any, Optional

import requests
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
from fastapi import FastAPI, Body
from pydantic import BaseModel

from proxy_ext import ProxyParams, create_proxy_extension
from utils import get_item_id_from_item_url

load_dotenv()


if 'USE_PYVIRTUALDISPLAY' in os.environ:
    from pyvirtualdisplay import Display

    display = Display(visible=False, size=(1920, 1080))
    display.start()

if 'ACCESS_KEY' not in os.environ:
    print('no access key found')
    exit(1)

with open("base_headers.json") as f:
    base_headers = json.load(f)

app = FastAPI()


def get_walmart_seller_offers(
        item_url: str,
        hc_id: int,
        output_path: str = "results.json",
        profile_path: Optional[str] = None,
        proxy_extension: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get all seller offers from Walmart with fast direct fetch.

    Args:
        item_url: The complete Walmart item URL
        output_path: Path to write results to
        profile_path: Path to Chrome user profile directory (to reuse sessions)
        proxy_extension: Optional proxy extension dir to load

    Returns:
        The API response as a dictionary
    """

    item_code = get_item_id_from_item_url(item_url)
    print("\n item_code = ", item_code)
    # Initialize variables
    driver = None
    result = None

    try:
        print("Starting browser session...")

        driver = start_chrome(profile_path, proxy_extension)

        driver.set_window_size(1920, 1080)
        driver.set_page_load_timeout(30)

        # Load the product page to establish cookies
        print(f"Loading page: {item_url}")
        driver.get(item_url)

        # Wait very briefly for essential cookies to be set
        print("Waiting for page to initialize 2...")
        time.sleep(2)

        # Generate random correlation ID and traceparent (like in nenad.js)
        correlation_id = ''.join(
            random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-', k=30))
        trace_id = ''.join(random.choices('0123456789abcdef', k=32))
        span_id = ''.join(random.choices('0123456789abcdef', k=16))
        traceparent = f"00-{trace_id}-{span_id}-00"

        # Create direct fetch request mirroring nenad.js
        print("Executing direct API request...")
        api_url = f"https://www.walmart.com/orchestra/home/graphql/GetAllSellerOffers/84178429fb8e20469ffd1b5bf3a6f8cf7aeeb1d0e6dfe36081fc58b1e4ff3053?variables=%7B%22itemId%22%3A%22{item_code}%22%2C%22isSubscriptionEligible%22%3Atrue%7D"
        print("\n api_url = ", api_url)

        headers = base_headers.copy()
        headers["traceparent"] = traceparent
        headers["wm_page_url"] = item_url
        headers["wm_qos.correlation_id"] = correlation_id
        headers["x-o-correlation-id"] = correlation_id
        fetch_script = f"""
            return new Promise((resolve, reject) => {{
                fetch("{api_url}", {{
                    "headers": {json.dumps(headers)},
                    "referrer": "{item_url}",
                    "referrerPolicy": "strict-origin-when-cross-origin",
                    "body": null,
                    "method": "GET",
                    "mode": "cors",
                    "credentials": "include"
                }})
                .then(response => {{
                    if (response.status === 412) {{
                        return resolve({{ success: false, status: 412, error: 'Bot detection triggered' }});
                    }}
                    if (!response.ok) {{
                        return resolve({{ success: false, status: response.status, error: 'Network response was not ok' }});
                    }}
                    return response.json().then(data => resolve({{ success: true, data }}));
                }})
                .catch(error => {{
                    resolve({{ success: false, error: error.toString() }});
                }});
            }});
        """

        fetch_result = driver.execute_script(fetch_script)

        if fetch_result and fetch_result.get('success'):
            print("Successfully retrieved data via direct fetch")
            result = fetch_result.get('data')
        else:
            status = fetch_result.get('status') if fetch_result else 'unknown'
            error = fetch_result.get('error') if fetch_result else 'unknown'
            print(f"Fetch failed with status {status}, error: {error}")
            raise Exception(f"API request failed: Status {status}, Error: {error}")

        # Save the result to file
        if result:

            selenium_cookies = driver.get_cookies()
            requests_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}

            # Save to file
            with open(f"/data/hc-{hc_id}.json", 'w') as f:
                json.dump({'cookies': requests_cookies, 'headers': headers, 'timestamp': time.time()}, f)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {output_path}")
        else:
            raise Exception("No data retrieved from API")

        return result

    except Exception as error:
        print(f"Error: {error}")

        # Create error file with details
        error_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "itemCode": item_code,
            "itemUrl": item_url,
            "error": str(error),
            "traceback": traceback.format_exc()
        }

        try:
            with open("error_log.json", 'w', encoding='utf-8') as f:
                json.dump(error_data, f, indent=2)
            print(f"Error details saved to error_log.json")
        except Exception as e:
            print(f"Failed to write error log: {e}")

        raise

    finally:
        # Close the browser
        if driver:
            print("Closing browser 2...")
            try:
                driver.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")


def get_walmart_page_and_store_hc(
        item_url: str,
        hc_id: int,
        proxy_extension: Optional[str] = None,
        profile_path: Optional[str] = None,
):
    driver = None
    #try:
    if 1==1:
        driver = start_chrome(profile_path, proxy_extension)
        print('\n driver = ', driver)
        #driver.set_window_size(1920, 1080)
        print('\n wait for 30 seconds')
        driver.set_page_load_timeout(30)

        # Load the product page to establish cookies
        print(f"Loading page 1: {item_url}")
        driver.get(item_url)

        # Wait very briefly for essential cookies to be set
        print("Waiting for page to initialize 1...")
        time.sleep(5)

        selenium_cookies = driver.get_cookies()
        requests_cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}

        ## making up some headers here
        correlation_id = ''.join(
            random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-', k=30))
        trace_id = ''.join(random.choices('0123456789abcdef', k=32))
        span_id = ''.join(random.choices('0123456789abcdef', k=16))
        traceparent = f"00-{trace_id}-{span_id}-00"
        headers = base_headers.copy()
        headers["traceparent"] = traceparent
        headers["wm_page_url"] = item_url
        headers["wm_qos.correlation_id"] = correlation_id
        headers["x-o-correlation-id"] = correlation_id

        with open(f"/data/hc-{hc_id}.json", 'w') as f:
            json.dump({'cookies': requests_cookies, 'headers': headers, 'timestamp': time.time()}, f)

        print("file saved successfully")
        print("file = ", hc_id)
    #except Exception as e:
    #    print(e)
    #    raise
    #finally:
        # Close the browser
    #    if driver:
    #        print("Closing browser...")
    #        try:
    #            driver.quit()
    #        except Exception as e:
    #            print(f"Error closing driver: {e}")


def start_chrome(profile_path: str, proxy_extension: str):
    # Create user profile directory if needed
    if profile_path is None:
        profile_path = "/tmp/chrome_profile"
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
        print(f"Created Chrome profile directory: {profile_path}")
    else:
        print(f"Using existing Chrome profile: {profile_path}")
    # Find path to Chrome (if using local Chrome)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #chrome_path = os.path.join(script_dir, "chrome-testing", "chrome-win64", "chrome.exe")
    chrome_path = "/usr/bin/chromedriver"
    # Verify Chrome exists
    if os.path.exists(chrome_path):
        print(f"Using Chrome binary at: {chrome_path}")
    else:
        print("Using system Chrome 1")
        chrome_path = None

    # Configure Chrome options
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={profile_path}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")  # Optional
    options.add_argument('--window-size=1920,1080')
    options.binary_location = '/usr/bin/chromium'

    # DO NOT use version_main or use_subprocess
    # Add these arguments to reduce detection
    options.add_argument("--disable-blink-features=AutomationControlled")

    if proxy_extension:
        options.add_argument(f"--load-extension={proxy_extension}")

    # Create webdriver instance with user profile
    if chrome_path:
        print("\n chrome_path = ", chrome_path)
        #driver = uc.Chrome(options=options, browser_executable_path=chrome_path, version_main=133)
        driver = uc.Chrome(
            options=options,
            driver_executable_path=chrome_path,  # Using system chromedriver
            headless=True,
            use_subprocess=False,  # Critical for ARM64
            version_main=133
        )
    else:
        print("\n I am in else")
        driver = uc.Chrome(options=options, version_main=133)
    print("driver returned")
    return driver


def get_walmart_seller_offer_fast(item_url: str, proxy_url: Optional[str]):
    with open("/data/hc.json", 'r') as f:
        hc = json.load(f)

        response = requests.post('http://node-fast-scraper:3000/scrape-fast',
                                 json={
                                     "url": item_url,
                                     "hc": hc,
                                     "proxy_url": proxy_url,
                                 },
                                 headers={
                                     "Content-Type": "application/json"
                                 })

        return response.json()


class GetSellersDto(BaseModel):
    url: str
    proxy_url: Optional[str] = None
    hc_id: int


@app.post("/store-hc-from-product-page")
def store_product_page(body: GetSellersDto = Body()):
    print("\n I am store_product_page called")
    proxy_extension = None
    if body.proxy_url:
        proxy_params = ProxyParams.from_url(body.proxy_url)
        create_proxy_extension(proxy_params, "/tmp/ext")
        proxy_extension = "/tmp/ext"
    get_walmart_page_and_store_hc(
        item_url=body.url,
        hc_id=body.hc_id,
        proxy_extension=proxy_extension,
    )

    return {"msg": "OK"}


@app.post("/sellers")
async def get_sellers(
        body: GetSellersDto = Body(description="key and url")
):
    url = body.url
    print('\n I am sellers = ', url)
    start_time = time.time()  # Record the start time

    proxy_extension = None
    if body.proxy_url:
        proxy_params = ProxyParams.from_url(body.proxy_url)
        create_proxy_extension(proxy_params, "/tmp/ext")
        proxy_extension = "/tmp/ext"
    result = get_walmart_seller_offers(url, hc_id=body.hc_id, proxy_extension=proxy_extension)

    end_time = time.time()  # Record the end time

    # Calculate the time taken in milliseconds
    time_taken_ms = (end_time - start_time) * 1000

    return {
        "stats": {"time_taken": time_taken_ms},
        "result": result,
    }


@app.delete("/chrome_profile")
def delete_chrome_profile():
    shutil.rmtree("/data/chrome_profile", ignore_errors=True)


@app.delete("/hc")
def delete_hc():
    shutil.rmtree("/data/hc.json", ignore_errors=True)


@app.get("/hc")
def get_hc():
    with open("/data/hc.json", 'r') as f:
        json_data = json.load(f)
        return json_data

@app.post("/test_request")
def test_request(body: GetSellersDto = Body()):
    proxy_url = body.proxy_url
    header_id = body.hc_id
    url = body.url

    return {
        "proxy_url": proxy_url,
        "header_id": header_id,
        "url": url,
    }

@app.get("/ping")
def ping():
    return {"msg": "OK"}


if __name__ == "__main__":
    print('use uvicorn')
    exit(1)
