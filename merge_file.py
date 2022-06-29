#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import sys

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--output_file', help='merge output file')
    args = arg_parser.parse_args()

    req_id = set()

    output_file_io = open(args.output_file, 'w')
    for file in sys.stdin:
        for line in open(file.strip()):
            uid, req_id, recall_docs = line.strip().split('\t')
            if req_id in req_id:
                continue
            output_file_io.write(line)