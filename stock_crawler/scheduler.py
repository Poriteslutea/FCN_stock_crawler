import time 

from apscheduler.schedulers.background import BackgroundScheduler

from create_report import main

from loguru import logger

def update_stock_report():
    main('SLN35')

def scheduler():
    scheduler = BackgroundScheduler(
        timezone="Asia/Taipei"
    )

    scheduler.add_job(
        id="update_stock_report",
        func=update_stock_report,
        trigger="cron",
        hour="8",
        minute="0",
        day_of_week="mon-sat"
    )

    logger.info("Update stock report for product: SLN35...")
    scheduler.start()

if __name__ == "__main__":
    scheduler()
    while True:
        time.sleep(600)