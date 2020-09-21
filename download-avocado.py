#!/usr/bin/env python

import argparse
import os
import sys

module_path = os.path.abspath(os.path.join("../experiments"))
if module_path not in sys.path:
    sys.path.append(module_path)

from utils import download_file

parser = argparse.ArgumentParser(description="Peax-Avocado")
parser.add_argument("chrom", help="chromosome name")

try:
    args = parser.parse_args()
except SystemExit as err:
    if err.code == 0:
        sys.exit(0)
    if err.code == 2:
        parser.print_help()
        sys.exit(0)
    raise

download_dir = "models"

base_url = "https://noble.gs.washington.edu/proj/avocado/model/"

download_file(
    f"{base_url}avocado-{args.chrom}.json",
    f"avocado-{args.chrom}.json",
    dir="models"
)
download_file(
    f"{base_url}avocado-{args.chrom}.h5",
    f"avocado-{args.chrom}.h5",
    dir="models"
)
