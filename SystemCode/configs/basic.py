PROJECT_NAME = 'ORAG'
LOG_LEVEL = 'DEBUG'

SENTENCE_SIZE = 100
EMBEDDING_MAX_WORKER = 4
EMBEDDING_HOST = 'localhost'
EMBEDDING_PORT = 18000

# ----------------- 以下为File Server相关配置 -----------------
FILE_SERVER_PORT = 18001
TASK_TIMEOUT = 10 * 60  # 任务超时时间，单位为秒, 超时后删除任务


# ----------------- 以下为URL Loader相关配置 -----------------
# URL解析时子链接的数量
MAX_URL_DEPTH = 5
