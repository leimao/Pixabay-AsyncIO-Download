import os
import sys
import asyncio
import argparse
import aiohttp
import aiofiles
from typing import List, Tuple, Optional
from timeit import default_timer as timer
from datetime import timedelta


def read_image_ids(image_ids_filepath: str) -> List[int]:

    image_ids = []

    with open(image_ids_filepath, "r") as f:
        for line in f:
            image_ids.append(int(line.strip()))

    return image_ids


def save_image_urls(image_url_tuples: Tuple[int, Optional[str]],
                    image_urls_filepath: str,
                    ignore_none: bool = False) -> None:

    with open(image_urls_filepath, "w") as f:
        for image_id, image_url in image_url_tuples:
            if ignore_none is True and image_url is None:
                continue
            else:
                f.write(f"{image_id},{image_url}\n")


def read_image_urls(image_urls_filepath: str) -> List[Tuple[int, str]]:

    image_url_tuples = []

    with open(image_urls_filepath, "r") as f:
        for line in f:
            image_id, image_url = line.split(",")
            image_id = int(image_id.strip())
            image_url = image_url.strip()
            image_url_tuple = (image_id, image_url)
            image_url_tuples.append(image_url_tuple)

    return image_url_tuples


async def async_get_pixabay_image_url(
        api_key: str, image_id: int,
        pixabay_api_url: str) -> Tuple[int, Optional[str]]:

    async with aiohttp.ClientSession() as session:
        async with session.get(pixabay_api_url,
                               params={
                                   "key": api_key,
                                   "id": image_id
                               }) as response:
            if response.status == 200:
                data = await response.json()
                retrieved_id = data["hits"][0]["id"]
                if retrieved_id != image_id:
                    print(f"Query image id is {image_id}, "
                          f"but got image id {retrieved_id}.")
                    image_url = None
                else:
                    image_url = data["hits"][0]["largeImageURL"]
            else:
                print(f"Unable to retrieve the url "
                      f"for image {image_id} from {response.url}")
                image_url = None

    return (image_id, image_url)


async def async_get_pixabay_image_urls(
        api_key: str, image_ids: List[int],
        pixabay_api_url: str) -> Tuple[int, Optional[str]]:

    coroutines = [
        async_get_pixabay_image_url(api_key=api_key,
                                    image_id=image_id,
                                    pixabay_api_url=pixabay_api_url)
        for image_id in image_ids
    ]
    image_url_tuples = await asyncio.gather(*coroutines)

    return image_url_tuples


async def async_download_image(image_url_tuple: Tuple[int, Optional[str]],
                               download_dir: str) -> None:

    image_id, image_url = image_url_tuple
    image_filename = f"{image_id}.jpg"
    image_filepath = os.path.join(download_dir, image_filename)
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                content = await response.read()
                async with aiofiles.open(image_filepath, "wb") as f:
                    await f.write(content)
            else:
                print(f"Unable to download image {image_id} from {image_url}")


async def async_download_images(image_url_tuples: List[Tuple[int, str]],
                                download_dir: str) -> None:

    if not os.path.exists(download_dir):
        os.mkdir(download_dir)

    coroutines = [
        async_download_image(image_url_tuple=image_url_tuple,
                             download_dir=download_dir)
        for image_url_tuple in image_url_tuples if image_url_tuple[1] != "None"
    ]

    await asyncio.gather(*coroutines)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Download Pixabay royalty-free images.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    pixabay_api_url = "https://pixabay.com/api"
    image_ids_filepath_default = "pixabay_ids.txt"
    image_urls_filepath_default = "pixabay_urls.txt"
    download_dir_default = "pixabay"
    update_image_urls = False

    parser.add_argument("--image-ids-filepath",
                        type=str,
                        help="The filepath for Pixabay image ids.",
                        default=image_ids_filepath_default)
    parser.add_argument("--image-urls-filepath",
                        type=str,
                        help="The filepath for Pixabay image ids and urls.",
                        default=image_urls_filepath_default)
    parser.add_argument(
        "--download-dir",
        type=str,
        help="The directory for saving the downloaded Pixabay images.",
        default=download_dir_default)
    parser.add_argument(
        "--update-image-urls",
        help="Force to update the image urls file using the Pixabay API.",
        action="store_true")
    parser.add_argument(
        "--pixabay-api-key",
        type=str,
        help="Pixabay API key for retrieving the Pixabay image urls.")

    argv = parser.parse_args()

    image_ids_filepath = argv.image_ids_filepath
    image_urls_filepath = argv.image_urls_filepath
    download_dir = argv.download_dir
    update_image_urls = argv.update_image_urls
    api_key = argv.pixabay_api_key

    if not os.path.exists(image_urls_filepath) or update_image_urls:

        if api_key is None:
            raise AssertionError(
                "Pixabay API key was not provided. "
                "To get a free API key, "
                "please register an account on https://pixabay.com/")

        print("Reading image ids...")
        image_ids = read_image_ids(image_ids_filepath=image_ids_filepath)

        print("Retrieving image urls...")
        start = timer()
        # Python 3.7+
        if sys.version_info >= (3, 7):
            image_url_tuples = asyncio.run(
                async_get_pixabay_image_urls(api_key=api_key,
                                             image_ids=image_ids,
                                             pixabay_api_url=pixabay_api_url))
        # Python 3.5-3.6
        else:
            loop = asyncio.get_event_loop()
            image_url_tuples = loop.run_until_complete(
                async_get_pixabay_image_urls(api_key=api_key,
                                             image_ids=image_ids,
                                             pixabay_api_url=pixabay_api_url))
        end = timer()
        print(f"Query Time Elapsed: {timedelta(seconds=end - start)}")
        print("Saving image urls...")
        save_image_urls(image_url_tuples=image_url_tuples,
                        image_urls_filepath=image_urls_filepath)

    print("Reading image urls...")
    image_url_tuples = read_image_urls(image_urls_filepath=image_urls_filepath)

    print("Downloading images...")
    start = timer()
    # Python 3.7+
    if sys.version_info >= (3, 7):
        asyncio.run(
            async_download_images(image_url_tuples=image_url_tuples,
                                  download_dir=download_dir))
    # Python 3.5-3.6
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            async_download_images(image_url_tuples=image_url_tuples,
                                  download_dir=download_dir))
    end = timer()
    print(f"Download Time Elapsed: {timedelta(seconds=end - start)}")
