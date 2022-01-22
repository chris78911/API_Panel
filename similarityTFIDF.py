import sqlite3
import jieba.posseg as pseg
import codecs
from gensim import corpora, models, similarities

def get_corpus():
    stopwords = ["v0","v1","v2","v3","v4","v5","v6","v7","v8","v9"]
    corpus = []
    sql = "select API from cmb_production_apis"
    api_namelist = query(sql, "API_DATA.db")
    for item in api_namelist:
        list = item[0].split("-")
        list1 = []
        for i in list:
            if i not in stopwords:
                list1.append(i)
        # corpus.append(item[0].split("-"))
        corpus.append(list1)
    return corpus



def query(sql, db):
    query_result = []
    con = sqlite3.connect(db)
    cur = con.cursor()
    data = cur.execute(sql)
    for item in data:
        query_result.append(item)
    cur.close()
    con.close()
    return query_result

# def tokenization(filename):
#     result = []
#     with open(filename, 'r') as f:
#         text = f.read()
#         words = pseg.cut(text)
#     for word, flag in words:
#         if flag not in stop_flag and word not in stopwords:
#             result.append(word)
#     return result

def take_second(list):
    return list[1]

def main_process(apiname):
    stopwords = ["-"]
    stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r']

    filenames = ['test.txt',
                 'test2.txt',
                 'test3.txt'
                ]
    corpus = get_corpus()
    # for each in filenames:
    #     # print("-----------------")
    #     # print(tokenization(each))
    #     corpus.append(tokenization(each))
    # print(corpus)
    # print(get_corpus())

    dictionary = corpora.Dictionary(corpus)
    # print(dictionary)

    doc_vectors = [dictionary.doc2bow(text) for text in corpus]
    # print(len(doc_vectors))
    # print(doc_vectors)

    tfidf = models.TfidfModel(doc_vectors)
    tfidf_vectors = tfidf[doc_vectors]

    # print(len(tfidf_vectors))
    # print(len(tfidf_vectors[0]))

    query = apiname.split("-")
    # print(query)
    query_bow = dictionary.doc2bow(query)
    # print(len(query_bow))
    # print(query_bow)

    index = similarities.MatrixSimilarity(tfidf_vectors)
    sims = index[query_bow]
    # print(list(enumerate(sims)))
    new_sims = []
    for item in list(enumerate(sims)):
        new_sims.append([item[0], item[1]])

    new_sims = sorted(new_sims, key=lambda x: x[1])
    best10 = new_sims[-10:]
    best10.sort(key=take_second, reverse=True)
    res = []
    for item in best10:
        res.append(("-".join(corpus[item[0]]), item[1]))
    return res
    # print("-------------")
    # print(best10)
    # print(res)
