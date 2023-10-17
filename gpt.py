import os
import re
import time
from io import BytesIO
from PIL import Image, ImageSequence
from selenium.webdriver.common.by import By
import requests
import numpy as np
import argparse
import undetected_chromedriver as uc
from urllib.parse import urlparse, urlunparse

EXTENSIONS = ("jpg", "jpeg", "png", "gif", "webp")


def find_image_urls(driver):
    img_image = [url.get_attribute("src") for url in driver.find_elements(By.TAG_NAME, "img")]
    img_image = [url for url in img_image if any(ext in url for ext in EXTENSIONS) and "http" in url]
    link_image = [url.get_attribute("href") for url in driver.find_elements(By.TAG_NAME, "link")]
    link_image = [url for url in link_image if any(ext in url for ext in EXTENSIONS) and "http" in url]

    return img_image + link_image


def download_image(url, main_url, overwrite, verbose, limit, allowed_extension, names, urls_done, count):
    if url in urls_done:
        if verbose: print(f"Url already done: {url}")
        return
    urls_done.append(url)

    clean_url, extension = extract_clean_url_and_extension(url, allowed_extension, verbose)

    if extension is None or '':
        extension = "jpg"
        if verbose:
            print(f"Extension not found {extension}, defaulting to jpg")

    filename = create_filename(clean_url, extension, names)
    if not overwrite and os.path.exists(filename):
        if verbose:
            print(f"File '{filename}' already exists in the folder")
        return

    if limit != -1 and count >= limit:
        print(f"Limit reached: {limit}")
        exit()

    headers = create_request_headers(main_url)
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Error: {response.status_code} with {url}")
        return

    img = open_image(response, url)
    if img is None:
        return

    if extension == "gif" and img.is_animated:
        handle_animated_image(img, filename, verbose)
        return

    img.save(filename)
    count += 1
    print(f"Image saved as {filename}")


def extract_clean_url_and_extension(url, allowed_extension, verbose):
    parsed_url = urlparse(url)
    clean_url = parsed_url._replace(query='')._replace(params='')._replace(fragment='')
    clean_url = urlunparse(clean_url)

    extension = clean_url.split(".")[-1]
    if extension != allowed_extension:
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


def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    ]
    return np.random.choice(user_agents)


def create_request_headers(main_url):
    headers = {
        "user-agent": str(random_user_agent()),
        "referer": main_url,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'Content-Type': 'image/jpeg, image/png, image/jpg, image/gif, image/webp',
    }
    return headers


def open_image(response, url):
    try:
        img = Image.open(BytesIO(response.content))
    except:
        print(f"Error with {url}, image cannot be opened")
        return None
    return img


def handle_animated_image(img, filename, verbose):
    skip_frames = 5
    print(f"Number of pixels: {img.size[0] * img.size[1]}")
    print(f"Number of frames: {img.n_frames}")

    frames = list(ImageSequence.Iterator(img))
    selected_frames = frames[::skip_frames]

    selected_frames[0].save(
        filename,
        format="GIF",
        save_all=True,
        append_images=selected_frames[1:],
        loop=0
    )

    print(f"Size of the image: {os.path.getsize(filename)}")
    print(f"Animated image saved as {filename}")
    count += 1


def save_images(driver, url, upper_bound, overwrite, depth, other_domain, hierarchy, verbose, ignored, timer, name,
                limit, extension, scroll, first_connection_timer, urls_done, count, names, pound):
    if depth == 0:
        return
    if not url.startswith(upper_bound):
        if other_domain == 0:
            return
        other_domain -= 1

    if pound:
        if url in urls_done: return
    else:
        urls_done.append(urlunparse(urlparse(url)._replace(fragment='')))

    directory = create_directory(url, name)
    os.chdir(directory)

    subdirectories = []
    if hierarchy:
        subdirectories = create_subdirectories(url)
        enter_subdirectories(subdirectories)

    main_url = "/".join(url.split('/')[:3])
    connect_to_url(driver, url, main_url, timer, first_connection_timer, scroll, urls_done)

    is_ignore = check_if_ignored(url, ignored, verbose)
    if is_ignore and verbose:
        print("Ignored URL detected")
    else:
        image_urls = find_image_urls(driver)
        if verbose: print(f"Image found: {len(image_urls)}")
        download_images(image_urls, main_url, overwrite, verbose, limit, extension, names, urls_done, count)

    exit_subdirectories(hierarchy, subdirectories)
    os.chdir("..")

    for link_url in find_links_by_driver(driver, verbose):
        save_images(driver=driver, url=link_url, upper_bound=upper_bound, overwrite=overwrite, depth=depth,
                    other_domain=other_domain, hierarchy=hierarchy, verbose=verbose, ignored=ignored, timer=timer,
                    name=name, limit=limit, extension=extension, scroll=scroll,
                    first_connection_timer=first_connection_timer, urls_done=urls_done, count=count, names=names,
                    pound=pound)


def create_directory(url, name):  #
    if name is None:
        directory = re.search(r"(?<=://)[^/]+", url).group(0)
    else:
        directory = name
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Directory created: '{directory}'")
    return directory


