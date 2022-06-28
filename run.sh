# !/bin/bash

SCRIPT_ROOT_DIR=$(dirname "$(readlink -f "$0")")

source ${SCRIPT_ROOT_DIR}/conf/recall.conf

if [[ ! -f ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER} ]]; then
  mkdir ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}
fi

while true; do
    start=$(TZ=UTC-8 date +%s)
    python ${SCRIPT_ROOT_DIR}/fetch_requests.py --limit 1000 --start $(TZ=UTC-8 date -d '-15 mins' +%s) > ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/${start}_uid_ts.txt
    end_fetch=$(TZ=UTC-8 date +%s)
    cat ${SCRIPT_ROOT_DIR}/uid_ts.txt | python ${SCRIPT_ROOT_DIR}/call_recall.py --url ${RECALL_URL} > ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/${start}_recall_result.txt
    end_call=$(TZ=UTC-8 date +%s)
    echo "Now time is $(TZ=UTC-8 date '+%Y-%m-%d %H:%M:%S'), fetch_requests cost time is $((end_fetch-start))s, call_recall cost time is $((end_call-end_fetch))s"
    echo -e "\n"
done

