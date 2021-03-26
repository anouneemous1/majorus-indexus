from posting import Posting, skip_forward
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
import sys
import heapq
import math
import shelve
import re
import time

from processor import process_dupes

posts_found = dict()

def query_main():
    'Runs the main loop of asking for queries, processing them, and returning retrieval results'
    global posts_found
    db = shelve.open('docs.db')
    docs = db['id_to_url']
    seeker = db['file_positions']
    n = db['doc_count']
    normalized_query = 0
    query =  ''
    with open('full_index.txt', 'r') as index:
        while True:
            query = input("Enter search term(s) or input '0quit' to quit: ")
            if query == '0quit':
                break
            start = time.time()
            lowerQuery = query.lower()
            w = RegexpTokenizer('\w+', flags = re.ASCII)
            s = PorterStemmer()
            terms = w.tokenize(lowerQuery)
            for t in terms:
                s.stem(t)
            term_counts = process_dupes(terms)
            query_scores, normalized_query = query_tfidf(term_counts,n,index,seeker)
            term_process(query, query_scores, normalized_query, docs, n)
            end = time.time()
            print(end - start)
            posts_found = dict()
        index.close()

#
def query_tfidf(terms, n, index, seeker):
    'Calculates the tfidf of the query term(s) and loads individual postings lists from the index'
    global posts_found
    scores = dict()
    normalized = 0
    tms = sorted(terms.keys())
    for t in terms:
        try:
            index.seek(seeker[t])
            t_str = index.read(85000)
            if '\n' in t_str:
                all_str = t_str.splitlines()
                t_d = eval(all_str[0])
            else:
                if t_str.endswith("]}") == False:
                    end = t_str.rfind("),")
                    part_str = t_str[:end+1] + "]}"
                    t_d = eval(part_str)
                else:
                    t_d = eval(t_str)
            idf = math.log(n/t_d[t][0])
            if idf <= 1.5:
                continue
            posts_found.update(t_d)
            w = (1+math.log(terms[t]))*idf
            scores.update({t:w})
            normalized += w**2
        except KeyError:
            scores.update({t:0})
    normalized = math.sqrt(normalized)
    return scores, normalized

def term_process(query, query_scores, normalized, docs, n):
    'Processes the postings lists by terms and retrieves the top 10 results'
    global posts_found
    scores = dict()
    results = []
    terms = sorted(posts_found.keys())
    for t in terms:
        i = 1
        if math.log(n/len(posts_found[t])) <= 1:
            continue
        while i < len(posts_found[t]):
            d = posts_found[t][i].docid
            if d not in scores:
                scores.update({d: 0})
            if posts_found[t][i].fields == True:
                scores[d] += 20
            scores[d] += query_scores[t]*posts_found[t][i].tfidf
            i += 1
    for s in sorted(scores.keys()):
        scores[s] = scores[s]/(normalized*math.sqrt(docs[str(s)][1]))
        heapq.heappush(results, (s, scores[s]))
    final = heapq.nlargest(10, results, key = lambda i: i[1])
    print("Results for {}:".format(query))
    for i in final:
        print(docs[str(i[0])][0])

if __name__ == "__main__":
    query_main()
