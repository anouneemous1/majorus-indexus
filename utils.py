from posting import Posting

#O(n)
def build_posting_str(posting):
    'Creates a string representation of the posting list for writing to a file'
    count = 0
    full_posting = "["
    for post in posting:
        count += 1
        if count < len(posting):
            full_posting += repr(post) +  ", "
        else:
            full_posting += repr(post) + "]"
    return full_posting
