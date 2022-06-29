#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import sys
import requests
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

executor = ThreadPoolExecutor(max_workers=60)

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)


def thread_func(line, url):
    result = requests.get(url).json()
    recall_docids = [vaule['docid'] for vaule in result['documents']]
    return f"{line}\t{' '.join(recall_docids)}"


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--url', type=str, help='recall url')
    args = arg_parser.parse_args()
    url = args.url
    cache = set()
    future_list = []
    for line in sys.stdin:
        if line in cache:  # 同一分钟, 假定召回结果不变，只记录一条召回结果即可
            continue
        line = line.strip()
        # logging.info(line)
        cache.add(line)
        uid, nb_req_id = line.strip().split('\t')
        tmp_url = url + f"&uid={uid}"
        future = executor.submit(thread_func, line=line, url=tmp_url)
        future_list.append(future)
    for future in as_completed(future_list):
        data = future.result()
        print(data)