import math
import heapq
import shelve
import os
from pathlib import Path
from utils import build_posting_str
from posting import Posting

id_to_url = dict()
indexes = []
index_buf = []
index_dicts = []
closed = []
fragments = []

#O(n)
def merge_indexes():
    'Initializes merging process by opening all partial indexes and reading an initial buffer from each'
    print("Phase 2: Merging indexes")
    global id_to_url
    global indexes
    global index_buf
    global index_dicts
    global closed
    global fragments
    docs = shelve.open('docs.db')
    id_to_url = docs['id_to_url']
    n = docs['doc_count']
    file_index = dict()
    i_count = 0
    cwd = os.path.dirname(__file__)
    filename = os.path.join(cwd, "partials")
    partials = Path(filename)
    for index in partials.iterdir():
        indexes.append(open(index, 'r'))
        i_count += 1
    with open('full_index.txt', 'a') as idex:
        for i in range(i_count):
            index_buf.append('')
            fragments.append('')
            index_dicts.append(dict())
            while index_dicts[i] == {} and i+1 not in closed:
                index_buf[i], closed = chunk_read(indexes[i], index_buf[i], closed, i)
                index_dicts[i], fragments[i] = eval_dict(index_dicts[i], index_buf[i], fragments[i])
        file_index = write_to_file(file_index, n, idex, i_count)
        idex.close()
    for index in indexes:
        index.close()
    docs['id_to_url'] = id_to_url
    docs.sync()
    docs['file_positions'] = file_index
    docs.sync()

#O(1)
def chunk_read(index, buf, closed, num):
    'Reads a fixed chunk of data from the given index file, also checks whether or not the file has been fully read'
    if num+1 not in closed:
        buf = index.read(20000)
        if buf == '':
            closed.append(num+1)
    return buf, closed

#O(n)
def eval_dict(di, buf, frag):
    'Evaluates each complete term/postings list in the read buffer for a given index file'
    di = dict()
    lines = buf.splitlines()
    if frag != '':
        lines[0] = frag + lines[0]
        frag = ''
    for l in lines:
        if l != '':
            try:
                d = eval(l)
                di.update(d)
            except SyntaxError:
                frag = l
    return di, frag

#O(n)
def write_to_file(file_pos, n, merged, i_count):
    'Reads, processes, and writes chunks of partial index data into a full index file by terms in alphabetical order'
    global id_to_url
    global index_dicts
    global index_buf
    global fragments
    global closed
    keys = []
    popped = []
    base_pos = 0
    full_str = ''
    for d in index_dicts:
        keys.append(sorted(d.keys()))
    for k in keys:
        popped.append(heapq.heappop(k))
    while len(closed) < i_count:
        posts = []
        df = 0
        prev_docid = 0
        current, popped, keys = determine_current(popped, keys)
        for d in range(i_count):
            if d+1 in closed:
                continue
            try:
                posts = posts + index_dicts[d][current]
                #read the next chunk of file after processing its last line
                if keys[d] == []:
                    index_dicts[d] = dict()
                    while index_dicts[d] == {} and d+1 not in closed:
                        index_buf[d], closed = chunk_read(indexes[d], index_buf[d], closed, d)
                        index_dicts[d], fragments[d] = eval_dict(index_dicts[d], index_buf[d], fragments[d])
                    keys[d] = sorted(index_dicts[d].keys())
                if keys[d] != []:
                    popped[d] = heapq.heappop(keys[d])
            except KeyError:
                continue
        posts = sorted(posts, key = lambda p: p.docid)
        for p in posts:
            if p.docid != prev_docid:
                df += 1
            prev_docid = p.docid
        for p in posts:
            p.tfidf = p.tfidf*math.log(n/df)
            id_to_url[str(p.docid)][1] += p.tfidf**2
        posts = sorted(posts, key = lambda p: (p.fields, p.tfidf), reverse = True)
        posts.insert(0,df)
        full_p = build_posting_str(posts)
        file_pos[current] = base_pos + len(full_str.encode('utf-8'))
        full_str += "{"+"\"{}\": {}".format(current,full_p)+ "}\n"
        if len(full_str.encode('utf-8')) >= 10000*i_count:
            merged.write(full_str)
            full_str = ''
            base_pos = merged.tell()
    if full_str != '':
        merged.write(full_str)
    return file_pos

#O(n)
def determine_current(popped, keys):
    'Decides which term to process next, given the highest alphabetical term from each partial index buffer'
    global indexes
    global index_buf
    global index_dicts
    global closed
    global fragments
    current = ''
    next_to_pop = 0
    for i in range(len(popped)):
        if i+1 in closed:
            continue
        if current == '':
            current = popped[i]
            next_to_pop = i
        elif popped[i] < current:
            current = popped[i]
            next_to_pop = i
    return current, popped, keys

if __name__ == '__main__':
    merge_indexes()
