#!/usr/bin/env python

import os
import pathlib
import sys

module_path = os.path.abspath(os.path.join("../experiments"))
if module_path not in sys.path:
    sys.path.append(module_path)

from utils import download_file

pathlib.Path("data").mkdir(parents=True, exist_ok=True)

download_dir = "data"

base_url = "https://egg2.wustl.edu/roadmap/data/byFileType/signal/consolidated/macs2signal/foldChange/"

# GM12878 DNase-seq read-depth normalized signal
download_file(base_url + "E116-DNase.fc.signal.bigwig", "E116-DNase.fc.signal.bigWig")

# GM12878 H3K27ac ChIP-seq fold change over control
download_file(
    base_url + "E116-H3K27ac.fc.signal.bigwig", "E116-H3K27ac.fc.signal.bigWig"
)
