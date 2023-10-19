import os
import re
from io import BytesIO
from PIL import Image, ImageSequence
import requests
from parser import extract_clean_url_and_extension, create_filename
from driver import create_request_headers


def download_image(url, main_url, overwrite, verbose, limit, allowed_extension, names, urls_done, count):
    if url in urls_done:
        if verbose: print(f"Url already done: {url}")
        return
    urls_done.append(url)

    clean_url, extension = extract_clean_url_and_extension(url, allowed_extension, verbose)

    if extension not in allowed_extension: return
    if extension is None or '':
        extension = "jpg"
        if verbose:
            print(f"Extension not found {extension}, defaulting to jpg")

    filename = create_filename(clean_url, extension, names)
    if not overwrite and os.path.exists(filename):
        if verbose:
            print(f"File '{filename}' already exists in the folder")
        return

    if limit != -1 and count[0] >= limit:
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
        count[0] += 1
        return

    img.save(filename)
    count[0] += 1
    print(f"Image saved as {filename}")


def download_images(image_urls, main_url, overwrite, verbose, limit, extension, names, urls_done, count):
    for image_url in image_urls:
        download_image(image_url, main_url, overwrite, verbose, limit, extension, names, urls_done, count)


def handle_animated_image(img, filename, verbose):
    skip_frames = 5  # TODO : add option to resize or set limit of size

    frames = list(ImageSequence.Iterator(img))
    selected_frames = frames[::skip_frames]

    if verbose:
        print(f"Number of pixels: {img.size[0] * img.size[1]}")
        print(f"Number of frames: {img.n_frames}")
        print(f"Number of frames selected: {len(selected_frames)}")

    selected_frames[0].save(
        filename,
        format="GIF",
        save_all=True,
        append_images=selected_frames[1:],
        loop=0
    )

    file_size = os.path.getsize(filename)
    if verbose:
        print(f"Animated image saved as {filename}")
        print(f"Size of the image: {file_size}")


def open_image(response, url):
    try:
        img = Image.open(BytesIO(response.content))
    except:
        print(f"Error with {url}, image cannot be opened")
        return None
    return img


def create_directory(url, name):
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
