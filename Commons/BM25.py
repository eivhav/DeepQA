# Eivind Havikbotn (havikbot@stud.ntnu.no)
# Github repo github.com/eivhav/DeepQA
# BM25 base from http://lixinzhang.github.io/implementation-of-okapi-bm25-on-python.html

import math
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words
from nltk.stem.snowball import NorwegianStemmer
from gensim import corpora, models
import gensim
from gensim import similarities
import numpy
from Commons import Evaluator as evaluator

tokenizer = RegexpTokenizer(r'\w+')
# create Norwegian stop words list
no_stop = get_stop_words('norwegian')

# Create no_stemmer of NorwegianStemmer()
no_stemmer = NorwegianStemmer()

class BM25 :
    def __init__(self, fn_docs, delimiter='|') :
        self.dictionary = corpora.Dictionary()
        self.DF = {}
        self.delimiter = delimiter
        self.DocTF = []
        self.DocIDF = {}
        self.N = 0
        self.DocAvgLen = 0
        self.fn_docs = fn_docs
        self.DocLen = []
        self.buildDictionary()
        self.TFIDF_Generator()

    def buildDictionary(self) :
        raw_data = []
        for line in self.fn_docs :
            raw_data.append(line.strip().split(self.delimiter))
        self.dictionary.add_documents(raw_data)

    def TFIDF_Generator(self, base=math.e) :
        docTotalLen = 0
        for line in self.fn_docs :
            doc = line.strip().split(self.delimiter)
            docTotalLen += len(doc)
            self.DocLen.append(len(doc))
            #print self.dictionary.doc2bow(doc)
            bow = dict([(term, freq*1.0/len(doc)) for term, freq in self.dictionary.doc2bow(doc)])
            for term, tf in bow.items() :
                if term not in self.DF :
                    self.DF[term] = 0
                self.DF[term] += 1
            self.DocTF.append(bow)
            self.N = self.N + 1
        for term in self.DF:
            self.DocIDF[term] = math.log((self.N - self.DF[term] +0.5) / (self.DF[term] + 0.5), base)
        self.DocAvgLen = docTotalLen / self.N

    def BM25Score(self, Query=[], k1=1.5, b=0.75) :
        query_bow = self.dictionary.doc2bow(Query)
        scores = []
        for idx, doc in enumerate(self.DocTF) :
            commonTerms = set(dict(query_bow).keys()) & set(doc.keys())
            tmp_score = []
            doc_terms_len = self.DocLen[idx]
            for term in commonTerms :
                upper = (doc[term] * (k1+1))
                below = ((doc[term]) + k1*(1 - b + b*doc_terms_len/self.DocAvgLen))
                tmp_score.append(self.DocIDF[term] * upper / below)
            scores.append(sum(tmp_score))
        return scores

    def TFIDF(self) :
        tfidf = []
        for doc in self.DocTF :
            doc_tfidf = [(term, tf*self.DocIDF[term]) for term, tf in doc.items()]
            doc_tfidf.sort()
            tfidf.append(doc_tfidf)
        return tfidf

    def Items(self) :
        # Return a list [(term_idx, term_desc),]
        items = self.dictionary.items()
        items.sort()
        return items

def prepocess_data(raw):
    raw = raw.replace('E', 'æ').replace('A', 'å').replace('O', 'ø').lower()
    tokens = tokenizer.tokenize(raw)
    # remove stop words from tokens
    stopped_tokens = [i for i in tokens if not i in no_stop]

    # stem tokens
    stemmed_tokens = [no_stemmer.stem(i) for i in stopped_tokens]

    # add tokens to list
    out = ""
    for t in stemmed_tokens:
        out = out + str(t) + " "
    return out.strip()


def load_data(qa_pairs):
    queries = []
    answers = []
    for pair in qa_pairs:
        queries.append(prepocess_data(pair[0].strip()))
        answers.append(prepocess_data(pair[1].strip()))

    return queries, answers



def eval_BM25(qa_pairs):

    questions, answers = load_data(qa_pairs)
    fn_docs = answers
    bm25 = BM25(fn_docs, delimiter=' ')
    sim_matrix = []
    for i in range(len(questions)):
        Query = questions[i].split()
        scores = bm25.BM25Score(Query)
        sim_matrix.append(scores)
    np_sims = numpy.array(sim_matrix)

    eval_methods = [('MMR', 0), ('Top', 1), ('Top', 5), ('Top', 20)] # qa_pairs_text does not work
    evaluator.evaulate([], [], np_sims, eval_methods)


def eval_LDA(qa_pairs):
    questions, answers = load_data(qa_pairs)
    ans_texts = []
    q_texts = []
    for a in answers:
        ans_texts.append(a.replace('hei ', '').replace('fname ', '').split(' '))
    # turn our tokenized documents into a id <-> term dictionary
    dictionary = corpora.Dictionary(ans_texts)
    # convert tokenized documents into a document-term matrix
    corpus = [dictionary.doc2bow(text) for text in ans_texts]
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=50, id2word=dictionary, passes=20)
    topics = ldamodel.print_topics(num_topics=50, num_words=6)
    for t in topics:
        print(t)

    for q in questions:
        q_texts.append(q.replace('hei ', '').replace('fnam ', '').split(' '))
    dictionaryQ = corpora.Dictionary(q_texts)
    # convert tokenized documents into a document-term matrix
    corpus_1 = [dictionaryQ.doc2bow(text) for text in q_texts]
    ldamodel_q = gensim.models.ldamodel.LdaModel(corpus_1, num_topics=50, id2word=dictionaryQ, passes=20)
    topics = ldamodel_q.print_topics(num_topics=50, num_words=6)
    for t in topics:
        print(t)

    lda = ldamodel
    index = similarities.MatrixSimilarity(lda[corpus])
    index.save("simIndex.index")
    sim_matrix = []
    c = 0
    for i in range(len(questions)):
        Query = questions[i]
        vec_bow = dictionary.doc2bow(Query.lower().split())
        vec_lda = lda[vec_bow]
        sims = index[vec_lda]
        sim_matrix.append(sims)
        if c % 100 == 0: print(c)

    np_sims = numpy.array(sim_matrix)

    eval_methods = [('MMR', 0), ('Top', 1), ('Top', 5), ('Top', 20)] # qa_pairs_text does not work
    evaluator.evaulate([], [], np_sims, eval_methods)






