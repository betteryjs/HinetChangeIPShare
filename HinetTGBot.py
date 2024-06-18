# stop
import signal
import sys


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

from loguru import logger
import json

# loads config
with open("config.json", 'r') as file:
    config_json = json.loads(file.read())

authorized_users = config_json["authorized_users"]
logName = config_json["name"] + '.log'
logger.remove(handler_id=None)  # 清除之前的设置
logger.add(logName, rotation="15MB", encoding="utf-8", enqueue=True, retention="1 days")

from telebot.util import quick_markup
import telebot
from HinetBase import Hinet

hinet = Hinet()
token = hinet.API
bot = telebot.TeleBot(token)


def send_menu(message):
    button = {
        "更换IP": {"callback_data": "1"},
        "检测当前奈非解锁": {"callback_data": "2"},
        "检测当前IP是否被墙": {"callback_data": "3"},
        "开启每日换IP": {"callback_data": "4"},
        "关闭每日换IP": {"callback_data": "5"},
        "每日换IP状态": {"callback_data": "6"},
        "开启奈非自动换IP": {"callback_data": "7"},
        "关闭奈非自动换IP": {"callback_data": "8"},
        "奈非自动换IP状态": {"callback_data": "9"},
        "开启GFW自动换IP": {"callback_data": "10"},
        "关闭GFW自动换IP": {"callback_data": "11"},
        "GFW自动换IP状态": {"callback_data": "12"},
        "获取当前ip": {"callback_data": "13"},
        "退出菜单": {"callback_data": "14"},

        # "当前日志": {"callback_data": "11"}

    }
    menu_message = bot.send_message(message.chat.id, "选择你要进行的操作! ",
                                    reply_markup=quick_markup(button, row_width=2))


def is_authorized(user_identifier):
    # 检查用户 ID 或用户名是否在授权用户列表中

    if str(user_identifier.id) in authorized_users:
        return True
    elif user_identifier.username in authorized_users:
        return True
    return False


@bot.message_handler(commands=['menu'])
def menu_command(message):
    if is_authorized(message.from_user):
        send_menu(message)
    else:
        bot.reply_to(message, f"You are not authorized to use this bot. id is {message.from_user.id}"
                              f"username is {message.from_user.username}")


@bot.callback_query_handler(func=lambda call: True)
def refresh(call):
    if call.data == "1":
        logger.info("chick 更换IP")
        msg = hinet.change_ip()
        bot.send_message(call.message.chat.id, msg)

    elif call.data == "2":
        logger.info("chick 检测当前奈非解锁")
        msg = hinet.check_nf()
        bot.send_message(call.message.chat.id, msg)


    elif call.data == "3":
        logger.info("chick 检测当前IP是否被墙")
        msg = hinet.check_gfw_block()
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "4":
        logger.info("chick 开启每日换IP")
        hinet.start_timer("changeip")
        msg = "开启每日换IP成功 crontab is {}".format(hinet.changeIPCrons)
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "5":
        logger.info("chick 关闭每日换IP")
        hinet.stop_timer("changeip")
        msg = "关闭每日换IP成功"
        bot.send_message(call.message.chat.id, msg)


    elif call.data == "6":

        logger.info("chick 每日换IP状态")
        if hinet.is_timer_running("changeip"):
            msg = "每日换IP已开启 crontab is {}".format(hinet.changeIPCrons)
        else:
            msg = "每日换IP已关闭"
        bot.send_message(call.message.chat.id, msg)





    elif call.data == "7":

        logger.info("chick 开启奈非自动换IP")
        hinet.start_timer("checkNf")
        msg = "开启奈非自动换IP成功"
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "8":
        logger.info("chick 关闭奈非自动换IP")
        hinet.stop_timer("checkNf")
        msg = "关闭奈非自动换IP成功"
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "9":

        logger.info("chick 奈非自动换IP状态")
        if hinet.is_timer_running("changeip"):
            msg = "奈非自动换IP已开启 crontab is {}".format(hinet.checkNfGfwCron)
        else:
            msg = "奈非自动换IP已关闭"
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "10":
        logger.info("chick 开启GFW自动换IP")

        hinet.start_timer("checkGfw")
        msg = "开启被墙自动换IP成功"
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "11":
        logger.info("chick 关闭GFW自动换IP")
        hinet.stop_timer("checkGfw")
        msg = "关闭被墙自动换IP成功"
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "12":

        logger.info("chick GFW自动换IP状态")
        if hinet.is_timer_running("checkGfw"):
            msg = "被墙自动换IP已开启 crontab is {}".format(hinet.checkNfGfwCron)
        else:
            msg = "被墙自动换IP已关闭"
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "13":
        logger.info("chick 获取当前ip")
        msg = "当前IP是 {}".format(hinet.get_ip())
        bot.send_message(call.message.chat.id, msg)



    elif call.data == "14":
        msg = "exit success!"
        logger.info("chick 退出菜单")
        bot.send_message(call.message.chat.id, msg)

    bot.delete_message(call.message.chat.id, call.message.message_id)


if __name__ == "__main__":
    bot.infinity_polling()
