import time
from apscheduler.schedulers.background import BackgroundScheduler
from evaluate import evaluate_all_users

scheduler = BackgroundScheduler()
scheduler.add_job(evaluate_all_users, 'interval', seconds=300)
scheduler.start()

try:
    while True:  # 防止主线程退出
        time.sleep(1)
except KeyboardInterrupt:
    scheduler.shutdown()