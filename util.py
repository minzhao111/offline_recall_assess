#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import urllib.parse


def parse_query(query):
    r = urllib.parse.urlparse(query)
    url = f'{r.scheme}://{r.netloc}/{r.path}' if r.netloc else f'{r.path}'
    params = urllib.parse.parse_qs(r.query) if r.query else {}
    # parse_qs return {k: [...]} here we retain only the first
    return url, {k: v[0] for k, v in params.items()}
