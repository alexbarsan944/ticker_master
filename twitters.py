import string

import nltk
import requests
from nltk.data import load
from nltk.tokenize.destructive import NLTKWordTokenizer

nltk.download('punkt')


def sent_tokenize(text, language="english"):
    tokenizer = load(f"tokenizers/punkt/{language}.pickle")
    return tokenizer.tokenize(text)


_treebank_word_tokenizer = NLTKWordTokenizer()


def word_tokenize(text, language="english", preserve_line=False):
    text = text.lower()
    sentences = [text] if preserve_line else sent_tokenize(text, language)
    lst = [
        token for sent in sentences for token in _treebank_word_tokenizer.tokenize(sent)
    ]
    unwanted = {'network', 'hiring', 'the', 'foundation', 'to', 'protocol', 'for', 'now', 'finance', 'of', 'is', 'smart', 'contract', 'official'}

    lst = [ele for ele in lst if ele not in string.punctuation and ele not in unwanted]

    return set(lst)


def create_map():
    URL = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=2000&sortBy=market_cap' \
          '&sortType=desc&convert=USD&cryptoType=all&tagType=all&audited=false '
    r = requests.get(url=URL)
    data = r.json()
    mapper = {}
    for d in data['data']['cryptoCurrencyList']:
        mapper[d['symbol'].lower()] = [d['name'].lower()]
    with open('twitters.txt') as f:
        lst = (list(eval(f.read())))

    for twitter in lst:
        for coin in twitter['coins']:
            try:
                for i in word_tokenize(twitter['name']):
                    mapper[coin].add(i)
                for i in word_tokenize(twitter['screen_name']):
                    mapper[coin].add(i)
                # print(mapper[coin])
            except:
                mapper[coin] = set(coin)
                mapper[coin].update(word_tokenize(twitter['name']))
                mapper[coin].update(word_tokenize(twitter['screen_name']))

    return mapper


mapper = create_map()

def extract(text):
    def get_keys(val):
        lst = set()
        for ticker in mapper.keys():
            if val in mapper[ticker]:
                lst.add(ticker)
        if len(lst) > 0:
            return lst
        return val

    text = text.lower()
    coins = set()
    lst = word_tokenize(text)
    for idx, word in enumerate(lst):
        if len(word) >= 2:
            if word in mapper.keys():
                coins.add(word)
                # print(word, 'here')
            else:
                for reference_list in mapper.values():
                    if word in reference_list:
                        coins.update(get_keys(word))
                        pass
        if len(coins):
            return set(coins)
        return []


