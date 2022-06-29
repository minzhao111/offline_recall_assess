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
#    echo $(ls -t ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/*_recall_result.txt | head -n $TOTAL_NEED_FILE_NUM) > ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/input_file.txt
#    cat $(ls -t ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/*_recall_result.txt | head -n $TOTAL_NEED_FILE_NUM) | python ${SCRIPT_ROOT_DIR}/merge_file.py --output_file $merge_file
    for file in $(ls -t ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/*_recall_result.txt | head -n $TOTAL_NEED_FILE_NUM); do
      echo $file >> ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/input_file.txt
#      cat $file >> $merge_file
    done
    python ${SCRIPT_ROOT_DIR}/merge_file.py --output_file $merge_file --input_files ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/input_file.txt
    rm ${SCRIPT_ROOT_DIR}/${RECALL_RESULT_FOLDER}/input_file.txt
    scp -oStrictHostKeyChecking=no -i ${PEM_FILE} $merge_file services@${HADOOP_IP}:${HADOOP_DATA_PATH}
    ssh -oStrictHostKeyChecking=no -i ${PEM_FILE} services@${HADOOP_IP} "cd ${HADOOP_DATA_PATH} && hadoop fs -rm ${HADOOP_UPLOAD_PATH}"
    ssh -oStrictHostKeyChecking=no -i ${PEM_FILE} services@${HADOOP_IP} "cd ${HADOOP_DATA_PATH} && hadoop fs -put ${MERGED_TEST_FILE_NAME} ${HADOOP_UPLOAD_PATH}"
    # 等文件拷贝过去以后, 在hue中执行命令建表, 命令参考以下：
    # "CREATE EXTERNAL TABLE temp.zhaomin_test_reqid (user_id INTEGER, req_id STRING, recall_docs STRING) row format delimited fields terminated by '\t' stored as TEXTFILE LOCATION 's3a://hdfs.bak/us/user/services/zhaomin/'"
}

merge_test_recall_result