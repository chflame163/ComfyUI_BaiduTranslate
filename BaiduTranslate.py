import http.client
import hashlib
import urllib.parse
import urllib.request
import random
import json
import requests
import os
import re

# 读取json
json_file = os.path.join(os.path.dirname(__file__), 'apikey.json')
with open(json_file, 'r') as f:
    api_dict = json.load(f)

# 判断字符串是否包含中文
def is_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

# 替换字符串中间一部分为'*'，reserve_digits是首尾保留位数
def string_asterisk_mask(str_, reserve_digits):
    if len(str_)==1:
        return '*'
    elif len(str_) <= reserve_digits * 2:
        return str_[:1] + re.sub(r'.','*', str_[1:])
    else:
        return (str_[:reserve_digits]
                + re.sub(r'.','*', str_[reserve_digits:-reserve_digits])
                + str_[-reserve_digits:])


# 通用翻译模块
class TextTranslate:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):

        API = [
            'Baidu developer API', 'Baidu v2Trans API', 'NiuTrans API',
        ]
        return {
            'required': {
                'text': ('STRING', {'multiline': True}),
                'Translate_to_language': (['en', 'zh'], {'default': 'en'}),
                "API": (API,),
            },
        }

    RETURN_TYPES = ('STRING',)
    FUNCTION = 'text_translation'
    CATEGORY = '😺dzNodes/BaiduTranslate'

    def text_translation(self, text, Translate_to_language, API):

        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        from_lang = 'auto'
        to_lang = Translate_to_language
        translate_result = ''
        debugmsg = ''

        if API == 'Baidu developer API':
            # get appid and appkey
            appid = api_dict['baidu_dev_appid']
            appkey = api_dict['baidu_dev_appkey']
            url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
            query = text

            print(f'# 😺dzNodes: TextTranslate: Baidu developer API, appid={string_asterisk_mask(appid, 3)}, '
                  f'appkey={string_asterisk_mask(appkey, 3)}, url={url}')

            # Generate salt and sign
            salt = random.randint(32768, 65536)
            s = appid + query + str(salt) + appkey
            sign = hashlib.md5(s.encode('utf-8')).hexdigest()

            # Build request
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

            result = [{'src': '', 'dst': 'error!'}]
            try:
                response = requests.post(url, params=payload, headers=headers).json()
                debugmsg = str(response)
                if "trans_result" in response:
                    result = response['trans_result']

            except Exception as e:
                print(e)

            for line in result:
                translate_result = translate_result + (line['dst']) + '\n'
            translate_result = translate_result[:-1]
            print('# 😺dzNodes: TextTranslate: Baidu developer API, ' + text + ' ---> ' + translate_result)
            if translate_result == 'error!':
                print(debugmsg)

        if API == 'Baidu v2Trans API':
            # 读取百度翻译的加盐算法
            import execjs
            js_file = os.path.join(os.path.join(os.path.dirname(__file__), 'js'), 'BaiduTranslate_sign.js')
            with open(js_file, 'r', encoding='utf-8') as f:
                sign_js = execjs.compile(f.read())

            token = '012cd082bf1f821bb7d94981bf6d477a'
            url = 'https://fanyi.baidu.com/v2transapi'
            print(f'# 😺dzNodes: TextTranslate: Baidu v2Trans API, token={string_asterisk_mask(token, 3)}, url={url}')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
                'cookie': 'BIDUPSID=3641572D5E0DB57A2F20F8F3373E302C; PSTM=1687090179; '
                          'BAIDUID=3641572D5E0DB57AF59F1D83EEBC5D2B:FG=1; BAIDUID_BFESS=3641572D5E0DB57AF59F1D83EEBC5D2B:FG=1; '
                          'ZFY=sGU1ho9nxRf2CX2bcYMVcfSXr9y2:BmKBeBdv7CDGhUs:C; '
                          'BDUSS'
                          '=tXaEJQVkxBeVBHMllBWWh1aTVZLXlhcVVqTWNCOXJGfmwzUUJmaHphWm1zZGRrSVFBQUFBJCQAAAAAAAAAAAEAAADWpvEyzqiwrsTjtcTQocPXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGYksGRmJLBkam; BDUSS_BFESS=tXaEJQVkxBeVBHMllBWWh1aTVZLXlhcVVqTWNCOXJGfmwzUUJmaHphWm1zZGRrSVFBQUFBJCQAAAAAAAAAAAEAAADWpvEyzqiwrsTjtcTQocPXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGYksGRmJLBkam; newlogin=1; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; BA_HECTOR=00aka5a12g80a10g25a52l0g1ie1gm11p; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=6; delPer=0; H_PS_PSSID=36550_39112_39226_39222_39097_39039_39198_39207_26350_39138_39225_39094_39137_39101; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1692451747; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1692451747; ab_sr=1.0.1_ZmQ3OWYzODRjZGNkOTYxOWI4ZTVhYjRmNTAwNjYyYTUwYmI3OGY2NTViMzhkNWYzM2IxZTVhNjAwNjdkMTU0ODE4Yzc2YmI3OGRmNTY3Y2QxMzZiZDRmZDIwMGIwYmQ2NGI5M2QzZWFlNmNkODBhZjllZDcxNGFkMTEyNmY0NGNhZGZjMTlmOGQ2YjIxNzNhMmUxNDJkMDhlZTM1NjhiZjkyMDc2MmQxN2Q5ODg3NDBkZGViNTEzMDU2NDQzNGEy'}

            sign = sign_js.call('e', text)
            data = {'from': from_lang,
                    'to': to_lang,
                    'query': text,
                    'transtype': 'realtime',
                    'simple_means_flag': 3,
                    'sign': sign,
                    'domain': 'common',
                    'token': token}

            result = [{'src': '', 'dst': 'error!'}]
            try:
                response = requests.post(url, headers=headers, data=data).json()
                debugmsg = str(response)
                if "trans_result" in response:
                    result = response['trans_result']['data']

            except Exception as e:
                print(e)

            for line in result:
                translate_result = translate_result + (line['dst']) + '\n'
            translate_result = translate_result[:-1]
            print('# 😺dzNodes: TextTranslate: Baidu_v2Trans API, ' + text + ' ---> ' + translate_result)
            if translate_result == 'error!' :
                print(debugmsg)

        if API == 'NiuTrans API':

            apikey = api_dict['niutrans_apikey']
            url = 'http://api.niutrans.com/NiuTransServer/translation?'
            data = {"from": from_lang, "to": to_lang, "apikey": apikey, "src_text": text}
            data_en = urllib.parse.urlencode(data)
            req = url + "&" + data_en
            res_dict = {}

            print(f'# 😺dzNodes: TextTranslate: NiuTrans API, apikey={string_asterisk_mask(apikey, 3)}, url={url[:-1]}')
            try:
                res = urllib.request.urlopen(req)
                res = res.read()
                res_dict = json.loads(res)
                debugmsg = str(res_dict)
            except Exception as e:
                print(e)

            if "tgt_text" in res_dict:
                translate_result = res_dict['tgt_text']
            else:
                translate_result = 'error!'

            print('# 😺dzNodes: TextTranslate: NiuTrans API, ' + text + ' ---> ' + translate_result)
            if translate_result == 'error!':
                print(debugmsg)


        return (translate_result,)


