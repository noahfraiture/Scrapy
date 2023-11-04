import time
import numpy as np
import undetected_chromedriver as uc


def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    ]
    return np.random.choice(user_agents)


def create_request_headers(main_url):
    rng_user = str(random_user_agent())
    headers = {
        "user-agent": rng_user,
        'User-Agent': rng_user,  # This is required for compatibility with some websites
        "referer": main_url,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'Content-Type': 'image/jpeg, image/png, image/jpg, image/gif, image/webp',
    }
    return headers


def connect_to_url(driver, url, main_url, timer, first_connection_timer, scroll, urls_done):
    print(f"Connection to: {url}...")
    try:
        driver.get(url)
        time.sleep(timer)
        if first_connection_timer > 0 and main_url not in urls_done:
            print(f"First connection to: {main_url}... Wait {first_connection_timer} seconds")
            time.sleep(first_connection_timer)
            urls_done.append(main_url)
        for _ in range(scroll):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # TODO : detected by some websites
            time.sleep(timer)
    except Exception as e:
        print(f"Connection timeout. Error: {e}")

    print("Connection finished !")


def get_driver(timeout=0, verbose=False):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent=[{random_user_agent()}]")
    if verbose:
        driver = uc.Chrome(options=options, service_args=["--verbose", "--log-path=D:\\qc1.log"])
    else:
        driver = uc.Chrome(options=options)
    if timeout:
        driver.set_page_load_timeout(timeout)
    return driver
