class Posting:
    def __init__(self, docid, tfidf, fields):
        self.docid = docid
        self.tfidf = tfidf
        self.fields = fields
    def __repr__(self):
        return "Posting({}, {}, {})".format(self.docid, self.tfidf, self.fields)
 
def didsearch(posts, searchid):
    for p in posts:
        if p.docid == searchid:
            return p
    return None

def skip_forward(posts, position, searchid):
    for i in range(position, len(posts)):
        if posts[i].docid == searchid:
            return i
    return len(posts)
