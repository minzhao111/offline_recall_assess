#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import sys
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--output_file', help='merge output file')
    arg_parser.add_argument('--input_files', help='merge output file')
    args = arg_parser.parse_args()

    req_id_set = set()

    output_file_io = open(args.output_file, 'w')
    for file in open(args.input_files):
        for line in open(file.strip()):
            try:
                uid, req_id, recall_docs = line.strip().split('\t')
                if req_id in req_id_set:
                    continue
                req_id_set.add(req_id)
                output_file_io.write(line)
            except Exception as e:
                logging.info(f"Process {line} failed, the error is {e}")


if __name__ == '__main__':
    main()