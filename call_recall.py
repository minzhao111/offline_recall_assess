#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import sys
import requests
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--url', type=str, help='recall url')
    args = arg_parser.parse_args()
    url = args.url
    cache = set()
    for line in sys.stdin:
        if line in cache:  # 同一分钟, 假定召回结果不变，只记录一条召回结果即可
            continue
        logging.info(line)
        cache.add(line)
        uid, ts = line.strip().split('\t')
        tmp_url = url + f"&={uid}"
        result = requests.get(tmp_url).json()
        logging.info(f"{result}  {tmp_url}")
        recall_docids = [vaule['docid'] for vaule in result['documents']]
        print(f"{line}\t{' '.join(recall_docids)}")