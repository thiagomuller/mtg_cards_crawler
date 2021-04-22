import scrapy
from scrapy.http import FormRequest
from scrapy import Request
import json
from scrapy.http import HtmlResponse
import logging
import ast
from os import getenv

class CardInfoSpider(scrapy.Spider):
    name = 'card_info_spider'


    def __init__(self, card_names):
        super(CardInfoSpider, self).__init__()
        self.start_urls = [getenv('crawler_url_prefix')+card_name for card_name in ast.literal_eval(card_names)]


    def parse(self, response):
        breakpoint()
        try:
            for i,r in enumerate(response.xpath("//div[@id='aba-cards']/child::div[contains(@id, 'line_')]")):
                if r.css('.edicaoextras .ed').get():
                    edition = r.css('.edicaoextras .ed .ed-simb::text').get()
                    foil = r.css(".edicaoextras .extras::text").get() == 'Foil'
                else:
                    edition = response.css(".nomeedicao .ed-simb::text").get()
                    foil = False
                yield FormRequest.from_response(
                    response,
                    method='POST',
                    url = 'https://www.ligamagic.com.br/ajax/mp/carrinho.php',
                    dont_filter=True,
                    headers={
                        'authority':'ligamagic.com.br',
                        'sec-ch-ua':'Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99',
                        'accept':'*/*',
                        'x-requested-with':'XMLHttpRequest',
                        'sec-ch-ua-mobile':'?0',
                        'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                        'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
                        'origin':'https://ligamagic.com.br',
                        'sec-fetch-site':'same-origin',
                        'sec-fetch-mode':'cors',
                        'sec-fetch-dest':'empty',
                        'referer':self.start_urls[0],
                        'accept-language':'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
                    },
                    formdata={
                        'opc':'put',
                        'tipo':'1',
                        'id':r.xpath("./@id").get().strip('line_e'),
                        'qty':'1'
                    },
                    meta={
                        'cookiejar':i,
                        'store_name':r.xpath("./child::div[contains(@class,'e-col1')]/img/@title").get(),
                        'edition':edition,
                        'foil':foil,
                        'language':r.xpath("./child::div[contains(@class,'e-col4')]/img/@title").get(),
                        'card_usage':r.xpath("./child::div[contains(@class,'e-col4')]/font/text()").get(),
                        'store_id':r.xpath("./child::div[contains(@class,'e-col1')]/child::img/@onclick").get().strip('mpuser.getStore();'),
                    },
                    callback=self.get_cart
                )
        except:
            logging.error('COULD NOT SCRAPE DATA FOR URl: ' + response.request.url) 

    def get_cart(self, response):
        print('RESPONSE FOR ADDING ON CART:  ' + response.text)
        yield Request(
            url='https://www.ligamagic.com.br/?view=mp/carrinho',
            dont_filter=True,
            headers={
                'authority':'ligamagic.com.br',
                'sec-ch-ua':'"GoogleChrome";v="89","Chromium";v="89",";NotABrand";v="99"',
                'accept':'*/*',
                'x-requested-with':'XMLHttpRequest',
                'sec-ch-ua-mobile':'?0',
                'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                'content-type':'application/x-www-form-urlencoded;charset=UTF-8',
                'origin':'https://ligamagic.com.br',
                'sec-fetch-site':'same-origin',
                'sec-fetch-mode':'cors',
                'sec-fetch-dest':'empty',
                'referer':self.start_urls[0],
                'accept-language':'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            },
            meta={
                'cookiejar':response.meta['cookiejar'],
                'store_name':response.meta['store_name'],
                'edition':response.meta['edition'],
                'foil':response.meta['foil'],
                'language':response.meta['language'],
                'card_usage':response.meta['card_usage'],
                'store_id':response.meta['store_id']
            },
            callback=self.parse_cart
        )

    def parse_cart(self, response):
        price = ''
        if response.css('.item-subpreco-desconto::text'):
            price = response.xpath("//div[contains(@class,'item-subpreco-desconto')]").get().split('<br>')[1].strip('</div>')
        else:
            price = response.css('.item-subpreco::text').get()
        previous_information={
            'store_name':response.meta['store_name'],
            'edition':response.meta['edition'],
            'foil':response.meta['foil'],
            'language':response.meta['language'],
            'card_usage':response.meta['card_usage'],
            'units':response.css('.item-estoque::text').get().split(' ')[0],
            'price':price,
            'store_id':response.meta['store_id']
        }
        request = FormRequest.from_response(
            response,
            method='POST',
            url='https://ligamagic.com.br/ajax/mp/actions.php',
            dont_filter=True,
            headers={
                'authority':'ligamagic.com.br',
                'sec-ch-ua':'"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                'accept':'*/*',
                'accept-encoding':'gzip, deflate, br',
                'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with':'XMLHttpRequest',
                'sec-ch-ua-mobile':'?0',
                'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                'content-type':'application/x-www-form-urlencoded; charset=UTF-8',
                'origin':'https://ligamagic.com.br',
                'sec-fetch-site':'same-origin',
                'sec-fetch-mode':'cors',
                'sec-fetch-dest':'empty',
                'referer':'https://ligamagic.com.br/?view=mp/carrinho',
                'accept-language':'pt-BR,pt;q=0.9'
            },
            meta={'cookiejar':response.meta['cookiejar']},
            formdata={
                    'opc':'getStoreData',
                    'tipo':'1',
                    'id':response.meta['store_id'],
                    'origin':'desktop',
                    'tcg':'1'
            },
            cookies={},
            cb_kwargs={},
            callback=self.parse_store_rating
        )
        request.cb_kwargs['previous_information']=previous_information
        yield request

    def parse_store_rating(self, response, previous_information):
        js = json.loads(response.text)
        response = HtmlResponse(url='https://www.ligamagic.com.br/ajax/mp/actions.php', body=response.text, encoding='utf-8')
        yield {
            'store_name':previous_information['store_name'],
            'edition':previous_information['edition'],
            'foil':previous_information['foil'],
            'language':previous_information['language'],
            'card_usage':previous_information['card_usage'],
            'units':previous_information['units'],
            'price':previous_information['price'],
            'general_average':response.xpath("//div[@class='aval-media-star']//span[@class='stars']/@title").get().split(':')[1].strip(),
            'shipping_efficiency':response.xpath("(//div[@class='aval-medias-stars']//div[@class='aval-specifics'])[1]//span/@title").get().split(':')[1].strip(),
            'packing_and_protection':response.xpath("(//div[@class='aval-medias-stars']//div[@class='aval-specifics'])[2]//span/@title").get().split(':')[1].strip(),
            'sent_itens_accuracy':response.xpath("(//div[@class='aval-medias-stars']//div[@class='aval-specifics'])[3]//span/@title").get().split(':')[1].strip()
        }