# 开发者API翻译模块
class BaiduTrans_devapi:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            'required': {
                'text': ('STRING', {'multiline': True}),
                'Translate_to_language': (['en', 'zh'], {'default': 'en'}),
            },
        }

    RETURN_TYPES = ('STRING',)
    FUNCTION = 'translation_devapi'
    CATEGORY = '😺dzNodes/BaiduTranslate'

    def translation_devapi(self, Translate_to_language, text):

        # get appid and appkey
        appid = api_dict['baidu_dev_appid']
        appkey = api_dict['baidu_dev_appkey']
        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        from_lang = 'auto'
        to_lang = Translate_to_language

        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path
        query = text
        translate_result = ''
        print(f'# 😺dzNodes: BaiduTrans_devapi: appid={string_asterisk_mask(appid, 3)}, '
              f'appkey={string_asterisk_mask(appkey, 3)}, url={url}')

        # Generate salt and sign
        salt = random.randint(32768, 65536)
        s = appid + query + str(salt) + appkey
        sign = hashlib.md5(s.encode('utf-8')).hexdigest()

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        result = [{'src': 'API error！', 'dst': '百度翻译API错误!，请检查是否填写正确的API Key并且有足够的API流量?'}]
        # Send request
        try:
            r = requests.post(url, params=payload, headers=headers)
            result = r.json()['trans_result']

        except Exception as e:
            print(e)

        for line in result:
            translate_result = translate_result + (line['dst']) + '\n'
        translate_result = translate_result[:-1]
        print('# 😺dzNodes: BaiduTrans_Api:' + text + ' ---> ' + translate_result)
        return (translate_result,)

