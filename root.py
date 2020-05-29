from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import time

print_check = False

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url,str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def easy_root(word):
    root = word
    at_least_four = len(root) > 3

    last = word[-1]
    last_two = word[-2:]
    last_three = word[-3:]
    if at_least_four:
        last_four = word[-4:]

    one_letter_suffixes = ['I','S','Y']
    two_letter_suffixes = ['ED','ER','LY']
    three_letter_suffixes = ['ING','EST','IST']
    four_letter_suffixes = ['ABLE','TION','SION']

    if at_least_four and (last_four in four_letter_suffixes):
        root = root[:-4]
    elif last_three in three_letter_suffixes:
        root = root[:-3]
    elif last_two in two_letter_suffixes:
        root = root[:-2]
    elif last in one_letter_suffixes:
        root = root[:-1]

    at_least_one = len(root) > 0
    at_least_two = len(root) > 1
    at_least_three = len(root) > 2
    at_least_four = len(root) > 3

    if at_least_one:
        first = root[:1]
    if at_least_two:
        first_two = root[:2]
    if at_least_three:
        first_three = root[:3]
    if at_least_four:
        first_four = root[:4]

    one_letter_prefixes = ['A','E']
    two_letter_prefixes = ['UN','RE','DE','IN']
    three_letter_prefixes = ['OUT']
    four_letter_prefixes = ['ANTI','OVER']

    if at_least_four and (first_four in four_letter_prefixes):
        root = root[4:]
    elif at_least_three and (first_three in three_letter_prefixes):
        root = root[3:]
    elif at_least_two and (first_two in two_letter_prefixes):
        root = root[2:]
    elif at_least_one and (first in one_letter_prefixes):
        root = root[1:]

    return root

def oed_strip(word):
    start_oed_strip = time.time()
    url_merriam = 'https://www.merriam-webster.com/dictionary/' + str(word or '')
    raw_html = simple_get(url_merriam)
    html.find('title').text.split(' ')[0]

def merriam_strip(word):
    start_merriam_strip = time.time()
    url_merriam = 'https://www.merriam-webster.com/dictionary/' + str(word or '')
    raw_html = simple_get(url_merriam)
    try:
        stripped_html = raw_html.decode()[0:30000]
    except AttributeError:
        return word

    html = BeautifulSoup(stripped_html, 'html.parser')
    root = html.find('h1', attrs={'class': "hword"}).text

    end_merriam_strip = time.time()
    if print_check:
        print(f"Merriam strip of {word} took: {end_merriam_strip - start_merriam_strip} seconds")
    return root

def merriam_time2(word):
    start_merriam_strip = time.time()
    url_merriam = 'https://www.merriam-webster.com/dictionary/' + str(word or '')
    raw_html = simple_get(url_merriam)
    html = BeautifulSoup(raw_html, 'html.parser')
    stripped_text = html.text[0:1000]
    root = stripped_text.split('recents     ')[1].split(' ')[0]
    end_merriam_strip = time.time()
    print(f"Merriam strip of {word} took: {end_merriam_strip - start_merriam_strip} seconds")
    return root

"""
def merriam_strip(word):
    start_merriam_strip = time.time()
    url_merriam = 'https://www.merriam-webster.com/dictionary/' + str(word or '')
    raw_html = simple_get(url_merriam)
    stripped_html = raw_html.decode()[0:30000]

    try:
        html = BeautifulSoup(stripped_html, 'html.parser')
        hword = html.find('h1', attrs={'class': "hword"}).text

        stripped_words = []
        
        
        #for hword in hwords:
        #    stripped_words.append(hword.text.strip())
        #stripped_words.append(hword.text.strip())

        end_merriam_strip = time.time()
        if print_check:
            print(f"Merriam strip of {word} took: {end_merriam_strip - start_merriam_strip} seconds")
        return hword
    except TypeError:
        return None

       # for hword in hwords:
       #     stripped_words.append(hword.text.strip())
       # stripped_words.append(hword.text.strip())


        end_merriam_strip = time.time()
        if print_check:
            print(f"Merriam strip of {word} took: {end_merriam_strip - start_merriam_strip} seconds")
        return hword
    except TypeError:
        return None
"""

def merriam_root(word):
    start_merriam_root = time.time()
    url_merriam = 'https://www.merriam-webster.com/dictionary/' + str(word or '')
    raw_html = simple_get(url_merriam)
    html = BeautifulSoup(raw_html, 'html.parser')
    html_text = html.get_text()
    root_word = html_text.split("recents     ")[1].split(' ')[0]
    end_merriam_root = time.time()
    if print_check:
        print(f"Checking merriam root time: {end_merriam_root - start_merriam_root} seconds")

    return root_word

def merriam_root_check(word1, word2):
    return merriam_root(word1) == merriam_root(word2)

def etym(word):
    url_etym = 'https://www.etymonline.com/word/' + str(word or '')
    raw_html = simple_get(url_etym)

    html = BeautifulSoup(raw_html, 'html.parser')
    spans = html.find_all('span', {'class': 'foreign notranslate'})
    roots = []
    for span in spans:
        roots.append(span.text.strip())

    """
    cross_ref_list = []
    refs = html.find_all('a', {'class': "crossreference notranslate"})
    for ref in refs:
        cross_ref_list.append(ref.text.strip())
    """

    return roots

def merriam_word_check(word):
    start_merriam_word_check = time.time()
    url_merriam = 'https://www.merriam-webster.com/dictionary/' + word
    raw_html = simple_get(url_merriam)
    html = BeautifulSoup(raw_html, 'html.parser')
    titles = html.find_all('title')

    titles_list = []
    for title in titles:
        titles_list.append(title.text.strip().split(' | ')[0])

    is_proper_noun = [not word.islower() for word in titles_list]
    end_merriam_word_check = time.time()
    if print_check:
        print(f"Merriam word check time: {end_merriam_word_check - start_merriam_word_check} seconds")
    return not all(is_proper_noun)

def lookup(word):
    url_etym = 'https://www.etymonline.com/word/' + str(word or '')
    raw_html = simple_get(url_etym)
    # stripped_word = merriam_strip(word)


    try:
        start_etymonline = time.time()
        html = BeautifulSoup(raw_html, 'html.parser')
        spans = html.find_all('span', {'class': 'foreign notranslate'})
        links = html.find_all('a', {'class': "crossreference notranslate"})
        roots = [word]
        for span in spans:
            roots.append(span.text.strip())
        for link in links:
            roots.append(link.text.strip())
        roots = [item for item in roots if not '-' in item]
        end_etymonline = time.time()
        if print_check:
            print(f"Etymonline of {word} took: {end_etymonline - start_etymonline} seconds")
        return roots
    except TypeError:
        """
        start_etymonline_strip = time.time()

        url_etym = 'https://www.etymonline.com/word/' + str(stripped_word or '')
        raw_html = simple_get(url_etym)

        try:
            html = BeautifulSoup(raw_html, 'html.parser')
            spans = html.find_all('span', {'class': 'foreign notranslate'})
            roots = [stripped_word]
            for span in spans:
                roots.append(span.text.strip())

            roots = [item for item in roots if not '-' in item]

            end_etymonline_strip = time.time()
            if print_check:
                print(f"Etymonline with stripped word {stripped_word} took: {end_etymonline_strip - start_etymonline_strip} seconds")

            return roots

        except TypeError:
            return [stripped_word]
        """
        return None




