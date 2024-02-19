
import json

from telegram import  Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

from loguru import logger
import json
from  HinetChangeIP import Hinet
from  HinetCheckNF import  HinetNFTest
from crontab import CronTab


hinet_change_ip = Hinet()
hinet_test_nf = HinetNFTest()




token = hinet_change_ip.API
# 创建当前用户的crontab，当然也可以创建其他用户的，但得有足够权限
my_cron = CronTab(user=True)

# 创建任务
cmd1="/root/HinetChangeIPShare/HinetChangeIP.sh >/dev/null 2>&1"
cmd2="/root/HinetChangeIPShare/HinetCheckNF.sh >/dev/null 2>&1"

changeip_job = my_cron.new(command=cmd1)
checknf_job = my_cron.new(command=cmd2)

changeip_job.setall(hinet_change_ip.changeIPCrons)
checknf_job.setall(hinet_change_ip.checkNfGfwCron)
changeip_job.enable(False) # 默认关闭
checknf_job.enable(False)
my_cron.write()










async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


# def main() -> None:
#     """Run the bot."""
#     # Create the Application and pass it your bot's token.
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [
            InlineKeyboardButton("更换IP", callback_data="1"),
            InlineKeyboardButton("检测当前奈非解锁", callback_data="2"),


        ],
        [
            InlineKeyboardButton("检测当前IP是否被墙", callback_data="3"),
            InlineKeyboardButton("开启每日换IP", callback_data="4"),

        ],
        [
            InlineKeyboardButton("关闭每日换IP", callback_data="5"),
            InlineKeyboardButton("每日换IP状态", callback_data="6"),

        ],

        [
            InlineKeyboardButton("开启奈非/FGW自动换IP", callback_data="7"),
            InlineKeyboardButton("关闭奈非/FGW自动换IP", callback_data="8"),


        ],
        [
            InlineKeyboardButton("获取当前ip", callback_data="9"),
            InlineKeyboardButton("退出菜单", callback_data="10"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    menumsg="选择你要进行的操作!"
    await update.message.reply_text(menumsg, reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    # print("query.data       ", query.data)

    if query.data == "1":
        msg=hinet_change_ip.change_ip_tg()
    elif query.data == "2":
        msg=hinet_test_nf.check_nf_tgbot()
    elif query.data == "3":
        msg=hinet_test_nf.check_gfw_block_tg()
    elif query.data == "4":
        changeip_job.enable()
        my_cron.write()
        msg="开启每日换IP成功 crontab is {}".format(hinet_change_ip.changeIPCrons)
    elif query.data == "5":
        changeip_job.enable(False)
        my_cron.write()
        msg="关闭每日换IP成功"
    elif query.data == "6":
        if not changeip_job.is_enabled():
            msg="每日换IP已关闭"
        else:
            msg="每日换IP已开启 crontab is {}".format(hinet_change_ip.changeIPCrons)

    elif query.data == "7":

        checknf_job.enable()
        my_cron.write()
        msg = "开启奈非/FGW自动换IP成功"
    elif query.data == "8":
        checknf_job.enable(False)
        my_cron.write()
        msg = "关闭奈非/FGW自动换IP成功"

    elif query.data == "9":
        msg="当前IP是 {}".format(hinet_change_ip.get_ip())
    elif query.data == "10":
        msg="exit success!"






    await query.answer()

    await query.edit_message_text(text=msg)


if __name__ == "__main__":


    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
