# !/bin/bash

SCRIPT_ROOT_DIR=$(dirname "$(readlink -f "$0")")

source ${SCRIPT_ROOT_DIR}/conf/recall.conf

function merge_test_recall_result() {
    merge_file= ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/${MERGED_TEST_FILE_NAME}
    if [[ -f ${merge_file} ]]; then
      rm ${merge_file}
    fi
    for file in $(ls -t ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/*_recall_result.txt | head -n $TOTAL_NEED_FILE_NUM); do
      echo $file
      cat $file >> $merge_file
    scp -i ${PEM_FILE} $merge_file services@${HADOOP_IP}:${HADOOP_DATA_PATH}
}}