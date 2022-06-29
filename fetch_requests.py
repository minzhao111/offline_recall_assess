#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import datetime
import argparse
import shlex
import requests
import re
import logging
from urllib import parse

from util import parse_query

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    level=logging.INFO)

"""
convert to timestamp in seconds
"""
def parse_ts(ts):
    if not ts:
        return None
    now = int(time.time())
    if ts == 'now':
        return now
    if ts[0] == '-':
        n = int(ts[:-1])
        unit = ts[-1]
        unit_interval = {
            's': 1,
            'm': 60,
            'h': 60 * 60,
            'd': 24 * 60 * 60
        }
        assert unit in unit_interval
        interval =  n * unit_interval[unit]
        return now + interval
    if len(ts) == 19:
        return int(ts) // 10**9
    if len(ts) == 10 and ts[0] == '1':
        return int(ts)
    date_format_map = {
        10: '%Y%m%d%H',
        12: '%Y%m%d%H%M',
    }
    assert len(ts) in date_format_map
    obj = datetime.datetime.strptime(ts, date_format_map[len(ts)])
    return int(obj.timestamp())


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--limit', type=int, default=1000,
                        help='number of request, 0 means no limit')
    parser.add_argument('--start', type=str, default='-10m',
                        help='time to start')
    parser.add_argument('--end', type=str, default='now',
                        help='time to end')
    args = parser.parse_args()

    args.start = parse_ts(args.start)
    args.end = parse_ts(args.end)
    assert args.start < args.end

    return args

def parse_curl(curl_command):
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('url')
    parser.add_argument('-H', action='append')

    components = shlex.split(curl_command)
    del components[0]
    args, _ = parser.parse_known_args(components)

    headers = dict(item.split(': ', 1) for item in args.H)
    cookies = {}
    cookie_header = headers.get('Cookie')
    if cookie_header:
        del headers['Cookie']
        cookies = dict(item.split('=', 1) for item in cookie_header.split('; '))

    url, params = parse_query(args.url)
    if 'limit' in params:
        params['limit'] = 10 ** 5 # fetch as many as possible
        # params['limit'] = 10000 # fetch as many as possible

    return url, params, headers, cookies

def fetch(start, end, limit, url, params, headers, cookies, filter=None):
    # requests limit max 10**5 entries per query, so be careful with interval
    limit = max(0, limit)
    interval = 1 * 60
    cur_end = end
    results = []
    while start < cur_end and (limit <= 0 or len(results) < limit):
        next_end = max(start, cur_end - interval)
        params['start'] = next_end * 10 ** 9
        params['end'] = cur_end * 10**9
        cur_end = next_end
        r = requests.get(url, params=params, headers=headers, cookies=cookies)
        data = r.json()
        for node in data.get('data', {}).get('result', []):
            for value in node.get('values', []):
                ts, query = value
                query = query.split('ACCESS: ')[1].strip()
                if not filter or filter(query):
                    try:
                        query_parsed = parse.unquote(query)
                        # print(query_parsed)
                        uid = re.findall('userid=(\d+)', query_parsed)[0]
                        nb_req_id = re.findall('nb_req_id=(\w+)', query_parsed)[0]
                        print(f'{uid}\t{nb_req_id}') # 输入uid nb_req_id，后续将基于此进行请求
                    except Exception as e:
                        logging.info(f"parse {query} failed, the exception is {e}")


def default_filter(query):
    _, params = parse_query(query)
    if params.get('pressure') == 'true':
        return False
    if params.get('debug') == 'true':
        return False
    if params.get('skipFlush') == 'true':
        return False
    if params.get('skipLog') == 'true':
        return False
    return True

def main(args, curl):
    url, params, headers, cookies = parse_curl(curl)
    results = fetch(args.start, args.end, args.limit, url, params, headers, cookies, default_filter)
    return results