def create_subdirectories(url):
    subdirectories = url.split('/')[3:]
    if subdirectories[-1] == "":
        subdirectories = subdirectories[:-1]
    for sub in subdirectories:
        os.makedirs(sub, exist_ok=True)
        os.chdir(sub)
    for _ in range(len(subdirectories)):
        os.chdir("..")
    print(f"Sub directories created: {subdirectories}")
    return subdirectories


def enter_subdirectories(subdirectories):
    for sub in subdirectories:
        os.chdir(sub)


def exit_subdirectories(hierarchy, subdirectories):
    if hierarchy:
        for _ in range(len(subdirectories)):
            os.chdir("..")


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
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(timer)
    except Exception as e:
        print(f"Connection timeout. Error: {e}")

    print("Connection finished !")


def check_if_ignored(url, ignored, verbose):
    is_ignore = False
    if verbose:
        print(f"Detecting if url is ignored...")
        print(f"URL: {url}")
        print(f"Ignored: {ignored}")
    for ignored_url in ignored:
        if ignored_url == "":
            continue
        if (ignored_url[-1] == "*" and url.startswith(ignored_url[:-1])) or url == ignored_url:
            is_ignore = True
            break
    return is_ignore


def download_images(image_urls, main_url, overwrite, verbose, limit, extension, names, urls_done, count):
    for image_url in image_urls:
        download_image(image_url, main_url, overwrite, verbose, limit, extension, names, urls_done, count)


def find_links_by_driver(driver, verbose):
    a_links = [url.get_attribute('href') for url in driver.find_elements(By.TAG_NAME, "a")]
    a_links = [url for url in a_links if url is not None and "http" in url]
    if verbose: print(f"Links found: {len(a_links)}")
    return a_links


def get_driver(timeout=0, verbose=False):
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument(f"user-agent=[{random_user_agent()}]")
    if verbose:
        driver = uc.Chrome(options=options, service_args=["--verbose", "--log-path=D:\\qc1.log"])
    else:
        driver = uc.Chrome(options=options)
    if timeout:
        driver.set_page_load_timeout(timeout)
    return driver


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str, help="URL to crawl")
    parser.add_argument("--upper_bound", type=str, default=None, help="Upper bound for the number of URLs to crawl")
    parser.add_argument("--overwrite", type=bool, default=False, help="Whether to overwrite existing files")
    parser.add_argument("--depth", type=int, default=1,
                        help="Depth of the crawl. When equals 0, stop the scraping. Use -1 to crawl all the website until the upper bound")
    parser.add_argument("--other_domain", type=int, default=0, help="Whether to include links from other domains")
    parser.add_argument("--hierarchy", type=bool, default=False, help="Create sub directories")
    parser.add_argument("--verbose", type=bool, default=False, help="Create log file on the driver")
    parser.add_argument("--ignored", type=str, default="",
                        help="List of ignored urls separated by a comma. The image from this specific url will not be downloaded. You can add * at the end of the url to ignore all the sub urls.")
    parser.add_argument("--timer", type=int, default=2, help="Timer in seconds to wait at every page (default: 2)")
    parser.add_argument("--name", type=str, default=None, help="Name of the folder to save the images")
    parser.add_argument("--limit", type=int, default=-1, help="Limit of images to download")
    parser.add_argument("-e", "--example", action="store_true", help="show an example of usage")
    parser.add_argument("--extension", type=str, default="jpg",
                        help="Extension of the images to download (default: jpg). Ignore others")
    parser.add_argument("--scroll", type=int, default=0, help="Scroll down the page to load more images (default: 0)")
    parser.add_argument("--timeout", type=int, default=0, help="Timeout in seconds for the connection (default: 0)")
    parser.add_argument("--first_connection_timer", type=int, default=0,
                        help="Timer in seconds to wait at the first connection (default: 0)")
    parser.add_argument("--pound", type=bool, default=False,
                        help="Pound says if pound (#) are important. (default : False)")
    return parser.parse_args()


def main():
    args = get_args()
    url = args.url
    upper_bound = args.upper_bound if args.upper_bound is not None else url
    overwrite = args.overwrite
    depth = args.depth
    other_domain = args.other_domain
    hierarchy = args.hierarchy
    verbose = args.verbose
    ignored = args.ignored.split(",")
    timer = args.timer
    name = args.name
    limit = args.limit
    extension = args.extension
    scroll = args.scroll
    first_connection_timer = args.first_connection_timer
    pound = args.pound

    driver = get_driver(timeout=args.timeout)
    names = {}
    urls_done = []
    count = 0
    save_images(
        driver=driver,
        url=url,
        upper_bound=upper_bound,
        overwrite=overwrite,
        depth=depth,
        other_domain=other_domain,
        hierarchy=hierarchy,
        verbose=verbose,
        ignored=ignored,
        timer=timer,
        name=name,
        limit=limit,
        extension=extension,
        scroll=scroll,
        names=names,
        first_connection_timer=first_connection_timer,
        urls_done=urls_done,
        count=count,
        pound=pound
    )


if __name__ == "__main__":
    main()

# after some try, it seems that i'm kick or something like that. I could see if can change the header to avoid that
# to do, encoder #
