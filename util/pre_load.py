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
    小学语文 -> 小学语文综合库
    小学数学 -> 小学数学综合库
    小学英语 -> 小学英语综合库
    初中语文 -> 初中语文综合库
    初中数学 -> 初中数学综合库
    初中英语 -> 初中英语综合库
    初中历史 -> 初中历史综合库
    初中生物 -> 初中生物综合库
    初中化学 -> 初中化学综合库
    初中地理 -> 初中地理综合库
    初中物理 -> 初中物理综合库
    初中政治 -> 初中政治综合库
    初中信息技术 -> 初中信息技术综合库
    高中语文 -> 高中语文综合库
    高中英语 -> 高中英语综合库
    高中数学 -> 高中数学综合库
    高中历史 -> 高中历史综合库
    高中生物 -> 高中生物综合库
    高中化学 -> 高中化学综合库
    高中地理 -> 高中地理综合库
    高中物理 -> 高中物理综合库
    高中政治 -> 高中政治综合库
    高中信息技术 -> 高中信息技术综合库
    高中通用技术 -> 高中通用技术综合库
    '''
    course_dict = {}
    course_dict['小学语文'] = '小学语文综合库'
    course_dict['小学数学'] = '小学数学综合库'
    course_dict['小学英语'] = '小学英语综合库'
    course_dict['初中语文'] = '初中语文综合库'
    course_dict['初中数学'] = '初中数学综合库'
    course_dict['初中英语'] = '初中英语综合库'
    course_dict['初中历史'] = '初中历史综合库'
    course_dict['初中生物'] = '初中生物综合库'
    course_dict['初中化学'] = '初中化学综合库'
    course_dict['初中地理'] = '初中地理综合库'
    course_dict['初中物理'] = '初中物理综合库'
    course_dict['初中政治'] = '初中政治综合库'
    course_dict['初中信息技术'] = '初中信息技术综合库'
    course_dict['高中语文'] = '高中语文综合库'
    course_dict['高中英语'] = '高中英语综合库'
    course_dict['高中数学'] = '高中数学综合库'
    course_dict['高中历史'] = '高中历史综合库'
    course_dict['高中生物'] = '高中生物综合库'
    course_dict['高中化学'] = '高中化学综合库'
    course_dict['高中地理'] = '高中地理综合库'
    course_dict['高中物理'] = '高中物理综合库'
    course_dict['高中政治'] = '高中政治综合库'
    course_dict['高中信息技术'] = '高中信息技术综合库'
    course_dict['高中通用技术'] = '高中通用技术综合库'

    print('init course dict...')
    return course_dict

# 初始化模型
def init_model():
    print('init intent classification model...')
    words_path = os.path.join(os.getcwd() + '/util/qa_model', "words.pkl")
    with open(words_path, 'rb') as f_words:
        words = pickle.load(f_words)

# 初始化模型
def init_kp_predict_model():

    print('init knowledge point predict model...')
    #1.加载词典
    words_path = os.path.join(os.getcwd() + '/util/kp_predict_model', "words.pkl")
    with open(words_path, 'rb') as f_words:
        kp_words = pickle.load(f_words)

    #2.加载知识点名
    knowledge_points_path = os.path.join(os.getcwd() + "/util/kp_predict_model", 'knowledge_points.pkl')
    with open(knowledge_points_path, 'rb') as f_knowledge_points:
        knowledge_points = pickle.load(f_knowledge_points)

    #3.加载停词
    stopwords_path = os.path.join(os.getcwd() + "/util/kp_predict_model", 'stopwords.txt')
    stopwords_set = set()
    with open(stopwords_path, 'r', encoding='utf-8') as f_read:
        for line in f_read:
            stopwords_set.add(line.strip())

    # 4.构建和加载分类模型
    class TextCNN(nn.Module):
        def __init__(self, vocab_size, embedding_dim, output_size, filter_num=100, filter_size=(3, 4, 5), dropout=0.5):
            '''
            vocab_size:词典大小
            embedding_dim:词维度大小
            output_size:输出类别数
            filter_num:卷积核数量
            filter_size(3,4,5):三种卷积核，size为3,4,5，每个卷积核有filter_num个，卷积核的宽度都是embedding_dim
            '''
            super(TextCNN, self).__init__()
            self.embedding = nn.Embedding(vocab_size, embedding_dim)
            # conv2d(in_channel,out_channel,kernel_size,stride,padding),stride默认为1，padding默认为0
            self.convs = nn.ModuleList([nn.Conv2d(1, filter_num, (k, embedding_dim)) for k in filter_size])
            self.dropout = nn.Dropout(dropout)
            self.fc = nn.Linear(filter_num * len(filter_size), output_size)

        def forward(self, x):
            # x :(batch, seq_len)
            x = self.embedding(x)  # [batch,word_num,embedding_dim] = [N,H,W]
            x = x.unsqueeze(1)  # [batch, channel, word_num, embedding_dim] = [N,C,H,W]
            x = [F.relu(conv(x)).squeeze(3) for conv in
                 self.convs]  # len(filter_size) * (N, filter_num, H)
            # MaxPool1d(kernel_size, stride=None, padding=0, dilation=1, return_indices=False, ceil_mode=False),stride默认为kernal_size
            x = [F.max_pool1d(output, output.shape[2]).squeeze(2) for output in
                 x]  # len(filter_size) * (N, filter_num)
            x = torch.cat(x, 1)  # (N, filter_num * len(filter_size))
            x = self.dropout(x)
            x = self.fc(x)
            return x

    kp_predict_model = TextCNN(len(kp_words), 300, 73) # 300为embedding维度，73为知识点个数。
    model_path = os.path.join(os.getcwd() + '/util/kp_predict_model', "model.h5")
    kp_predict_model.load_state_dict(torch.load(model_path))
    return kp_predict_model,kp_words,knowledge_points,stopwords_set

# 1.初始化hanlp
segment = init_hanlp()

# 2.初始化neo4j
neo4jconn = init_neo4j()

# 3.初始化学科名
course_dict = init_course_kp()

# 4.初始化意图分类模型
model_dict = init_model()
