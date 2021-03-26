from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from bs4 import BeautifulSoup
import re
import math
from posting import Posting

#O(n+m)
def parse_page(page, types):
    'Parses the desired tagged text using BeautifulSoup'
    chunks = []
    if len(types) == 1:
        for tag in page.findAll():
            if tag.name.lower() in ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'strong', 'em']:
                tag.extract()
    text = page.find_all(types)
    for t in text:
        tex = t.text
        tex = re.sub(r"[^\x00-\x7F]+", ' ', tex)
        chunks.append(tex.lower())
    parsed = ' '.join(chunks)
    return parsed

#O(c)
def tokenize(text):
    'Tokenizes the input text using nltk\'s tokenizing function'
    tokenizer = RegexpTokenizer('\w+', flags = re.ASCII)
    words = tokenizer.tokenize(text)
    return stem_words(words)

#O(n)
def stem_words(words):
    'Uses Porter Stemming on the tokenized words'
    ps = PorterStemmer()
    for w in words:
        ps.stem(w)
    return words

#O(n)
def process_dupes(words):
    'Processes duplicate words by using a dict to keep count of duplicated words'
    nondupe = dict()
    for w in words:
        #Skip words bigger than 4 digits or not in date format
        if re.match(r'[0-9]{1,4}|[0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}', w) != None:
            continue
        #Skip "_" and "-" repeating
        if re.match(r'^(_+|-+)$', w) != None:
            continue
        if w not in nondupe:
            nondupe.update({w: 0})
        nondupe[w] += 1
    return nondupe

#O(n+m)
def post_words(words, index, page_id, field):
    'Adds to the index using the tokens, their frequencies, the current doc_id, and misc. fields'
    for w in words.keys():
        if w not in index:
            wPost = [Posting(page_id, 1+math.log(words[w]), field)]
            index.update({w: wPost})
        else:
            index[w].append(Posting(page_id, 1+math.log(words[w]), field))
    return index
