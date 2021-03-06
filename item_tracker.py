import time
import winsound

import pyperclip
import requests

from items import my_items
from settings import EXALTED_TO_CHAOS, LEAGUE, RETRY_MINUTES, SLEEP_MINUTES

print('Start searching...')
league = LEAGUE
trade_url = f"https://www.pathofexile.com/api/trade/search/{league}"
item_api_url = 'https://www.pathofexile.com/api/trade/fetch/{}?query={}'
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'PostmanRuntime/7.26.10',
}
found = False


def print_breakline():
    print('------------------------------------------------------------------------------')


def get_chaos_price(amount, currency):
    if currency == 'exalted':
        return amount * EXALTED_TO_CHAOS
    return amount


def search_item(item):
    trade = requests.post(trade_url, item['body'], headers=headers)
    trade = trade.json()
    if 'error' in trade:
        time.sleep(SLEEP_MINUTES * 60)
        return False
    if not trade['result'] or item['state'] is False:
        print(item['name'], ': not found', item['url'])
        return False
    item_hash = trade['result'][0]
    item_result = requests.get(item_api_url.format(item_hash, trade['id']), headers=headers)
    item_result = item_result.json()
    if 'result' not in item_result:
        time.sleep(SLEEP_MINUTES * 60)
        return False
    name = item_result['result'][0]['item']['name']
    type_line = item_result['result'][0]['item']['typeLine']
    whisper = item_result['result'][0]['listing']['whisper']
    price = item_result['result'][0]['listing']['price']
    if price:
        print(f"{name or type_line} - {price['amount']} {price['currency']} -", item['url'])
        list_price = get_chaos_price(price['amount'], price['currency'])
        my_price = get_chaos_price(item['price']['amount'], item['price']['currency'])
        if my_price >= list_price:
            winsound.Beep(frequency=500, duration=500)
            print(
                f"\t({price['amount']} {price['currency']} <= {item['price']['amount']} {item['price']['currency']})", )
            print('\t', whisper)
            pyperclip.copy(whisper)
            return True


while True:
    print_breakline()
    for my_item in my_items:
        found = search_item(my_item)
    time.sleep(60 * RETRY_MINUTES)
