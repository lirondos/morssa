#!/bin/bash

source ~/miniconda3/etc/profile.d/conda.sh
conda activate morssa
python /home/ealvarezmellado/morssa/morssa.py /home/ealvarezmellado/morssa/param/param.yaml /home/ealvarezmellado/morssa/ > /home/ealvarezmellado/morssa/log.txt 2>&1