from os import getenv, path, system
import sys


def parse_cards_file():
    with open(path.join(sys.path[0],'../../cards.txt'), 'r') as cards_file:
        return strip_cards([card for card in cards_file])

def format_card_list(cards):
    for card in cards:
        if '//' in card:
            card.strip()
            card = card.split('//')[0] + '+' + card.split('//')[1]
        card = card.split(' ')[0] + '+' + card.split(' ')[1]

def strip_cards(cards):
    return remove_empties([card.strip() for card in cards])

def remove_empties(cards):
    return handle_double_names([card for card in cards if card])

def initialize_crawl():
    cards = parse_cards_file()
    print('scrapy crawl {0} -a card_names="{1}" -o {2}'.format(getenv('spider_name'), str(cards), getenv('info_file_name')))
    #system('scrapy crawl {0} -a card_names="{1}" -o {2}'.format(getenv('spider_name'), str(cards), getenv('info_file_name')))

if __name__ == '__main__':
    initialize_crawl()