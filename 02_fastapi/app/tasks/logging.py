from datetime import datetime,timezone
from app.db.init_celery import celery_app

@celery_app.task(name="app.tasks.logging.log_login_event")
def log_login_event(email:str,success:bool,ip:str) -> None:
    with open("login_audit_log.log","a") as f:
        log = f"{datetime.now(timezone.utc).isoformat()} |email =  {email} | success = {success} | ip = {ip} "
        f.write(log+"\n")
