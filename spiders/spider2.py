import requests
from json import loads


class Spider2():
    def __init__(self):
        self.base_url = 'http://proxylist.fatezero.org/proxy.list'
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'}

    def get_proxys(self):
        results = []
        try:
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                for line in response.text.split('\n'):
                    if line:
                        line = loads(line)
                        r = {'type':line['type'], 'host': line['host'], 'port':line['port'], 'address':line['country']}
                        if line['anonymity'] == 'high_anonymous':
                            r['anonymity'] = 'h'
                        elif line['anonymity'] == 'anonymous':
                            r['anonymity'] = 'a'
                        elif line['anonymity'] == 'transparent':
                            r['anonymity'] = 't'
                        else:
                            r['anonymity'] = ''
                        results.append(r)
        except:
            pass
        return results


if __name__ == '__main__':
    FZ = Spider2()
    proxys = FZ.get_proxys()
    print(proxys)