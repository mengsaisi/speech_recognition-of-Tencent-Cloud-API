# 以下是腾讯语音识别API
# -*- coding:utf-8 -*-
import json

# python3导入
from urllib import request

import hmac
import hashlib
import base64
import time
import random
import os

class SpeechRecognition:

    def __init__(self,secret_key, secretid, appid, filepath):
        self.secret_key = secret_key
        self.secretid = secretid
        self.appid = appid
        self.engine_model_type = '16k_0'
        self.res_type = 0
        self.result_text_format = 0
        self.voice_format = 1
        self.cutlength = 20000
        self.template_name = ""
        self.filepath = filepath
        """
        说明：
        secret_key、secretid、appid在进行腾讯云注册时获得
        engine_model_type：引擎模型类型。
                           8k_0：电话 8k 中文普通话通用，可用于双声道音频的识别；
                           8k_6：电话 8k 中文普通话话者分离，仅用于单声道；
                           16k_0：16k 中文普通话通用。
        res_type: 结果返回方式。 1：同步返回；0：尾包返回
        result_text_format:识别结果文本编码方式。0：UTF-8；1：GB2312；2：GBK；3：BIG5
        voice_format: 语音数据来源。0：语音 URL；1：语音数据（post body）
        
            """

    def sign(self,signstr):
        # python3做二进制转换
        bytes_signstr = bytes(signstr, 'utf-8')
        bytes_secret_key = bytes(self.secret_key, 'utf-8')
        # bytes_secret_key = bytes(secret_key, 'latin-1')

        hmacstr = hmac.new(bytes_secret_key, bytes_signstr, hashlib.sha1).digest()
        s = base64.b64encode(hmacstr)
        return s

    def formatSignString(self,param):
        #api调用时生成签名，签名将用来进行接口授权
        signstr = "POSTaai.qcloud.com/asr/v1/"
        for t in param:
            if 'appid' in t:
                signstr += str(t[1])
                break
        signstr += "?"
        for x in param:
            tmp = x
            if 'appid' in x:
                continue
            for t in tmp:
                signstr += str(t)
                signstr += "="
            signstr = signstr[:-1]
            signstr += "&"
        signstr = signstr[:-1]
        return signstr

    def randstr(self,n):
        #生成随机字符串
        seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        sa = []
        for i in range(n):
            sa.append(random.choice(seed))
        salt = ''.join(sa)
        return salt

    def sendVoice(self):
        if len(str(self.secret_key)) == 0:
            print('secretKey can not empty')
            return
        if len(str(self.secretid)) == 0:
            print('secretid can not empty')
            return
        if len(str(self.appid)) == 0:
            print('appid can not empty')
            return
        if len(str(self.engine_model_type)) == 0 or (
                str(self.engine_model_type) != '8k_0' and str(self.engine_model_type) != '16k_0' and str(
            self.engine_model_type) != '16k_en'):
            print('engine_model_type is not right')
            return
        if len(str(self.res_type)) == 0 or (str(self.res_type) != '0' and str(self.res_type) != '1'):
            print('res_type is not right')
            return
        if len(str(self.result_text_format)) == 0 or (
                str(self.result_text_format) != '0' and str(self.result_text_format) != '1' and str(
                self.result_text_format) != '2' and str(self.result_text_format) != '3'):
            print('result_text_format is not right')
            return
        if len(str(self.voice_format)) == 0 or (
                str(self.voice_format) != '1' and str(self.voice_format) != '4' and str(self.voice_format) != '6'):
            print('voice_format is not right')
            return
        if len(str(self.filepath)) == 0:
            print('filepath can not empty')
            return
        if len(str(self.cutlength)) == 0 or str(self.cutlength).isdigit() == False or self.cutlength > 200000:
            print('cutlength can not empty')
            return

        query_arr = dict()
        query_arr['appid'] = self.appid
        query_arr['projectid'] = 1013976
        if len(self.template_name) > 0:
            query_arr['template_name'] = self.template_name
        query_arr['sub_service_type'] = 1
        query_arr['engine_model_type'] = self.engine_model_type
        query_arr['res_type'] = self.res_type
        query_arr['result_text_format'] = self.result_text_format
        query_arr['voice_id'] = self.randstr(16)
        query_arr['timeout'] = 100
        query_arr['source'] = 0
        query_arr['secretid'] = self.secretid
        query_arr['timestamp'] = str(int(time.time()))
        query_arr['expired'] = int(time.time()) + 24 * 60 * 60
        query_arr['nonce'] = query_arr['timestamp'][0:4]
        query_arr['voice_format'] = self.voice_format
        file_object = open(self.filepath, 'rb')
        file_object.seek(0, os.SEEK_END)
        datalen = file_object.tell()
        file_object.seek(0, os.SEEK_SET)
        seq = 0
        while (datalen > 0):
            end = 0
            if (datalen < self.cutlength):
                end = 1
            query_arr['end'] = end
            query_arr['seq'] = seq
            query = sorted(query_arr.items(), key=lambda d: d[0])
            signstr = self.formatSignString(query)
            autho = self.sign(signstr)

            if (datalen < self.cutlength):
                content = file_object.read(datalen)
            else:
                content = file_object.read(self.cutlength)
            seq = seq + 1
            datalen = datalen - self.cutlength
            headers = {}
            headers['Authorization'] = autho
            headers['Content-Length'] = len(content)
            requrl = "http://"
            requrl += signstr[4::]

            # python3
            req = request.Request(requrl, data=content, headers=headers)

            res_data = request.urlopen(req)
            # time.sleep(0.3)
            res = res_data.read().decode('utf-8')
            print(res)

        file_object.close()

        return res

    def get_result(self):
        res = self.sendVoice()
        res_dict = json.loads(res)
        return res_dict['text']

if __name__ == '__main__':
    # secret_key, secretid, appid换成自己申请的
    secret_key = 'xxxxx'
    secretid = 'xxxx'
    appid = 'xxxx'

    #要识别的语音
    file_path = 'test.wav'

    init_value = SpeechRecognition(secret_key, secretid, appid, file_path)
    recognition_result = init_value.get_result()
    print('识别结果为:',recognition_result)