import requests
import re

url_start = "https://www.dictionaryapi.com/api/v3/references/collegiate/json/"
url_end = "?key=1d218d21-dc07-4abc-8198-1cb5fadb100d"


def get_word_data(word):
    url = url_start + word + url_end
    response = requests.get(url)
    try:
        data = response.json()[0]
        return data
    except IndexError:
        return None


def get_etym(word):
    data = get_word_data(word)
    try:
        etym_string = data['et'][0][1]
        pattern = '{it}(.*?){/it}'
        etym_list_commas = re.findall(pattern, etym_string)
        etym_list_split = []
        for string in etym_list_commas:
            etym_list_split = etym_list_split + string.split(', ')
        return etym_list_split

    except TypeError:
        return None



