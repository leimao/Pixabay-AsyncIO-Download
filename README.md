# Pixabay AsyncIO Download

## Introduction

[Pixabay](https://pixabay.com/) is a vibrant community of creatives, sharing copyright free images, videos and music. All contents are released under the Pixabay License, which makes them safe to use without asking for permission or giving credit to the artist - even for commercial purposes.

This application allows the user to download images in large scale from [Pixabay](https://pixabay.com/) asynchronously using Python `asyncio`.

## Dependencies

* [`aiohttp`](https://docs.aiohttp.org/en/stable/)
* [`aiofiles`](https://github.com/Tinche/aiofiles)

## Usages

### Install Dependencies

To install the dependencies, please run the following command in the terminal.

```bash
$ pip install -r requirements.txt
```

### Download Images

Please register a [Pixabay](https://pixabay.com/) account and obtain the [Pixabay API key](https://pixabay.com/api/docs/).

To download the images, please prepare the Pixabay image ids in a file, such as `pixabay_ids.txt`, and run the following command in the terminal.

```bash
$ python download_async.py \
    --image-ids-filepath pixabay_ids.txt \
    --image-urls-filepath pixabay_urls.txt \
    --download-dir pixabay \
    --pixabay-api-key xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxx \
    --update-image-urls
```

This will consume the Pixabay API key `xxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxx`, read the images ids from `pixabay_ids.txt`, save the images urls to `pixabay_urls.txt`, and download all the images to the directory `pixabay`.

Alternatively, if the images urls file, such as, `pixabay_urls.txt` is already available, please run the following command in the terminal.

```bash
$ python download_async.py \
    --image-urls-filepath pixabay_urls.txt \
    --download-dir pixabay
```

This will read the images urls from `pixabay_urls.txt` and download all the images to the directory `pixabay`. No Pixabay API key is required to download the images from the urls.

