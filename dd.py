#!/usr/bin/python3
# coding:utf-8
'''
APP模拟自动化工具

@version v1.0

@author soeasyd@gmail.com

@date 2018-11-14

@require python3

* 功能操作
* 界面识别
* 操作上报
'''
import time, datetime
import os
import subprocess
import requests
from PIL import Image
import pytesseract
import random

IMAGE_API = "http://WEBHOOK"

OP_START_APP = "adb shell am start -n com.alibaba.android.rimet/.biz.SplashActivity"
OP_KILL_APP = "adb shell am force-stop  com.alibaba.android.rimet"
OP_BACK = "adb shell input keyevent 4"
OP_INPUT_CLEAR = "adb shell input keyevent 67"
OP_LOCK_AND_UNLOCK = "adb shell input keyevent 26"

USERNAME = "账户"
PASSWORD = "密码"


def runCommand(command):
    # status, output = commands.getstatusoutput(command)
    output = subprocess.check_output(command, shell=True)

    return True, str(output, encoding="utf-8")


def clearInput():
    for i in range(1, 20):
        runCommand(OP_INPUT_CLEAR)


def login():
    # 判断是否需要登录
    if is_login() != True:
        time.sleep(5)
        if is_home() != True:
            print("[!][%s]非登录界面\n" % log_time())
            return False
        else:
            print("[!][%s]用户已登陆\n" % log_time())
            return True

    # 定位
    command = "adb shell input tap 540 460"
    _, result = runCommand(command)

    #
    clearInput()

    # 账户
    command = ("adb shell input text '%s'" % USERNAME)
    runCommand(command)

    print("[*][%s]账户输入正常\n" % log_time())

    command = "adb shell input tap 600 600"
    runCommand(command)

    # 密码
    command = ("adb shell input text '%s'" % PASSWORD)
    runCommand(command)

    print("[*][%s]密码输入正常\n" % log_time())

    # submit
    command = "adb shell input tap 325 716"
    runCommand(command)

    print("[*][%s]登录正常\n" % log_time())

    return True


def home():
    if is_home() != True:
        print("[!][%s]非主界面\n" % log_time())
        return False

    # `工作`菜单
    command = "adb shell input tap 370 1224"
    runCommand(command)

    print("[*][%s]进入`工作菜单`正常\n" % log_time())

    if is_work() != True:
        print("[!][%s]非工作模块\n" % log_time())
        return False

    # `考勤`菜单
    command = "adb shell input tap 110 840"
    runCommand(command)

    # 等待`打卡`模块加载
    time.sleep(10)

    if is_sign() != True:
        print("[!][%s]非考勤模块\n" % log_time())
        return False

    print("[*][%s]进入`考勤菜单`正常\n" % log_time())

    # 等待定位
    time.sleep(6)

    # 外勤判断
    # TODO

    # `打卡`按钮
    command = "adb shell input tap 360 530"
    runCommand(command)

    # 等待结果
    time.sleep(3)

    print("[*][%s]打卡完成\n" % log_time())

    # 上传结果
    # upload()

    return True


def is_login():
    return op_judge("login")


def is_home():
    return op_judge("home")


def is_work():
    return op_judge("work")


def is_sign():
    return op_judge("sign")


# 截图
def screen_shot():
    command = "adb shell 'screencap -p > /sdcard/daka.png'"
    runCommand(command)

    filename = time.strftime("%H-%M-%S", time.localtime()) + ".png"
    command = "adb pull /sdcard/daka.png %s" % filename

    _, result = runCommand(command)

    if result.find("error") > 0:
        print("[!][%s]截图异常 => %s\n" % (log_time(), result))

        return False

    print("[*][%s]截图正常 => %s\n" % (log_time(), filename))

    return True, filename


# 截图上传
def upload():
    status, filename = screen_shot()

    if status == False:
        print("[!][%s]结果上报失败 => %s\n" % (log_time()))
        return False

    if os.path.exists(filename) == False:
        print("[!][%s]文件不存在 => %s\n" % (log_time(), filename))
        return False

    # 裁剪
    img = Image.open(filename)
    uploadFile = img.crop((40, 280, 680, 1160))
    uploadFile.save("upload.png")

    data = {"filename": ("upload.png", open("upload.png", "rb"), "image/png")}

    resp = requests.post(IMAGE_API, files=data)

    if resp.status_code != 200:
        print("[*][%s]上传异常  => %s \n" % (log_time(), resp.text))
        return False
    else:
        _r = resp.json()
        if _r.code != 0:
            print("[*][%s]上传异常  => %s \n" % (log_time(), _r.message))
            return False

    print("[*][%s]上传正常 => %s\n" % (log_time(), "upload.png"))

    return True


# 识图
def op_judge(action):
    status, filename = screen_shot()

    if status == False:
        return False

    img = Image.open(filename)

    # OCR
    content = pytesseract.image_to_string(img, "chi_sim")

    if action == "login":
        return True if (content.find("忘记密码") > 0 and content.find("新用户注册") > 0) else False

    if action == "home":
        return True if (content.find("工作") > 0 and content.find("通讯录") > 0) else False

    if action == "work":
        return True if (content.find("考勤打卡") > 0 and content.find("签到") > 0) else False

    if action == "sign":
        return True if (content.find("帮助") > 0 and content.find("点此选择班次") > 0) else False

    return False


def log_time():
    return time.strftime("%H:%M:%S", time.localtime())


# 设备判断
def devices():
    command = "adb devices"
    status, result = runCommand(command)

    data = result.split("\n")

    if data[1] == "":
        print("[!][%s] 未发现设备\n" % log_time())
        return False

    device = data[1].split("\t")

    print("[*][%s] 设备`%s`连接正常 \n" % (log_time(), device[0]))

    return True


# 启动
def runApp():
    runCommand(OP_KILL_APP)

    time.sleep(1)

    _, result = runCommand(OP_START_APP)

    print("[*][%s]APP启动正常\n" % log_time())
    return True


def main():
    week_day = datetime.datetime.now().weekday() + 1
    if (week_day == 6 or week_day == 7):
        print("[!][%s]周末 %s" % (log_time(), week_day))
        return

    if devices() == False:
        return

    if runApp() == False:
        return

    time.sleep(8)

    if login() == False:
        return
    rand_time = random.randint(10, 60)

    print("[*][%s]随机睡眠时间:%d" % (log_time(), rand_time))

    time.sleep(rand_time)

    if home() == False:
        return

    runCommand(OP_KILL_APP)
    runCommand("rm -rf *.png")
	runCommand(OP_LOCK_AND_UNLOCK)
    print("[*][%s]执行完成\n" % log_time())

if __name__ == "__main__":
    main()


