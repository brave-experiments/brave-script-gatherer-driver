#!/bin/bash
CUR_DIR=`dirname "$(readlink -f "$0")"`
source "$CUR_DIR/../bin/activate";
ALEXA_LIST=$CUR_DIR/alexa-lists/alexa-1m.txt;
python2.7 $CUR_DIR/scrape.py \
    --domain-list $ALEXA_LIST;
