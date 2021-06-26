# code:utf-8
import os
import sys
import time
from urllib import parse
import yaml
from eg_video_check_lastday.req import Req


homepath = os.getcwd()
testdatapath = os.path.join(homepath + r'/testdata.yaml')

if __name__ == '__main__':
    with open(testdatapath) as f:
        y = yaml.load(f, Loader=yaml.FullLoader)
    env = 'test_2'
    get_cfg_data = y[env]
    login_name = get_cfg_data['login_name']
    if (len(sys.argv) > 1 and sys.argv[1] is not None):
        env = sys.argv[1]
        get_cfg_data = y[env]
    if (len(sys.argv) > 2 and sys.argv[2] is not None):
        login_name = sys.argv[2]

    # 私钥签名
    siteCodeUserName = str(get_cfg_data['channel_id']) + login_name + get_cfg_data['ip']
    data_tobesignature = {
        "privateKey": get_cfg_data['private_key'],
        "siteCodeUserName": siteCodeUserName
    }
    r_sig = Req.post(url=get_cfg_data['host_api_gateway'] + '/auth/getSign', data=data_tobesignature)
    signature = r_sig.get('sign')

    # 获取H5LINK
    data_toh5link = {
        "signature": signature,
        "ip": get_cfg_data['ip'],
        "username": login_name,
        "channelId": get_cfg_data['channel_id']
    }
    header = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }
    r_h5link = Req.post(url=get_cfg_data['host'] + '/api/h5link', data=parse.urlencode(data_toh5link).encode('utf-8'),
                 header=header)
    get_cfg_data['h5link'] = r_h5link.get('h5Link')
    # 公钥加密
    timestamp=str(round(time.time()*1000))
    tobe_encrypt = {
        "username": login_name,
        "expire_time": "2022-01-01 11:11:11",
        "callback_url": "https://www.baidu.com",
        "timestamp":timestamp,
        "game":"main",
        "lang":"en_us"
    }
    data_getEgEncryptOrDecrypt = {
        "publicKey": get_cfg_data['public_key'],
        "siteCodeUserName": str(tobe_encrypt)
    }
    r_encrypt = Req.post(url=get_cfg_data['host_api_gateway'] + '/auth/getEgEncryptOrDecrypt', data=data_getEgEncryptOrDecrypt)
    # 编制地址
    params = r_encrypt.get('sign')
    data = {
        "params": params,
        "channel_id": get_cfg_data['channel_id']
    }
    # 获取redirect地址
    url = Req.get_url_format(url=get_cfg_data['h5link'] + '/redirect', params=data)
    print(url)
