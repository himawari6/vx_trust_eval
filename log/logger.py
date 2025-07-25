import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage()
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record, ensure_ascii=False)

def get_logger(name="trust_eval"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.FileHandler('log/log.jsonl', encoding='utf-8')  # 日志写入文件
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger