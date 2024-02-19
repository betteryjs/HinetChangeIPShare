# ./nf -proxy socks5://hinet.660114.xyz:10241
import json
import subprocess
import requests
from cloudflare_ddns import CloudFlare
from loguru import logger

logger.remove(handler_id=None)  # 清除之前的设置
logger.add("HinetChangeIP.log",rotation="10MB", encoding="utf-8", enqueue=True, retention="5 days")

class HinetNFTest(object):


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
        self.cf = CloudFlare(self.email, self.api_key, self.domain)
        self.sock5Port=configJson["sock5Port"]
        self.name=configJson["name"]
        self.checkGFWUrl=configJson["checkGFWUrl"]


    def sendTelegram(self,msg):
        params={
            "chat_id":self.chartId,
            "text": msg
        }
        resp=requests.get(url=self.sendTelegramUrl,params=params)
        logger.debug(resp.text)

    def cf_ddns(self, ip):
        res = self.cf.get_record('A', self.ddnsUrl)
        logger.debug("改变前 " + res["content"])
        self.cf.update_record(dns_type='A', name=self.ddnsUrl, content=ip, ttl=60)
        res = self.cf.get_record('A', self.ddnsUrl)
        logger.debug("改变后 " + res["content"])

    def change_ip(self):
        try:
            response = requests.get(url=self.changeHinetIpUrl)
            logger.debug(response.text)
            if response.status_code == 200 and len(response.text.split(".")) == 4:
                res_ip = response.text.strip()
                self.cf_ddns(res_ip)
                self.sendTelegram("[{}]-[IP更换成功]-[当前IP {}]".format(self.name,res_ip))


        except Exception as err:
            logger.error(err)
            self.sendTelegram("[{}]-[IP更换失败]-[当前IP {}]".format(self.name,self.get_ip()))


    def check_nf(self):
        cmds="./nf -proxy socks5://"+self.get_ip()+":"+self.sock5Port
        p = subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        res=out.decode()
        ipv4res = res[0:res.find("[IPv6]")]
        ipv6res = res[res.find("[IPv6]"):]
        logger.debug(ipv4res)
        if "您的出口IP完整解锁Netflix"  in ipv4res:
            msg="[{}]-[奈非检测]-[您的出口IP完整解锁Netflix]".format(self.name)
            logger.debug(msg)
        else:
            msg="[{}]-[奈非检测]-[奈非检测失败]".format(self.name)
            self.sendTelegram(msg)
            logger.debug(msg)
            self.change_ip()
    def check_nf_tgbot(self):
        cmds="./nf -proxy socks5://"+self.get_ip()+":"+self.sock5Port
        p = subprocess.Popen(cmds, shell=True, stdout=subprocess.PIPE)
        out, err = p.communicate()
        res=out.decode()
        ipv4res = res[0:res.find("[IPv6]")]
        ipv6res = res[res.find("[IPv6]"):]
        logger.debug(ipv4res)
        if "您的出口IP完整解锁Netflix"  in ipv4res:
            msg="[{}]-[奈非检测]-[您的出口IP完整解锁Netflix]".format(self.name)
            logger.debug(msg)
            return msg
        else:
            msg="[{}]-[奈非检测]-[奈非检测失败]".format(self.name)
            logger.debug(msg)
            return msg


    def check_gfw_block(self):
        gfwUrl = self.checkGFWUrl + self.get_ip()
        resp = requests.get(url=gfwUrl).json()
        if resp["isblock"]==True:
            msg="[{}]-[GFW检测]-[IP ban 啦]".format(self.name)
            self.sendTelegram(msg)
            logger.debug(msg)
            self.change_ip()
        else:
            logger.debug("[{}]-[GFW检测]-[IP正常]".format(self.name))

    def check_gfw_block_tg(self):
        gfwUrl = self.checkGFWUrl + self.get_ip()
        resp = requests.get(url=gfwUrl).json()
        if resp["isblock"]==True:
            msg="[{}]-[GFW检测]-[IP ban 啦]".format(self.name)
            logger.debug(msg)
            return msg
        else:
            msg="[{}]-[GFW检测]-[IP正常]".format(self.name)
            logger.debug(msg)
            return msg








    def get_ip(self):
        try:
            res = self.cf.get_record('A', self.ddnsUrl)
            logger.debug("ip is {}".format(res["content"]))
            return res["content"]

        except Exception as err:
            logger.error(err)



if __name__ == '__main__':
    nftest=HinetNFTest()

    nftest.check_gfw_block()
    nftest.check_nf()

