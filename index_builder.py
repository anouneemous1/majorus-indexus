from pathlib import Path
from urllib.parse import urlparse, urldefrag
from bs4 import BeautifulSoup
import os
import json
import shelve
import sys
import math

import processor
from posting import Posting
from utils import build_posting_str
from index_merger import merge_indexes

#path: /home/lopes/Datasets/IR/DEV/
#module load python/3.7.4

#Docid -> URL
id_to_url = dict()
#URL -> Docid
url_to_id = dict()

#O(n)
def main(corpus):
    'Big function that handles initiating page processing and index construction'
    global id_to_url
    docs = shelve.open('docs.db')
    docs.clear()
    index = dict()
    doc_count = 0
    file_num = 0
    cwd = os.path.dirname(__file__)
    filename = os.path.join(cwd, "partials")
    os.makedirs(filename, exist_ok = True)
    corpus = Path(corpus)
    files = corpus.rglob("*.json")
    print("Phase 1: Processing corpus")
    for page in files:
        with open(page, encoding="utf8", errors='ignore') as f:
            rPage = f.read()
            jPage = json.loads(rPage)
            if jPage['encoding'].lower() not in ['ascii', 'utf-8', 'utf8']:
                continue
            page_id = hash_page(doc_count, jPage['url'])
            if page_id == -1:
                f.close()
                continue
            else:
                doc_count += 1
            pageSoup = BeautifulSoup(jPage['content'], features = "lxml")
            parsed_imp = processor.parse_page(pageSoup, ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'bold', 'strong', 'em'])
            parsed_std = processor.parse_page(pageSoup, ['p'])
            words_imp = processor.tokenize(parsed_imp)
            words_imp = processor.process_dupes(words_imp)
            words_std = processor.tokenize(parsed_std)
            words_std = processor.process_dupes(words_std)
            index = processor.post_words(words_imp, index, page_id, True)
            index = processor.post_words(words_std, index, page_id, False)
            f.close()
        if doc_count%10000 == 0:
            file_num += 1
            write_partial(index, file_num)
            index = dict()
    file_num += 1
    write_partial(index, file_num)
    docs['id_to_url'] = id_to_url
    docs.sync()
    docs['doc_count'] = doc_count
    docs.sync()

#O(1)
def hash_page(count, url): 
    'Creates an int docid for the url, while also making sure the defragmented URL has not already been counted'
    global url_to_id
    global id_to_url
    true_url = urldefrag(url)[0]
    if true_url in url_to_id:
        return -1
    c = str(count+1)
    id_to_url[c] = [true_url, 0]
    url_to_id[true_url] = c
    return count+1

#O(n)
def write_partial(index, file_num):
    'Writes a partial index of a certain size to a file'
    print("Writing partial {} to disk".format(file_num))
    with open('partials/index{}.txt'.format(file_num), 'a') as idex:
        full_str = ''
        tokens = sorted(index.items())
        for token, posts in tokens:
            full_p = build_posting_str(posts)
            full_str += "{"+"\"{}\": {}".format(token,full_p)+ "}\n"
        idex.write(full_str)
    print("Partial index write done. Resuming corpus processing.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Too many or too few arguments.")
        sys.exit()
    main(sys.argv[1])
    merge_indexes()
