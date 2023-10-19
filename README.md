# Scrapy
Scrapy is a Python script that allows you to scrape every image of a website. The script automatically finds other links and follows them following some rules.
![Scrapy the mascot (Thx dall-e)](assets/mascot.jpeg)

## Installation
To install Scrapy, run the following command in a terminal:

```
git clone https://github.com/NoahFraiture/scrapy.git
chmod +x spider.py
```
## Usage
To use Scrapy, simply run the following command:

```./spider.py <url>```
Where <url> is the URL of the website you want to scrape.

### Options
Scrapy has a number of options that you can use to control its behavior. These options are listed below:

- --**upper**: Upper bound for the URLs to crawl (default: None)
- --**overwrite**: Whether to overwrite existing files (default: False)
- --**depth**: Depth of the crawl. Stop at 0. Use -1 to crawl all the website until the upper bound (default: 1)
- --**domain**: Depth to include links from other domains (default: 0)
- --**hierarchy**: Create sub directories (default: False)
- --**verbose**: Create log file on the driver (default: False)
- --**ignored**: List of ignored urls separated by a comma. You can add * at the end of the url to ignore all the sub urls (default: "")
- --**timer**: Timer in seconds to wait at every page (default: 2)
- --**name**: Name of the folder to save the images (default: None)
- --**limit**: Limit of images to download (default: 1)
- --**extension**: List of extension as string of the images to download. Ignore others (default: "jpg gif")
- --**scroll**: Scroll down the page to load more images (default: 0)
- --**timeout**: Timeout in seconds for the connection (default: 0)
- --**connection**: Timer in seconds to wait at the first connection (default: 0)
- --**pound**: Pound says if pound (#) are important. (default: False)

### Example
To scrape all images of a specific page, you would run the following command:

```./spider.py https://example.com/page```

To scrape 20 gifs from the website https://example.com, you would run the following command:

```./spider.py https://example.com --limit 20 --depth -1 --name example --connection 10 --extension gif```

## Conclusion
Scrapy is cool, you should use it. I hesitated to name it spider, so the main file is spider but it could change in the future.