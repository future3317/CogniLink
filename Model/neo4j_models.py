# -*- coding: utf-8 -*-
from py2neo import Graph,NodeMatcher

class KnowledgePoint():
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Question():
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Neo4j_Handle():
	graph = None
	# matcher = None
	def __init__(self):
		pass

	def connectNeo4j(self):
		self.graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
		# self.matcher = NodeMatcher(self.graph)




