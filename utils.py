#!/usr/bin/env python

import os
import pathlib
import requests
from tqdm import tqdm


def download_file(
    url: str,
    filename: str,
    base: str = ".",
    dir: str = "data",
    overwrite: bool = False,
    silent: bool = False,
):
    """Method for downloading a file from the world-wide cyber space

    Arguments:
        filename {str} -- File name

    Keyword Arguments:
        base {str} -- Base directory (default: {"."})
        dir {str} -- Download directory (default: {"data"})
        overwrite {bool} -- If {True} existing files with be overwritten (default: {False})

    Returns:
        {str} -- Returns a pointer to `filename`.
    """
    filepath = os.path.join(base, dir, filename)

    if pathlib.Path(filepath).is_file() and not overwrite:
        print(f"{filepath} already exist. To overwrite pass `overwrite=True`")
        return

    chunkSize = 1024
    name, _ = os.path.splitext(filename)
    r = requests.get(url, stream=True)

    with open(filepath, "wb") as f:
        if not silent:
            pbar = tqdm(
                unit="B", unit_scale=True, total=int(r.headers["Content-Length"])
            )
        for chunk in r.iter_content(chunk_size=chunkSize):
            if chunk:  # filter out keep-alive new chunks
                if not silent:
                    pbar.update(len(chunk))
                f.write(chunk)

    return filename