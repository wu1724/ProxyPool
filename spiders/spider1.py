import requests


class Spider1():
    def __init__(self):
        self.base_url = 'https://www.padaili.com/proxyapi?api=wF0MqtsPPiHJJh3xRm2zEH61RvqsbMA3&num=500&type=3' \
                        '&xiangying=1&order=jiance '
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0'}

    def get_proxys(self):
        results = []
        try:
            response = requests.get(self.base_url, headers=self.headers)
            if response.status_code == 200:
                data = response.text.split('<br/>')
                data.pop()
                # print(data)
                for line in data:
                    # print(line)
                    ip, port = line.split(':')
                    r = {'type': 'http', 'host': ip, 'port': port}
                    results.append(r)
        except:
            pass
        return results


if __name__ == '__main__':
    spider = Spider1()
    proxys = spider.get_proxys()
    print(proxys)