if __name__ == '__main__':
    # curl command copied from chrome, replace with yours, eg: {app_kubernetes_io_instance="monica-k8s"} |= "ACCESS" |= "mode=ie"
    curl = """
  curl 'https://grafana.n.newsbreak.com/api/datasources/proxy/24/loki/api/v1/query_range?direction=BACKWARD&limit=2000&query=%7Bapp_kubernetes_io_instance%3D%22monica-k8s%22%7D%20%7C%3D%20%22ACCESS%22%20%7C%3D%20%22mode%3Die%22&start=1656470574373000000&end=1656474174373000000&step=5' \
  -H 'Accept-Language: zh-CN,zh;q=0.9' \
  -H 'Connection: keep-alive' \
  -H 'Cookie: nb_bucket_share-button-position-exp=other; nb_bucket_share-lp-1=other; nb_bucket_share-lp-style=test; nb_wuid=c8f4229c-3f0c-46ce-a499-bd7e5b0a813f; nb_bucket_general=g7; nb_bucket_share-lp-nav=test; nb_bucket_share-lp-brand=test; nb_bucket_share-lp-scroll-btn=control; __gads=ID=8f0fd309e0376a5d:T=1637052074:S=ALNI_MbMrVUOGrTV4_MfNijZhBmeMoSaKw; nb_bucket_share-lp-2=other; nb_bucket_share-positive-feedback-2=useful; nb_bucket_unsub-frequency=control; nb_bucket_newsletter-lp-2=test; nb_bucket_summary-article-button=control; nb_bucket_newsletter-article-variant-5=control; nb_t_v2=tze2qmfLt8KaX+B+0HCEL0QXhxw9wxeZ5L5ncK+a0CW3Hf/yGd6dt1yKM8WrRN595GPIoU9sAxv5W5aXXmF3oTPukUaPU3brlolGuU8rqZGAx+wKn2wUEKYBMM+tkaBG; push_user_id=168590741; nb_t=tze2qmfLt8KaX+B+0HCEL0QXhxw9wxeZ5L5ncK+a0CW3Hf/yGd6dt1yKM8WrRN595GPIoU9sAxv5W5aXXmF3oTPukUaPU3brlolGuU8rqZGAx+wKn2wUEKYBMM+tkaBG; nb_bucket_newsletter-channel-variant-5=test; nb_bucket_read-in-app=control; nb_bucket_newsletter-lp-3=versionB; _fbp=fb.1.1651827098589.1393950434; nb_bucket_preview-lp-2=control; nb_bucket_content-expand=test; nb_bucket_newsletter-lp-2b=control; _gcl_au=1.1.409153344.1655289287; amplitude_id_42c5fd9815508f0054e1f8253213b939newsbreak.com=eyJkZXZpY2VJZCI6IjQ0NTU1NzkxLTY4NjgtNGMwNy1iYTIyLWU3MjA4Y2MwNTRjN1IiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTY1NTQ0NTI0NDE5NCwibGFzdEV2ZW50VGltZSI6MTY1NTQ0NTI0NDE5NSwiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6Mywic2VxdWVuY2VOdW1iZXIiOjN9; amplitude_id_946c9f37ae37636fa4587f12dd74a039_newsbreaknewsbreak.com=eyJkZXZpY2VJZCI6IjdlNjMxYjI0LWUyYWMtNDkzZC1iZTgyLTk1N2U5OWUyZDU2ZFIiLCJ1c2VySWQiOm51bGwsIm9wdE91dCI6ZmFsc2UsInNlc3Npb25JZCI6MTY1NTQ0NTI0NDE5OCwibGFzdEV2ZW50VGltZSI6MTY1NTQ0NTI0NDE5OCwiZXZlbnRJZCI6MCwiaWRlbnRpZnlJZCI6MCwic2VxdWVuY2VOdW1iZXIiOjB9; _ga=GA1.2.1167252793.1635908067; __gpi=UID=00000506d0152465:T=1650945718:RT=1655800700:S=ALNI_MalPzXVQXd_EnPahp_v2h8HzaA-Pw; nb_bucket_read-in-app-position=test; _ga_R9E7L6CF8Y=GS1.1.1656342089.33.0.1656342089.0; grafana_session=60cd9148dead28a34b3d38f319dc136e' \
  -H 'Referer: https://grafana.n.newsbreak.com/explore?orgId=1&left=%7B%22datasource%22:%22Loki%20Prod%22,%22queries%22:%5B%7B%22expr%22:%22%7Bapp_kubernetes_io_instance%3D%5C%22monica-k8s%5C%22%7D%20%7C%3D%20%5C%22ACCESS%5C%22%20%7C%3D%20%5C%22mode%3Die%5C%22%22,%22refId%22:%22A%22%7D%5D,%22range%22:%7B%22from%22:%22now-1h%22,%22to%22:%22now%22%7D%7D' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36' \
  -H 'accept: application/json, text/plain, */*' \
  -H 'sec-ch-ua: ".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'x-grafana-org-id: 1' \
  --compressed
    """

    args = parse_args()
    results = main(args, curl)

