# Majorus Indexus
Search engine scripts written for an Information Retrieval course.

## Overview
Majorus Indexus is a set of Python scripts designed for an Information Retrieval course. The goal of the project was to create a search engine that could process a huge corpus of documents into an index and search through this index under harsh conditions. The corpus was provided for this project; it contained 88 domains with just under 56,000 pages, and totals in an unzipped size of 229MB. The requirements for this search engine was for it to have a response time of under 300 milliseconds for most queries and without being able to load a full inverted index onto memory. Instead, the index had to be loaded to at least 3 partial indexes on disk during index construction and either merged or left as separate index files at the end of construction. Also, the search component had to read postings from the index(es) on disk rather than try to load the index onto memory.

Below is a more detailed description of each file, by the order in which they should be run.

## index_builder
First script for taking in a corpus and adding each document to an inverted index one-by-one. Takes in a path to the corpus on disk as a command-line argument. A hashmap is made to store doc ID's so that duplicate docs can be caught and skipped. The builder processes 10000 docs before it writes a partial index file into disk.

## index_merger
Second script for merging all partial indexes created by index_builder into one main inverted index. Takes in a path to a folder containing the partial indexes as a command-line argument. Each partial index is read line-by-line until each posting list has been read into memory as a dict object. These posting lists are then written to the main index, taking care to insert the lists by alphabetical order of the terms and merging posting lists if they share the same term.

## ranked_query
Third script that acts as the search component. Takes a query as user input. The user's query is first processed through a RegexpTokenizer and a PorterStemmer. The searcher then looks through the index to find the most relevant documents based on each query term. To save time while searching for each query term, the index is first seeked for the term, and only the first 85000 chars from where the index seeked are read into memory. Document scores are calculated with a combination of TF-IDF and PageRank scoring. The top 10 documents for the query are displayed, along with the retrieval time starting from when the query was sent.

**The last three files should not be run; they are all helper files.**

## processor
Helper functions for processing documents to add to the index. Uses nltk and BeautifulSoup.

## posting
Class file for the posting list. Includes functions for searching the list by document ID and an unused function.

## utils
Script file for functions that do not fit anywhere else. This only contains a function for creating a string representation of a Posting list.
