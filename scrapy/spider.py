#!/usr/bin/env python3
import argparse
from urllib.parse import urlparse, urlunparse
import os
from file import create_directory, create_subdirectories, exit_subdirectories, enter_subdirectories, download_images
from driver import connect_to_url, get_driver
from parser import find_links_by_driver, find_image_urls, EXTENSIONS



def save_images(driver, url, upper_bound, overwrite, depth, other_domain, hierarchy, verbose, ignored, timer, name,
                limit, extension, scroll, first_connection_timer, urls_done, count, names, pound):

    if depth == 0:
        return
    if not url.startswith(upper_bound):
        if other_domain == 0:
            return
        other_domain -= 1

    if not pound:
        url = urlunparse(urlparse(url)._replace(fragment=''))

    if url in urls_done: return
    urls_done.append(url)

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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", metavar='\b', type=str, help="URL to crawl")
    parser.add_argument("--upper", metavar='\b', type=str, default=None, help="Upper bound for the number of URLs to crawl (default: None)")
    parser.add_argument("--overwrite", metavar='\b', type=bool, default=False, help="Whether to overwrite existing files (default: False)")
    parser.add_argument("--depth", metavar='\b', type=int, default=1, help="Depth of the crawl. Stop at 0. Use -1 to crawl all the website until the upper bound (default: 1)")
    parser.add_argument("--domain", metavar='\b', type=int, default=0, help="Depth to include links from other domains (default: 0)")
    parser.add_argument("--hierarchy", metavar='\b', type=bool, default=False, help="Create sub directories (default: False)")
    parser.add_argument("--verbose", metavar='\b', type=bool, default=False, help="Create log file on the driver (default: False)")
    parser.add_argument("--ignored", metavar='\b', type=str, default="", help="List of ignored urls separated by a comma. You can add * at the end of the url to ignore all the sub urls (default: \"\")")
    parser.add_argument("--timer", metavar='\b', type=int, default=2, help="Timer in seconds to wait at every page (default: 2)")
    parser.add_argument("--name", metavar='\b', type=str, default=None, help="Name of the folder to save the images (default: None)")
    parser.add_argument("--limit", metavar='\b', type=int, default=-1, help="Limit of images to download (default: 1)")
    parser.add_argument("--extension", metavar='\b', type=str, default="jpg gif", help="List of extension as string of the images to download. Ignore others (default: \"jpg gif\")")
    parser.add_argument("--scroll", metavar='\b', type=int, default=0, help="Scroll down the page to load more images (default: 0)")
    parser.add_argument("--timeout", metavar='\b', type=int, default=0, help="Timeout in seconds for the connection (default: 0)")
    parser.add_argument("--connection", metavar='\b', type=int, default=0, help="Timer in seconds to wait at the first connection (default: 0)")
    parser.add_argument("--pound", metavar='\b', type=bool, default=False, help="Pound says if pound (#) are important. (default: False)")
    return parser.parse_args()


def main():
    args = get_args()
    driver = get_driver(timeout=args.timeout)
    save_images(
        driver=driver,
        url=args.url,
        upper_bound=args.upper if args.upper is not None else args.url,
        overwrite=args.overwrite,
        depth=args.depth,
        other_domain=args.domain,
        hierarchy=args.hierarchy,
        verbose=args.verbose,
        ignored=args.ignored.split(","),
        timer=args.timer,
        name=args.name,
        limit=args.limit,
        extension=args.extension,
        scroll=args.scroll,
        names={},
        first_connection_timer=args.connection,
        urls_done=[],
        count=0,
        pound=args.pound
    )


def start(url, upper_bound, overwrite, depth, other_domain, hierarchy, verbose, ignored,
          timer, name, limit, extension, scroll, timeout, first_connection_timer, pound):
    driver = get_driver(timeout=timeout)
    names = {}
    urls_done = []
    count = 0
    save_images(
        driver=driver,
        url=url,
        upper_bound=upper_bound if upper_bound is not None else url,
        overwrite=overwrite,
        depth=depth,
        other_domain=other_domain,
        hierarchy=hierarchy,
        verbose=verbose,
        ignored=ignored.split(","),
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
