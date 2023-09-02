import json
import os.path
from getpass import getpass

import requests

file_save_name = 'creds.txt'
# 账号信息
cred = ''

app_code = '4ca99fa6b56cc2ba'

header = {
    'cred': cred,
    'User-Agent': 'Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close'
}
header_login = {
    'User-Agent': 'Skland/1.0.1 (com.hypergryph.skland; build:100001014; Android 31; ) Okhttp/4.11.0',
    'Accept-Encoding': 'gzip',
    'Connection': 'close'
}

# 签到url
sign_url = "https://zonai.skland.com/api/v1/game/attendance"
# 绑定的角色url
binding_url = "https://zonai.skland.com/api/v1/game/player/binding"

# 使用token获得认证代码
grant_code_url = "https://as.hypergryph.com/user/oauth2/v2/grant"

# 使用认证代码获得cred
cred_code_url = "https://zonai.skland.com/api/v1/user/auth/generate_cred_by_code"

def login_by_token():
    token_code = "AAVM36nfLHmKG0fzSNgP/g6w"
    try:
        t = json.loads(token_code)
        token_code = t['data']['content']
    finally:
        pass
    grant_code = get_grant_code(token_code)
    return get_cred(grant_code)


def get_grant_code(token):
    resp = requests.post(grant_code_url, json={
        'appCode': app_code,
        'token': token,
        'type': 0
    }, headers=header_login).json()
    if resp['status'] != 0:
        raise Exception(f'获得认证代码失败：{resp["msg"]}')
    return resp['data']['code']


def get_cred(grant):
    resp = requests.post(cred_code_url, json={
        'code': grant,
        'kind': 1
    }, headers=header_login).json()
    if resp['code'] != 0:
        raise Exception(f'获得cred失败：{resp["messgae"]}')
    return resp['data']['cred']


def get_binding_list():
    v = []
    resp = requests.get(url=binding_url, headers=header).json()
    if resp['code'] != 0:
        print(f"请求角色列表出现问题：{resp['message']}")
        if resp.get('message') == '用户未登录':
            print(f'用户登录可能失效了，请重新运行此程序！')
            os.remove(file_save_name)
            return []
    for i in resp['data']['list']:
        if i.get('appCode') != 'arknights':
            continue
        v.extend(i.get('bindingList'))
    return v


def do_sign():
    header['cred'] = cred
    characters = get_binding_list()
    for i in characters:
        body = {
            'uid': i.get('uid'),
            'gameId': i.get("channelMasterId")
        }
        resp = requests.post(sign_url, headers=header, json=body).json()
        if resp['code'] != 0:
            print(f'角色{i.get("nickName")}({i.get("channelName")})签到失败了！原因：{resp.get("message")}')
            continue
        print(
            f'角色{i.get("nickName")}({i.get("channelName")})签到成功，获得了{resp.get("resource").get("name")}×{resp.get("count")}'
        )

def do_init():
    print("使用鹰角网络通行证账号登录")
    login_by_token()

try:
    do_init()
    do_sign()
    print("签到完成！")
except Exception as ex:
    print(f'签到失败，原因：{str(ex)}')
input()
