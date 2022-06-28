# !/bin/bash

SCRIPT_ROOT_DIR=$(dirname "$(readlink -f "$0")")

source ${SCRIPT_ROOT_DIR}/conf/recall.conf

if [[ ! -f ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER} ]]; then
  mkdir ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}
fi

function cleanup() {
    find /data/sim-pipeline/offline_recall_assess/recall_result/ -type f -mtime +3 -exec rm -rf {} \;
}

while true; do
    start=$(TZ=UTC-8 date +%s)
    one_mins_later=$(TZ=UTC-8 date -d '1 mins' +%s)
    python ${SCRIPT_ROOT_DIR}/fetch_requests.py --limit 100000 --start $(TZ=UTC-8 date -d '-1 mins' +%s) > ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/${start}_uid_ts.txt
    end_fetch=$(TZ=UTC-8 date +%s)
    cat ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/${start}_uid_ts.txt | python ${SCRIPT_ROOT_DIR}/call_recall.py --url ${RECALL_URL} > ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/${start}_recall_result.txt
    end_call=$(TZ=UTC-8 date +%s)
    echo "Now time is $(TZ=UTC-8 date '+%Y-%m-%d %H:%M:%S'), fetch_requests cost time is $((end_fetch-start))s, call_recall cost time is $((end_call-end_fetch))s"
    while true; do
      if [[ $(TZ=UTC-8 date +%s) -gt one_mins_later ]]; then
        echo "We have waited about $(($(TZ=UTC-8 date +%s) - end_call))s. Starting the next round."
        break
      else
        sleep 5s
      fi
    done
    echo -e "\n"
    cleanup # 删除特别老的文件

    # 文件攒够以后退出(默认是攒够一个小时的数据)
    total_file_num=$(ls ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/*_uid_ts.txt | wc | awk '{print $1}')
    if [[ $total_file_num -gt $TOTAL_NEED_FILE_NUM ]]; then
      break
    fi
done