class BaiduTrans_v2trans:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            'required': {
                'text': ('STRING', {'multiline': True}),
                'Translate_to_language': (['en', 'zh'], {'default': 'en'}),
            },
        }

    RETURN_TYPES = ('STRING',)
    FUNCTION = 'translation_v2trans'
    CATEGORY = '😺dzNodes/BaiduTranslate'
    OUTPUT_NODE = True

    def translation_v2trans(self, Translate_to_language, text):

        # 读取百度翻译的加盐算法
        import execjs
        js_file = os.path.join(os.path.join(os.path.dirname(__file__), 'js'), 'BaiduTranslate_sign.js')
        with open(js_file, 'r', encoding='utf-8') as f:
            sign_js = execjs.compile(f.read())

        from_lang = 'auto'
        to_lang = Translate_to_language

        token = '012cd082bf1f821bb7d94981bf6d477a'
        url = 'https://fanyi.baidu.com/v2transapi'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'cookie': 'BIDUPSID=3641572D5E0DB57A2F20F8F3373E302C; PSTM=1687090179; '
                      'BAIDUID=3641572D5E0DB57AF59F1D83EEBC5D2B:FG=1; BAIDUID_BFESS=3641572D5E0DB57AF59F1D83EEBC5D2B:FG=1; '
                      'ZFY=sGU1ho9nxRf2CX2bcYMVcfSXr9y2:BmKBeBdv7CDGhUs:C; '
                      'BDUSS'
                      '=tXaEJQVkxBeVBHMllBWWh1aTVZLXlhcVVqTWNCOXJGfmwzUUJmaHphWm1zZGRrSVFBQUFBJCQAAAAAAAAAAAEAAADWpvEyzqiwrsTjtcTQocPXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGYksGRmJLBkam; BDUSS_BFESS=tXaEJQVkxBeVBHMllBWWh1aTVZLXlhcVVqTWNCOXJGfmwzUUJmaHphWm1zZGRrSVFBQUFBJCQAAAAAAAAAAAEAAADWpvEyzqiwrsTjtcTQocPXAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGYksGRmJLBkam; newlogin=1; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; BA_HECTOR=00aka5a12g80a10g25a52l0g1ie1gm11p; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; PSINO=6; delPer=0; H_PS_PSSID=36550_39112_39226_39222_39097_39039_39198_39207_26350_39138_39225_39094_39137_39101; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1692451747; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1692451747; ab_sr=1.0.1_ZmQ3OWYzODRjZGNkOTYxOWI4ZTVhYjRmNTAwNjYyYTUwYmI3OGY2NTViMzhkNWYzM2IxZTVhNjAwNjdkMTU0ODE4Yzc2YmI3OGRmNTY3Y2QxMzZiZDRmZDIwMGIwYmQ2NGI5M2QzZWFlNmNkODBhZjllZDcxNGFkMTEyNmY0NGNhZGZjMTlmOGQ2YjIxNzNhMmUxNDJkMDhlZTM1NjhiZjkyMDc2MmQxN2Q5ODg3NDBkZGViNTEzMDU2NDQzNGEy'}

        sign = sign_js.call('e', text)
        data = {'from': from_lang,
                'to': to_lang,
                'query': text,
                'transtype': 'realtime',
                'simple_means_flag': 3,
                'sign': sign,
                'domain': 'common',
                'token': token}

        result = [{'src': 'error！', 'dst': '百度翻译v2transapi爬取错误!'}]
        try:
            baidutranslate = requests.post(url, headers=headers, data=data).json()
            # t = baidutranslate['trans_result']['data'][0]['dst']
            result = baidutranslate['trans_result']['data']

        except Exception as e:
            print(e)

        translate_result = ''
        for line in result:
            translate_result = translate_result + (line['dst']) + '\n'
        translate_result = translate_result[:-1]
        # 如果目标语言是英语 且 翻译结果包含中文 且 原始文本不包含中文，返回原文
        if Translate_to_language == 'en' and is_contain_chinese(translate_result) and not is_contain_chinese(text):
            translate_result = text
        # 如果目标语言是中文 且 翻译结果不包含中文 且 原始文本包含中文，返回原文
        if Translate_to_language == 'zh' and not is_contain_chinese(translate_result) and is_contain_chinese(text):
            translate_result = text

        print('# 😺dzNodes: BaiduTrans_v2trans:' + text + ' ---> ' + translate_result)
        return (translate_result,)

# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    'TextTranslate': TextTranslate,
    'BaiduTrans_DevApi': BaiduTrans_devapi,
    'BaiduTrans_v2Trans': BaiduTrans_v2trans,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    'TextTranslate': 'Text Translate',
    'BaiduTrans_DevApi': 'BaiduTrans(DevApi)',
    'BaiduTrans_v2Trans': 'BaiduTrans(v2Trans)',
}
