import subprocess
import sys
import time
import subprocess
import schedule
import signal

def getDailyQuestion():
    print("running....")
    subprocess.run([f"{sys.executable}","dailyQuestion.py"])
    return

def signal_handler(signum,frame):
    print("\n程序结束！")
    sys.exit(0)
signal.signal(signal.SIGINT,signal_handler)

if __name__ == '__main__' :
    print("开始运行，等待定时触发")

    schedule.every().day.at("00:00").do(getDailyQuestion)

    while True :
        schedule.run_pending()
        time.sleep(50)