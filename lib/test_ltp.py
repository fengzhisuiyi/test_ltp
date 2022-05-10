# -*- coding: utf-8 -*-
"""
Created on Sat May  7 18:46:53 2022

@author: zyw19
"""

import hanlp
HanLP = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)

def hanlp_data(sentence_list):
    doc = HanLP(sentence_list)
    return doc['dep'],doc['pos/ctb'],doc['tok/fine'],doc['con']
    
    
def node_extraction(seg, pos):
    """从语义依存图中提取出节点的名字和节点类型"""
    for i in range(len(seg)):
        seg[i] = [str(i) for i in seg[i]]
        pos[i] = [str(i) for i in pos[i]]

    return seg, pos

def relation_extraction(ds,nodes):
    pass
    """
    提取出节点间的关系，将节点与关于整合成三元组，并存放在列表中。
    （node1,node2,relation)
    """
    rel = []
    for ds_sentence, nodes_sentence in zip(ds, nodes):
        rel_sentence = []
        for idx,(ds_word, nodes_word) in enumerate(zip(ds_sentence, nodes_sentence)):
            #print('!!!!!!!!',idx,int(ds_word[0]) - 1)
            # 根据索引提取出节点和关系
            index1 = idx#int(ds_word[0]) - 1
            index2 = int(ds_word[0]) - 1
            node1 = nodes_sentence[index1]
            node2 = nodes_sentence[index2]
            relation = ds_word[1]

            # 将节点和关系添加到3元组中
            rel_word = []
            rel_word.append(node1)
            rel_word.append(node2)
            rel_word.append(relation)

            # 将3元组整合到句子中
            rel_sentence.append(rel_word)

            # 将单句整合到列表中
        rel.append(rel_sentence)

    return rel
from py2neo import Node, Graph, Relationship
#from ltp_data import ltp_data
# 可以先阅读下文档：https://py2neo.org/v4/index.htm

class DataToNeo4j(object):
    """将excel中数据存入neo4j"""

    def __init__(self):
        """建立连接"""
        link = Graph("http://localhost:7474", auth=("neo4j", "zyw8253688"))
        self.graph = link
        # self.graph = NodeMatcher(link)
        self.graph.delete_all()

        """
        node3 = Node('animal' , name = 'cat')
        node4 = Node('animal' , name = 'dog')  
        node2 = Node('Person' , name = 'Alice')
        node1 = Node('Person' , name = 'Bob')  
        r1 = Relationship(node2 , 'know' , node1)    
        r2 = Relationship(node1 , 'know' , node3) 
        r3 = Relationship(node2 , 'has' , node3) 
        r4 = Relationship(node4 , 'has' , node2)    
        self.graph.create(node1)
        self.graph.create(node2)
        self.graph.create(node3)
        self.graph.create(node4)
        self.graph.create(r1)
        self.graph.create(r2)
        self.graph.create(r3)
        self.graph.create(r4)
        """

    def create_node(self, name_node, type_node):
        """建立节点"""
        nodes = []
        for name_sentence, type_sentence in zip(name_node, type_node):
            nodes_sentence = []
            for name_word, type_word in zip(name_sentence, type_sentence):
                # 创建节点
                node = Node(type_word, name = name_word)
                self.graph.create(node)
                # 保存下来
                nodes_sentence.append(node)
            nodes.append(nodes_sentence)

        print('节点建立成功')
        return nodes


    def create_relation(self, rel):
        """建立联系"""
        for sentence in rel:
            for word in sentence:
                try:
                    # 关系要转化成字符串格式
                    r = Relationship(word[0], str(word[2]), word[1])
                    self.graph.create(r)
                except AttributeError as e:
                    print(e)

        print('关系建立成功')

def test(sentence_list):
    ws,pos,dep = hanlp_data(sentence_list)

if __name__ == '__main__':
    #sentence_list = ["一加一等于","1+1等于","二加二十等于","50+887","50加90224.4"]
    sentence_list = ["一加一等于","1+1等于","二加二十再加5等于","50+887","50加90224.4","50加90224.4加4一"]
    dep, pos, ws,con = hanlp_data(sentence_list)#ltp_data()#
    create_data = DataToNeo4j()

    # 建立节点
    node_name, node_type = node_extraction(ws, pos)
    nodes = create_data.create_node(node_name, node_type)
    print("第一句话的节点：\n{k}".format(k = nodes[0]))
    
    # 建立联系
    rel = relation_extraction(dep, nodes)
    create_data.create_relation(rel)
    print("第一句话的关系：\n{k}".format(k = rel[0]))



#MATCH (n) DETACH DELETE n