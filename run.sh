# !/bin/bash

SCRIPT_ROOT_DIR=$(dirname "$(readlink -f "$0")")

source ${SCRIPT_ROOT_DIR}/conf/recall.conf

while true; do
    python ${SCRIPT_ROOT_DIR}/fetch_requests.py --limit 1000 --start $(TZ=UTC-8 date -d '-15 mins' +%s) > ${SCRIPT_ROOT_DIR}/uid_ts.txt
    cat ${SCRIPT_ROOT_DIR}/uid_ts.txt | python ${SCRIPT_ROOT_DIR}/call_recall.py --url ${RECALL_URL} > ${SCRIPT_ROOT_DIR}/recall_result.txt
done

