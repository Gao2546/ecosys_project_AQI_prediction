from celery import Celery
import os

# กำหนดการเชื่อมต่อกับ Redis
celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task(bind=True, max_retries=3)
def save_image_task(self, filepath):
    try:
        # กำหนดโฟลเดอร์ถาวร
        permanent_dir = 'permanent_uploads'
        if not os.path.exists(permanent_dir):
            os.makedirs(permanent_dir)
        
        # ย้ายไฟล์จากโฟลเดอร์ชั่วคราวไปยังโฟลเดอร์ถาวร
        os.rename(filepath, os.path.join(permanent_dir, os.path.basename(filepath)))
        print(f"File {filepath} has been moved to {permanent_dir}")
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        self.retry(exc=e, countdown=60)  # retry หลังจาก 60 วินาที
