#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
import re
from multiprocessing import Pool as ThreadPool
from email.mime.text import MIMEText
import smtplib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# 修改自己的cookies
cookie = ''

# 构建请求头数据
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': cookie,
    'DNT': '1',
    'Host': 'tieba.baidu.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36'
}

urls = []
suc_titles = []
error_titles = []


# 获取关注贴吧列表
def find_kw():
    page_count = 1
    kw_list = []
    while 1:
        like_url = 'http://tieba.baidu.com/f/like/mylike?&pn=%d' % page_count
        like_html = requests.get(url=like_url, headers=headers).text
        re_kw = re.compile(ur'<a href="/f\?kw=(.+?)" title="(.+?)"')
        temp_kw = re_kw.findall(like_html)
        if not temp_kw:
            break
        if not kw_list:
            kw_list = temp_kw
        else:
            kw_list += temp_kw
        page_count += 1

    if kw_list:
        for kw in kw_list:
            urls.append('http://tieba.baidu.com/mo/m?kw=' + kw[0] + '\\' + kw[0] + '\\' + kw[1])

    print u'我喜欢的%d个贴吧:' % len(kw_list)


# 签到
def sign(url):
    # sign_url = 'http://tieba.baidu.com/mo/m?kw=' + kw
    sign_url = url.split('\\')[0]
    kw = url.split('\\')[1]
    title = url.split('\\')[2]

    sign_html = requests.get(url=sign_url, headers=headers).text

    try:
        is_sign = re.findall(u'已签到', sign_html)

        if is_sign:
            suc_titles.append(title)
            print title + u' ok'
            return True
        else:
            print title + u' signing...'

            re_fid = re.compile(r'<input type="hidden" name="fid" value="(.+?)"\/>')
            fid = re.findall(re_fid, sign_html)
            if len(fid) == 0:
                fid = re.findall(r'fid=(.*?)&', sign_html, re.S)[0]
            else:
                fid = fid[0]

            re_tbs = re.compile(r'<input type="hidden" name="tbs" value="(.+?)"\/>')
            tbs = re.findall(re_tbs, sign_html)
            if len(tbs) == 0:
                tbs = re.findall(r'tbs=(.*?)&', sign_html, re.S)[0]
            else:
                tbs = tbs[0]

            data = {
                'tbs': tbs,
                'fid': fid,
                'kw': kw
            }

            sign_url = 'http://tieba.baidu.com/mo/q---C367D41E4214449AC861EDF6CE73CD4E%3AFG%3D1--1-3-0--2--wapp_1443524105422_889/sign?tbs=' + tbs + '&fid=' + fid + '+&kw=' + kw

            requests.get(url=sign_url, headers=headers, data=data)

            suc_titles.append(title)
            print title + u' ok'

            return True

    except Exception as e:
        print title + u' error'
        error_titles.append(title)
        return False

mail_to_list = list()
mail_host = 'smtp.qq.com'   # 设置服务器
mail_user = '770362426'     # 用户名
mail_pass = 'yrh0306'       # 密码
mail_postfix = 'qq.com'     # 发件箱后缀


def send_mail(to_list, sub, content):
    me = '<' + mail_user + "@" + mail_postfix + '>'
    msg = MIMEText(content, _subtype='plain', _charset='utf8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print e
        return False

if __name__ == '__main__':

    find_kw()
    # 设置进程数
    # pool = ThreadPool(8)
    # pool.map(sign, urls)
    # pool.close()
    # pool.join()
    for url in urls:
        sign(url)

    print u'\n\n---------------签到完成---------------'

    print u'成功数：' + str(len(suc_titles))
    print u'失败数' + str(len(error_titles))

    print u'--------------------------------------'

    if len(error_titles) > 0:
        print u'失败列表：'
    for i in error_titles:
        print '\t' + i
    if len(suc_titles) > 0:
        print u'成功列表：'
    for i in suc_titles:
        print '\t' + i

    mail_to_list.append('yangruihan@vip.qq.com')
    content = '-----签到结果-----\n' + '\t成功数：' + str(len(suc_titles)) + '\n\t失败数：' + str(len(error_titles)) \
              + '\n------------------\n\n' + '---失败列表---\n' + '\n'.join(error_titles) + '\n---成功列表---\n' + '\n'.join(suc_titles)
    if send_mail(mail_to_list, '百度贴吧签到', content):
        print u'\n邮件发送成功'
    else:
        print u'\n邮件发送失败'


