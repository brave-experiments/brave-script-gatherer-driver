#!/bin/bash
CUR_DIR=`dirname "$(readlink -f "$0")"`
source "$CUR_DIR/../bin/activate";
python $CUR_DIR/abp_alexa_scrape.py;
