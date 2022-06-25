from datetime import datetime

import requests


class Spider3():
    def __init__(self):
        self.base_url = 'https://ip.jiangxianli.com/api/proxy_ips'
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'}

    def get_proxys(self):
        html = []
        results = []
        url = datetime.strftime(datetime.now(), "https://ip.ihuan.me/today/%Y/%m/%d/%H.html")
        try:
            resp = requests.get(url, headers=self.headers, timeout=15)
            html = resp.text.split('<p class="text-left">')[1].split('<br></p></div></div></div>')[0].split('<br>')
        except:
            return results
        del html[0]
        for li in html:
            r = {}
            ip = li.split('@')[0]
            other = li.split('@')[1]
            anonymity = other.split('[')[1].split(']')[0]
            if other.find('HTTPS') != -1:
                r['type'] = 'https'
            else:
                r['type'] = 'http'
            try:
                r['host'] = ip.split(':')[0]
                r['port'] = ip.split(':')[1]
            except IndexError:
                continue
            if anonymity == '高匿':
                r['anonymity'] = 'h'
            elif anonymity == '普匿':
                r['anonymity'] = 'a'
            else:
                r['anonymity'] = 't'
            r['address'] = other.split(']')[1].split(' ')[0]
            results.append(r)
        return results


if __name__ == '__main__':
    proxylists = Spider3()
    proxys = proxylists.get_proxys()
    print(proxys)
