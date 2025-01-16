from abc import ABC, abstractmethod
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener

class m3u8_strategy(ABC):
    @abstractmethod
    def parse_urls_in_m3u8(self):
        pass

class m3u8_strategy_chabeihu(m3u8_strategy):
    def parse_urls_in_m3u8(self):
        print('in chabeihu')

# a = m3u8_strategy_chabeihu()
# a.parse_urls_in_m3u8()

config = {
    'strategy': {
        'chabeihu': m3u8_strategy_chabeihu
    }
}
def parse(website):
    print(config['strategy'].get('chabeihu'))
    return config['strategy']['chabeihu']

a = parse('aaaaaa')().parse_urls_in_m3u8()

# class Test_A():
#     value = 123
#     def calc(self):
#         return self.value + 1000
    
# test_a = Test_A()
# print(test_a.calc())