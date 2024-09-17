import os
import re
import uuid
import urllib
import asyncio
import logging
from datetime import datetime

from sanic.response import ResponseStream
from sanic.response import json as sanic_json
from sanic.response import text as sanic_text
from sanic import request as sanic_request

from SystemCode.configs.database import CONNECT_MODE
from SystemCode.configs.basic import *
from SystemCode.core.file import File
from SystemCode.utils.general_utils import *
from SystemCode.connector.database.mysql_client import MySQLClient


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# init Mysql client
mysql_client = MySQLClient(CONNECT_MODE)


def init_folders():
    """
    init the necessary folders
    :return:
    """
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    if not os.path.exists(FILES_PATH):
        os.makedirs(FILES_PATH)

    if not os.path.exists(MODEL_PATH):
        os.makedirs(MODEL_PATH)


async def new_knowledge_base(req: sanic_request):
    """
    user_id, new_knowledge_base
    create new knowledge base for user, insert into milvus, mysql
    """
    user_id = safe_get(req, 'user_id')
    if type(user_id) == list:
        user_id = user_id[0]

    logging.info("[API]-[new knowledge base] user_id: %s", user_id)
    if user_id is None:
        return sanic_json({"code": 2002, "msg": f'[user_id]输入非法！request.json：{req.json}，请检查！'})
    is_valid = validate_user_id(user_id)
    if not is_valid:
        return sanic_json({"code": 2005, "msg": get_invalid_user_id_msg(user_id=user_id)})
    logging.info("new_knowledge_base %s", user_id)
    kb_name = safe_get(req, 'kb_name')
    if kb_name is None:
        return sanic_json({"code": 2002, "msg": f'[kb_name]输入非法！request.json：{req.json}，请检查！'})

    kb_id = 'KB' + uuid.uuid4().hex
    mysql_client.create_milvus_collection(user_id, kb_id, kb_name)
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")
    return sanic_json({"code": 200, "msg": "success create knowledge base {}".format(kb_id),
                       "data": {"kb_id": kb_id, "kb_name": kb_name, "timestamp": timestamp}})


async def upload_files(req: sanic_request):
    user_id = safe_get(req, 'user_id')
    if user_id is None:
        return sanic_json({"code": 2002, "msg": f'输入非法！request.form: {req.form}，request.files: {req.files}请检查！'})
    is_valid = validate_user_id(user_id)
    if not is_valid:
        return sanic_json({"code": 2005, "msg": get_invalid_user_id_msg(user_id=user_id)})
    logging.info("upload_files %s", user_id)
    kb_id = safe_get(req, 'kb_id')

    mode = safe_get(req, 'mode', default='soft')  # soft代表不上传同名文件，strong表示强制上传同名文件
    logging.info("mode: %s", mode)
    use_local_file = safe_get(req, 'use_local_file', 'false')
    if use_local_file == 'true':
        files = read_files_with_extensions()
    else:
        files = req.files.getlist('files')

    not_exist_kb_ids = mysql_client.check_kb_exist(user_id, [kb_id])
    if not_exist_kb_ids:
        msg = "invalid kb_id: {}, please check...".format(not_exist_kb_ids)
        return sanic_json({"code": 2001, "msg": msg, "data": [{}]})

    data = []
    local_files = []
    file_names = []
    for file in files:
        if isinstance(file, str):
            file_name = os.path.basename(file)
        else:
            logging.info('ori name: %s', file.name)
            file_name = urllib.parse.unquote(file.name, encoding='UTF-8')
            logging.info('decode name: %s', file_name)
        # 删除掉全角字符
        file_name = re.sub(r'[\uFF01-\uFF5E\u3000-\u303F]', '', file_name)
        file_name = file_name.replace("/", "_")
        logging.info('cleaned name: %s', file_name)
        file_name = truncate_filename(file_name)
        file_names.append(file_name)

    exist_file_names = []
    if mode == 'soft':
        exist_files = mysql_client.check_file_exist_by_name(user_id, kb_id, file_names)
        exist_file_names = [f[1] for f in exist_files]

    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M")

    for file, file_name in zip(files, file_names):
        if file_name in exist_file_names:
            continue
        file_size = len(file.body)
        file_path = os.path.join(FILES_PATH, file_name)
        file_id, msg = mysql_client.add_file(user_id, kb_id, file_name, timestamp, file_size, file_path)
        logging.info(f"{file_name}, {file_id}, {msg}")
        data.append(
            {"file_id": file_id, "file_name": file_name, "status": "gray", "bytes": file_size,
             "timestamp": timestamp})

    if exist_file_names:
        msg = f'warning，当前的mode是soft，无法上传同名文件{exist_file_names}，如果想强制上传同名文件，请设置mode：strong'
    else:
        msg = "success，后台正在飞速上传文件，请耐心等待"

    return sanic_json({"code": 200, "msg": msg, "data": data})


