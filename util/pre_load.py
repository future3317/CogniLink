# -*- coding: utf-8 -*-
from pyhanlp import HanLP
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
import pickle

from Model.neo4j_models import Neo4j_Handle

def init_hanlp():
    segment = HanLP.newSegment().enableNameRecognize(True).enableOrganizationRecognize(True).enablePlaceRecognize(True).enableCustomDictionaryForcing(True)
    print("init hanlp...")
    return segment

def init_neo4j():
    neo4jconn = Neo4j_Handle()
    neo4jconn.connectNeo4j()
    print('init neo4j...')
    return neo4jconn

def init_course_kp():
    '''

    '''
    course_dict = {}


    print('init course dict...')
    return course_dict

# 初始化模型
def init_model():
    print('init intent classification model...')
    words_path = os.path.join(os.getcwd() + '/util/qa_model', "words.pkl")
    with open(words_path, 'rb') as f_words:
        words = pickle.load(f_words)



# 1.初始化hanlp
segment = init_hanlp()

# 2.初始化neo4j
neo4jconn = init_neo4j()

