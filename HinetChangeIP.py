import requests
from cloudflare_ddns import CloudFlare
from loguru import logger
import json




logger.add("HinetChangeIP.log",rotation="10MB", encoding="utf-8", enqueue=True, retention="5 days")


# 南投 彰化 台中



class Hinet(object):

    def __init__(self):
        with open("config.json", 'r') as file:
            configJson = json.loads(file.read())
        self.email=configJson["email"]
        self.api_key=configJson["api_key"]
        self.domain=configJson["domain"]
        self.changeHinetIpUrl=configJson["changeHinetIpUrl"]
        self.API=configJson["TGBotAPI"]
        self.sendTelegramUrl="https://api.telegram.org/bot"+self.API+"/sendMessage"
        self.chartId=configJson["chartId"]
        self.ddnsUrl=configJson["ddnsUrl"]
        self.name=configJson["name"]
        self.cf = CloudFlare(self.email, self.api_key, self.domain)


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

    def get_ip(self):
        try:
            res = self.cf.get_record('A', self.ddnsUrl)
            return res["content"]

        except Exception as err:
            logger.error(err)


    def sendTelegram(self,msg):
        params={
            "chat_id":self.chartId,
            "text": msg
        }
        resp=requests.get(url=self.sendTelegramUrl,params=params)
        logger.debug(resp.text)






    def cf_ddns(self,ip):
        res=self.cf.get_record('A', self.ddnsUrl)
        logger.debug("改变前 "+res["content"])
        self.cf.update_record(dns_type='A', name=self.ddnsUrl, content=ip,ttl=60)
        res = self.cf.get_record('A', self.ddnsUrl)
        logger.debug("改变后 "+res["content"])



if __name__ == '__main__':
    hinet=Hinet()
    hinet.change_ip()

