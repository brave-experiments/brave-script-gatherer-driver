#!/usr/bin/env python2.7
"""
Command line utility for dispatching script gathering lambda functions.
"""
import argparse
import json
import sys
import uuid
import boto3
import botocore
from multiprocessing import Pool

LAMBDA_FUNC_NAME = "arn:aws:lambda:us-east-1:275005321946:function:brave-script-gatherer"
COIN_TERMS = [
    # CoinHive
    "CoinHive.Anonymous",

    # CryptoLoot
    "CryptoLoot.Anonymous",

    # deepMiner
    "deepMiner.Anonymous",
]

COIN_DOMAINS = [
    # CryptoLoot
    "crypto-loot.com",
    "cryptoloot.pro",

    # CoinImp
    "coinimp.com",
    "www.hashing.win",
    "www.freecontent.bid",
    "webassembly.stream",

    # Minr
    "cnt.statistic.date",
    "cdn.static-cnt.bid",
    "ad.g-content.bid",
    "cdn.jquery-uim.download",
]

def target(subproc_args):
    try:
        rank, url, region, batch_tag, debug = subproc_args
        scrape_args = {
            "url": "http://" + url,
            "rank": rank,
            "terms": COIN_TERMS,
            "domains": COIN_DOMAINS,
            "batch": batch_tag,
            "region": region,
        }

        if debug:
            scrape_args["debug"] = debug

        config = botocore.client.Config(read_timeout=360, retries={'max_attempts': 0})
        client = boto3.client('lambda', region_name='us-east-1', config=config)
        print(u"{}: Scraping {}".format(rank, url))
        client.invoke(
            FunctionName=LAMBDA_FUNC_NAME,
            InvocationType="RequestResponse",
            LogType="None",
            Payload=json.dumps(scrape_args, ensure_ascii=False)
        )
    except Exception, e:
        error_params = [url, str(e)]
        sys.stderr.write("Error scraping {}\n{}\n".format(*error_params))


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Check a file of domains for "
                                                 "coin miner scripts")
    PARSER.add_argument("--domain-list", "-d", required=True,
                        help="Path to a file of domains, in Alexa popularity "
                             "order.")
    PARSER.add_argument("--country-code", "-c", default=None,
                        help="The two character country code of the domain set "
                             "being crawled.  If omitted, then the dataset "
                             "is recorded as being a global recording.")
    PARSER.add_argument("--debug", action="store_true",
                        help="Indicates that the lambda function should print "
                             "debugging information.")
    ARGS = PARSER.parse_args()

    TAG = str(uuid.uuid4())
    CC = ARGS.country_code
    DEBUG = ARGS.debug

    with open(ARGS.domain_list, "r") as handle:
        SUBPROCESS_ARGS = ((r + 1, d.strip(), CC, TAG, DEBUG) for (r, d) in enumerate(handle))
        POOL = Pool(processes=50)
        POOL.map(target, SUBPROCESS_ARGS)
        POOL.close()
        POOL.join()
