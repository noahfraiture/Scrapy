from selenium.webdriver.common.by import By
from urllib.parse import urlparse, urlunparse
import numpy as np

EXTENSIONS = ("jpg", "jpeg", "png", "gif", "webp")

def find_image_urls(driver):
    img_image = [url.get_attribute("src") for url in driver.find_elements(By.TAG_NAME, "img")]
    img_image = [url for url in img_image if url is not None and any(ext in url for ext in EXTENSIONS) and "http" in url]
    link_image = [url.get_attribute("href") for url in driver.find_elements(By.TAG_NAME, "link")]
    link_image = [url for url in link_image if url is not None and any(ext in url for ext in EXTENSIONS) and "http" in url]

    return img_image + link_image


def find_links_by_driver(driver, verbose):
    a_links = [url.get_attribute('href') for url in driver.find_elements(By.TAG_NAME, "a")]
    a_links = [url for url in a_links if url is not None and "http" in url]
    if verbose: print(f"Links found: {len(a_links)}")
    return a_links


def extract_clean_url_and_extension(url, allowed_extension, verbose):
    parsed_url = urlparse(url)
    clean_url = parsed_url._replace(query='')._replace(params='')._replace(fragment='')
    clean_url = urlunparse(clean_url)

    extension = clean_url.split(".")[-1]
    if extension not in allowed_extension:
        if verbose:
            print(f"Extension not allowed {extension}, allowed {allowed_extension}\nUrl : {url}")
        return clean_url, None
    return clean_url, extension


def create_filename(clean_url, extension, names):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
    name = clean_url.split("/")[-1]
    if name != "":
        filename = name
    else:
        filename = f"{''.join(np.random.choice(list(characters), size=8))}.{extension}"
    if filename in names:
        filename = f"{names[filename]}-{filename}"
    if "." not in filename:
        filename = f"{filename}.{extension}"
    names[filename] = names.get(filename, 0) + 1
    return filename
