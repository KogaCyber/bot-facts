import subprocess
import time
import os
import signal
import sys
from datetime import datetime
import pytz

TIMEZONE = pytz.timezone('Asia/Tashkent')

def get_tashkent_time():
    return datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

def run_bot():
    while True:
        try:
            print(f"\n[{get_tashkent_time()}] Starting bot...")
            
            # Запускаем основной скрипт бота
            process = subprocess.Popen([sys.executable, 'main.py'])
            
            # Ждем завершения процесса
            process.wait()
            
            # Если процесс завершился, выводим сообщение и перезапускаем
            exit_code = process.returncode
            print(f"\n[{get_tashkent_time()}] Bot stopped with exit code {exit_code}. Restarting in 15 seconds...")
            
            # Убеждаемся, что процесс действительно завершен
            try:
                os.kill(process.pid, signal.SIGTERM)
            except:
                pass
                
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("\nStopping bot (Ctrl+C pressed)")
            try:
                os.kill(process.pid, signal.SIGTERM)
            except:
                pass
            sys.exit(0)
            
        except Exception as e:
            print(f"\n[{get_tashkent_time()}] Error: {e}")
            time.sleep(15)
            continue

if __name__ == "__main__":
    run_bot()