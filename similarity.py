import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import pickle
import scipy

def get_api_namelist():
    sql = "select API from cmb_production_apis"
    api_namelist = query(sql, "API_DATA.db")
    return api_namelist

def get_sentences():
    # sql = "select API from cmb_production_apis"
    # api_namelist = query(sql, "API_DATA.db")
    api_namelist = get_api_namelist()
    sentences = []
    for data in api_namelist:
        name_words_list = data[0].split('-')
        suffix = name_words_list[-1]
        if (suffix[0] == 'v') & suffix[1:].isdecimal():
            name_words_list.pop()
        sentence = " ".join(name_words_list) + "."
        sentences.append(sentence)
    return [api_namelist, sentences]

def similarity_cal(sentences):
    dic = {}
    model = SentenceTransformer('roberta-large-nli-stsb-mean-tokens')
    sentence_embeddings = model.encode(sentences)
    for sentence, embedding in zip(sentences, sentence_embeddings):
        dic[sentence] = embedding
    f = open('vector_dic.txt', 'wb')
    pickle.dump(sentence_embeddings, f)
    f.close()

def read_vector_dic():
    f = open('vector_dic2.txt', 'rb')
    data = pickle.load(f)
    f.close()
    return data

def test(api_namelist, sentences, target_sentence, number_top_matches):
    result_list = []
    query = target_sentence
    queries = [query]
    model = SentenceTransformer('roberta-large-nli-stsb-mean-tokens')
    query_embeddings = model.encode(queries)
    sentence_embeddings = read_vector_dic()
    for query, query_embedding in zip(queries, query_embeddings):
        distances = scipy.spatial.distance.cdist([query_embedding], sentence_embeddings, "cosine")[0]
        results = zip(range(len(distances)), distances)
        results = sorted(results, key=lambda x: x[1])

        # print("Target Sentence:", query)
        # print("\nTop {} most similar sentences in corpus:".format(number_top_matches))

        for idx, distance in results[0:number_top_matches]:
            # print(sentences[idx].strip(), "(Cosine Score: %.4f)" % (1 - distance))
            result_list.append((api_namelist[idx][0], format(1-distance, '.4f')))
    return result_list

def apiname_convert_sentence(apiname):
    name_words_list = apiname.split('-')
    suffix = name_words_list[-1]
    if (suffix[0] == 'v') & suffix[1:].isdecimal():
        name_words_list.pop()
    sentence = " ".join(name_words_list) + "."
    return sentence

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

# API = "cmb-dbbhk-notification-pa-pes-fulfillment-v1"
def main_process(apiname):
    target_sentence = apiname_convert_sentence(apiname)
    list = get_sentences()
    api_namelist = list[0]
    sentences = list[1]
    return test(api_namelist, sentences, target_sentence, 10)

main_process("cmb-dbbhk-notification-pa-pes-fulfillment-v1")

# similarity_cal(get_sentences())

# read_vector_dic()
# a = np.array([1, 2, 3])
# print(type(a))
# print(a)
# dic = {}
# dic["1"] = a
# dic["2"] = a
# print(dic)
# f=open('file1.txt','wb')
# pickle.dump(dic,f)
# f.close()

