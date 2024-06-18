import json
import re
import subprocess
import requests
from cloudflare_ddns import CloudFlare
from loguru import logger
import time
from datetime import datetime
from croniter import croniter
from threading import Thread, Event


class Hinet(object):

    def __init__(self):
        with open("config.json", 'r') as file:
            configJson = json.loads(file.read())
        self.email = configJson["email"]
        self.api_key = configJson["api_key"]
        self.domain = configJson["domain"]
        self.changeHinetIpUrl = configJson["changeHinetIpUrl"]
        self.API = configJson["TGBotAPI"]
        self.sendTelegramUrl = "https://api.telegram.org/bot" + self.API + "/sendMessage"
        self.chartId = configJson["chartId"]
        self.ddnsUrl = configJson["ddnsUrl"]
        self.name = configJson["name"]
        self.cf = CloudFlare(self.email, self.api_key, self.domain)
        self.changeIPCrons = configJson["changeIPCrons"]  # "0 3 * * *"
        self.checkNfGfwCron = configJson["checkNfGfwCron"]  # "*/1 * * * *"
        self.checknfport = configJson["checknfport"]
        self.checkGFWUrl = configJson["checkGFWUrl"]
        self.checkgfwport = configJson["checkgfwport"]
        # 定时器存储
        self.timers = {}

        # 初始化定时器，但不启动
        self.initialize_timer('checkGfw', self.checkNfGfwCron, self.check_gfw_block)
        self.initialize_timer('checkNf', self.checkNfGfwCron, self.check_nf)
        self.initialize_timer('changeip', self.changeIPCrons, self.change_ip)

    def change_ip(self):
        try:
            start = time.time()
            self.stop_timer("checkGfw")
            self.stop_timer("checkNf")
            response = requests.get(url=self.changeHinetIpUrl)
            resipv4_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'  # 正则表达式匹配IPv4地址
            res_ip_list = re.findall(resipv4_pattern, response.text)
            if res_ip_list != []:
                res_ip = res_ip_list[0]
                self.cf_ddns(res_ip)
                msg = "[{}]-[IP更换成功]-[当前IP {}]-[用时 {}s ]".format(self.name, res_ip, int(time.time() - start))
            else:
                logger.error("response.text -------> {}".format(response.text))
                msg = "[{}]-[IP更换失败]-[当前IP {}]".format(self.name, self.get_ip())
            logger.info(msg)
            self.start_timer("checkGfw")
            self.start_timer("checkNf")
            return msg
        except Exception as err:
            logger.error(err)
            msg = "[{}]-[IP更换失败]-[当前IP {}]".format(self.name, self.get_ip())
            logger.error(msg)
            self.start_timer("checkGfw")
            self.start_timer("checkNf")
            return msg

    def get_ip(self):
        try:
            self.cf.refresh()
            res = self.cf.get_record('A', self.ddnsUrl)
            ip = res["content"]
            logger.info("ip is {}".format(ip))
            return ip

        except Exception as err:
            logger.error(err)

    def sendTelegram(self, msg):
        params = {
            "chat_id": self.chartId,
            "text": msg
        }
        resp = requests.get(url=self.sendTelegramUrl, params=params)
        logger.info(resp.text)

    def cf_ddns(self, ip):
        logger.info("............start cf ddns.....................")
        res = self.cf.get_record('A', self.ddnsUrl)
        logger.info("改变前 " + res["content"])
        self.cf.update_record(dns_type='A', name=self.ddnsUrl, content=ip, ttl=60)
        res = self.cf.get_record('A', self.ddnsUrl)
        logger.info("改变后 " + res["content"])
        logger.info("............end cf ddns.......................")

    def check_nf(self):
        cmds = "./nf -proxy socks5://" + self.get_ip() + ":" + self.checknfport
        logger.info(cmds)
        p = subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        res = out.decode()
        ipv4res = res[0:res.find("[IPv6]")]
        logger.info(res)
        # ipv6res = res[res.find("[IPv6]"):]
        if "您的出口IP完整解锁Netflix" in ipv4res:
            msg = "[{}]-[奈非检测]-[您的出口IP完整解锁Netflix]".format(self.name)
            logger.info(msg)
        elif "您的网络可能没有正常配置IPv4" in ipv4res:
            # 正在换ip 或者网络波动
            msg = "[{}]-[奈非检测]-[您的网络可能没有正常配置IPv4]".format(self.name)
            logger.error(msg)
        else:
            msg = "[{}]-[奈非检测]-[奈非检测失败]".format(self.name)
            logger.info(msg)
            self.change_ip()
        return msg

    def check_gfw_block(self):
        gfwUrl = self.checkGFWUrl + self.get_ip() + ":" + self.checkgfwport
        resp = requests.get(url=gfwUrl).json()
        logger.info(resp)
        if resp["isblock"] == True:
            msg = "[{}]-[GFW检测]-[IP ban 啦]".format(self.name)
            logger.info(msg)
            self.change_ip()
        else:
            msg = "[{}]-[GFW检测]-[IP正常]".format(self.name)
            logger.info(msg)
        return msg

    def schedule_cron(self, cron_expression, stop_event, job):
        base_time = datetime.now()
        cron = croniter(cron_expression, base_time)

        while not stop_event.is_set():
            next_run = cron.get_next(datetime)
            sleep_duration = (next_run - datetime.now()).total_seconds()

            if sleep_duration > 0:
                stop_event.wait(sleep_duration)
                if not stop_event.is_set():
                    job()

    def initialize_timer(self, timer_id, cron_expression, job):
        stop_event = Event()
        self.timers[timer_id] = {
            'cron_expression': cron_expression,
            'job': job,
            'stop_event': stop_event,
            'thread': None
        }

    def start_timer(self, timer_id):
        if timer_id in self.timers and self.timers[timer_id]['thread'] is None:
            cron_expression = self.timers[timer_id]['cron_expression']
            job = self.timers[timer_id]['job']
            stop_event = self.timers[timer_id]['stop_event']
            t = Thread(target=self.schedule_cron, args=(cron_expression, stop_event, job))
            self.timers[timer_id]['thread'] = t
            t.start()

    def stop_timer(self, timer_id):
        if timer_id in self.timers and self.timers[timer_id]['thread'] is not None:
            self.timers[timer_id]['stop_event'].set()
            self.timers[timer_id]['thread'].join()
            self.timers[timer_id]['thread'] = None

    def is_timer_running(self, timer_id):
        return timer_id in self.timers and self.timers[timer_id]['thread'] is not None
