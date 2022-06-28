# !/bin/bash

SCRIPT_ROOT_DIR=$(dirname "$(readlink -f "$0")")

source ${SCRIPT_ROOT_DIR}/conf/recall.conf

if [[ ! -f ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER} ]]; then
  mkdir ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}
fi

function merge_test_recall_result() {
    merge_file=${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/${MERGED_TEST_FILE_NAME}
    if [[ -f ${merge_file} ]]; then
      rm ${merge_file}
    fi
    # 取出最新的TOTAL_NEED_FILE_NUM份文件, merge后scp到hadoop机器上
    for file in $(ls -t ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/*_recall_result.txt | head -n $TOTAL_NEED_FILE_NUM); do
      echo $file
      cat $file >> $merge_file
    done
    scp -oStrictHostKeyChecking=no -i ${PEM_FILE} $merge_file services@${HADOOP_IP}:${HADOOP_DATA_PATH}
    ssh -oStrictHostKeyChecking=no -i ${PEM_FILE} services@${HADOOP_IP} "cd ${HADOOP_DATA_PATH} && hadoop fs -put ${MERGED_TEST_FILE_NAME} ${HADOOP_UPLOAD_PATH}"

}

merge_test_recall_result