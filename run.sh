# !/bin/bash

SCRIPT_ROOT_DIR=$(dirname "$(readlink -f "$0")")

source ${SCRIPT_ROOT_DIR}/conf/recall.conf

while true; do
    python ${SCRIPT_ROOT_DIR}/fetch_requests.py \
      --limit 1000 \
      --start '-5m' > ${SCRIPT_ROOT_DIR}/uid_ts.txt

    cat ${SCRIPT_ROOT_DIR}/uid_ts.txt | python ${SCRIPT_ROOT_DIR}/call_recall.py > ${SCRIPT_ROOT_DIR}/recall_result.txt
done

