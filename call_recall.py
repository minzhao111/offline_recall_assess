#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import sys
import requests


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--url', type=str, help='recall url')
    args = arg_parser.parse_args()
    url = args.url

    for line in sys.stdin:
        uid, ts = line.strip().strip('\t')
        url = url + f"&={uid}"
        result = requests.get(url)
        print('\t'.join(result.json()['data']) + '\n')