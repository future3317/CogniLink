from django.shortcuts import render, HttpResponse, redirect, reverse
from system.models import Account
from django.http import JsonResponse
import py2neo
from py2neo import Graph, Node, Relationship, RelationshipMatcher, NodeMatcher
import pandas as pd
from django.shortcuts import render
from util.pre_load import neo4jconn, course_dict
import json


# Create your views here.

def login(request):
    if request.method == 'POST':
        print("进入页面")
        email = request.POST.get('username')
        password = request.POST.get('password')
        corr_email = Account.objects.filter(email=email).first()
        print("获取到信息")
        print(email)
        print(password)
        print(corr_email)
        print(len(email))

        if corr_email is not None and email == corr_email.email and password == corr_email.password:
            print('登录成功')
            return redirect(reverse('home'))
        else:
            print('登录失败')
            return HttpResponse('登录失败')

    return render(request, './system/login.html')


def logon(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        if password == repassword:
            user = Account()
            user.name = name
            user.email = email
            user.password = password
            user.save()
            print('注册成功')
            return redirect(reverse('login'))
        else:
            print('两次密码不一致')
            return HttpResponse('两次密码不一致')

    return render(request, './system/logon.html')


def logout(request):
    return HttpResponse('退出')


def index(request):
    print("进入index")
    return redirect(reverse('login'))


def graph(request):
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")

        if 'query_nodes' in request.POST:
            name1 = request.POST.get('node1')
            node_matcher = NodeMatcher(graph)  # 节点匹配器

        elif 'create_node' in request.POST:
            name1 = request.POST.get('node1')
        elif 'create_relation' in request.POST:

            name1 = request.POST.get('node1')
            relation = request.POST.get('relation')
            name2 = request.POST.get('node2')
            node1 = Node('Person', name=name1)
            node2 = Node('Person', name=name2)


            graph.create(node1)
            graph.create(node2)
            graph.create(relation)
        elif 'edit_nodes' in request.POST:
            return redirect(reverse('edit_node'))
    return render(request, './system/graph.html')


def edit_node(request):
    if request.method == "POST":
        originalNodeName = request.POST.get("originalNodeName")
        originalNodeType = request.POST.get("originalNodeType")

        # 建立与Neo4j数据库的连接
        graph = Graph("http://localhost:7474/", username="neo4j", password="futureneo")

        # 根据编辑后的节点名字和类型查询要更新的节点
        node = graph.nodes.match(name=originalNodeName, type=originalNodeType).first()

        edited_node_name = request.POST.get("editedNodeName")
        edited_node_type = request.POST.get("editedNodeType")
        if node:
            # 更新节点的属性
            node["name"] = edited_node_name
            node["type"] = edited_node_type
            node.push()  # 将更新后的节点保存回数据库

            updated_node = {
                "name": edited_node_name,
                "type": edited_node_type
            }

        else:
            # 节点不存在的处理逻辑
            return HttpResponse('节点不存在')

    return render(request, "./system/edit_node.html")


def check_node(request):
    if request.method == "POST":
        data = json.loads(request.body)
        edited_node_name = data.get("nodeName")
        edited_node_type = data.get("nodeType")

        # 建立与Neo4j数据库的连接
        graph = Graph("http://localhost:7474/", username="neo4j", password="futureneo")

        # 在Neo4j数据库中查询是否存在匹配的节点
        node = graph.nodes.match(name=edited_node_name, type=edited_node_type).first()

        if node:
            return JsonResponse({"nodeExists": True})
        else:
            return JsonResponse({"nodeExists": False})

    return JsonResponse({"error": "Invalid request method"})


def search_course_knowledgepoint(request):
    ctx = {}
    # 根据传入的实体名称搜索出关系
    if (request.GET):
        entity = request.GET['user_text']
        if entity in course_dict.keys():
            entity = course_dict.get(entity)
        entityRelation = neo4jconn.course_knowledgepoint(entity)
        if len(entityRelation) == 0:
            # 若数据库中无法找到该实体，则返回数据库中无该实体
            ctx = {'title': '<h2>知识库中暂未添加该实体</h1>'}
            return render(request, './system/course.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
        else:
            return render(request, './system/course.html',
                          {'entityRelation': json.dumps(entityRelation, ensure_ascii=False)})
    # 需要进行类型转换
    return render(request, './system/course.html', {'ctx': ctx})


# 题目知识点查询
def search_question_knowledgepoint(request):
    ctx = {}
    # 根据传入的实体名称搜索出关系
    if (request.GET):
        entity = request.GET['user_text']
        entityRelation = neo4jconn.question_knowledgepoint(entity)
        if len(entityRelation) == 0:
            # 若数据库中无法找到该实体，则返回数据库中无该实体
            ctx = {'title': '<h2>知识库中暂未添加该实体</h1>'}
            return render(request, './system/question.html', {'ctx': json.dumps(ctx, ensure_ascii=False)})
        else:
            return render(request, './system/question.html',
                          {'entityRelation': json.dumps(entityRelation, ensure_ascii=False)})
    # 需要进行类型转换
    return render(request, './system/question.html', {'ctx': ctx})


# 知识点关系查询
def search_relation(request):
    ctx = {}
    if (request.GET):
        # 实体1
        entity1 = request.GET['entity1_text']
        # 关系
        relation = request.GET['relation_name_text']
        # 实体2
        entity2 = request.GET['entity2_text']
        # 将关系名转为大写
        relation = relation.upper()

        if entity1 in course_dict.keys():
            entity1 = course_dict.get(entity1)
        if entity2 in course_dict.keys():
            entity2 = course_dict.get(entity2)

        # 保存返回结果
        searchResult = {}

        # 1.若只输入entity1,则输出与entity1有直接关系的实体和关系
        if (len(entity1) != 0 and len(relation) == 0 and len(entity2) == 0):
            searchResult = neo4jconn.findRelationByEntity1(entity1)
            if (len(searchResult) > 0):
                return render(request, './system/graph.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        # 2.若只输入entity2则,则输出与entity2有直接关系的实体和关系
        if (len(entity2) != 0 and len(relation) == 0 and len(entity1) == 0):
            searchResult = neo4jconn.findRelationByEntity2(entity2)
            if (len(searchResult) > 0):
                return render(request, './system/graph.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        # 3.若输入entity1和relation，则输出与entity1具有relation关系的其他实体
        if (len(entity1) != 0 and len(relation) != 0 and len(entity2) == 0):
            searchResult = neo4jconn.findOtherEntities(entity1, relation)
            if (len(searchResult) > 0):
                return render(request, './system/graph.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        # 4.若输入entity2和relation，则输出与entity2具有relation关系的其他实体
        if (len(entity2) != 0 and len(relation) != 0 and len(entity1) == 0):
            searchResult = neo4jconn.findOtherEntities2(entity2, relation)
            if (len(searchResult) > 0):
                return render(request, './system/graph.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        # 5.若输入entity1和entity2,则输出entity1和entity2之间的关系
        if (len(entity1) != 0 and len(relation) == 0 and len(entity2) != 0):
            searchResult = neo4jconn.findRelationByEntities(entity1, entity2)
            if (len(searchResult) > 0):
                return render(request, './system/graph.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        # 6.若输入entity1,entity2和relation,则输出entity1、entity2是否具有相应的关系
        if (len(entity1) != 0 and len(entity2) != 0 and len(relation) != 0):
            print(relation)
            searchResult = neo4jconn.findEntityRelation(entity1, relation, entity2)
            if (len(searchResult) > 0):
                return render(request, './system/graph.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        # 7.若全为空
        if (len(entity1) != 0 and len(relation) != 0 and len(entity2) != 0):
            pass

        ctx = {'title': '<h1>暂未找到相应的匹配</h1>'}
        return render(request, './system/graph.html', {'ctx': ctx})

    return render(request, './system/graph.html', {'ctx': ctx})

def course(request):
    return render(request, './system/course.html')

def home(request):
    if request.method == 'POST':
        # Get the new subject name from the POST request.
        new_subject_name = request.POST.get('new_subject')

        # Connect to the Neo4j database.
        graph = neo4jconn()

        # Check if the subject already exists to prevent duplicates.
        if not graph.run(f"MATCH (s:Subject {{name: '{new_subject_name}'}}) RETURN s").data():
            # If the subject doesn't exist, create a new node.
            new_subject_node = Node("Subject", name=new_subject_name)
            graph.create(new_subject_node)
            msg = f"学科 {new_subject_name} 已成功添加!"
        else:
            msg = f"学科 {new_subject_name} 已经存在!"

        # Return a message to inform the user of the result.
        return render(request, './system/home.html', {"message": msg})
    else:
        # If the request is not a POST, just render the home page.
        return render(request, './system/home.html')



#输入两个节点的名字，查询他们的关系
def wander(request):
    ctx = {}
    if request.method == "POST":
        # 实体1
        entity1 = request.POST.get('StartPoint')
                # 实体2
        entity2 = request.POST.get('EndPoint')


        print(entity1)
        print(entity2)

        if entity1 in course_dict.keys():
            entity1 = course_dict.get(entity1)
        if entity2 in course_dict.keys():
            entity2 = course_dict.get(entity2)

        # 保存返回结果
        searchResult = {}
        # 1.若只输入entity1,则输出与entity1有直接关系的实体和关系

        if (len(entity1) != 0  and len(entity2) == 0):
            searchResult = neo4jconn.findRelationByEntity1(entity1)
            if (len(searchResult) > 0):
                return render(request, './system/wander.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        if (len(entity1) != 0 and len(entity2) != 0):
            searchResult = neo4jconn.findRelationByEntities(entity1, entity2)
            print(searchResult)
            if (len(searchResult) > 0):
                return render(request, './system/wander.html',
                              {'searchResult': json.dumps(searchResult, ensure_ascii=False)})

        ctx = {'title': '<h1>暂未找到相应的匹配</h1>'}
        return render(request, './system/wander.html', {'ctx': ctx})

    return render(request, './system/wander.html', {'ctx': ctx})



def detail_edit(request):
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
        Pointname = request.POST.get("Pointname")
        Pointtype = request.POST.get("Pointtype")
        Pointdetail = request.POST.get("detail")

        matcher = NodeMatcher(graph)
        person = matcher.match(Pointtype, name=Pointname).first()
        person["detail"] = Pointdetail
        graph.push(person)

    return render(request, './system/detail_edit.html')
def add_book(request):
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
        BookName = request.POST.get("BookName")
        BookIntro = request.POST.get("BookIntro")
        InitNode = request.POST.get("InitNode")
        InitNodeType = request.POST.get("InitNodeType")
        InitNodeDetail = request.POST.get("InitNodeDetail")

        zero_node = Node(BookName, name=BookName,detail=BookIntro)
        graph.create(zero_node)

        init_node = Node(BookName, name=InitNode,detail=InitNodeDetail)
        graph.create(init_node)

        relationship_type = "对应"

        if zero_node and init_node:
            # 创建关系
            relation = Relationship(zero_node, relationship_type, init_node)
            graph.create(relation)

        print(BookName)
        print(BookIntro)
        print(InitNode)
        print(InitNodeType)
        print(InitNodeDetail)

        # 指定标签
        label = BookName

        # 查询相同标签下的所有节点和关系
        subgraph = graph.run(f"MATCH (n:{label})-[*0..]->(m:{label}) RETURN n, m").to_subgraph()

        # 转换为字典格式
        data = {
            "nodes": [],
            "relationships": []
        }

        for node in subgraph.nodes:
            data["nodes"].append(dict(node))

        for relationship in subgraph.relationships:
            data["relationships"].append(dict(relationship))

        # 将数据保存到JSON文件
        with open("output_小学数学.json", "w") as file:
            json.dump(data, file)

    return render(request, './system/add_book.html')
def node_new(request):
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
        NodeName = request.POST.get("NodeName")
        NodeType = request.POST.get("NodeType")
        NodeDetail = request.POST.get("NodeDetail")

        node1 = Node(NodeType, name=NodeName,detail=NodeDetail)
        graph.create(node1)
        print(NodeName)
        print(NodeType)
        print(NodeDetail)
    return render(request, './system/node_new.html')

def node_edit(request):
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
        StartPoint = request.POST.get("StartPoint")
        EndPoint = request.POST.get("EndPoint")
        node1 = Node(EndPoint, name=StartPoint)
        graph.create(node1)
        print(StartPoint)
        print(EndPoint)

    return render(request, './system/node_edit.html')

def relationship_edit(request):
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
        start_point = request.POST.get("StartPoint")
        end_point = request.POST.get("EndPoint")
        relationship_type = request.POST.get("Relationship")

        node_matcher = NodeMatcher(graph)  # 节点匹配器
        relation_matcher = RelationshipMatcher(graph)  # 关系匹配器

        # 找到查询关系中的两个节点，
        start_node = node_matcher.match(name=start_point).first()
        end_node = node_matcher.match(name=end_point).first()

        result = relation_matcher.match({start_node, end_node}, r_type=None).first()
        print(result)  # 打印结果，格式一般是 (节点一)-[关系]->(节点二)
        print(result.nodes)  # 打印节点

        graph.separate(result)  # 删除关系

        # 创建新关系
        if start_node and end_node:
            new_relationship = Relationship(start_node, relationship_type, end_node)
            graph.create(new_relationship)

        # 将新关系添加到图数据库中
        print(start_point)
        print(end_point)
        print(relationship_type)

    return render(request, './system/relationship_edit.html')

def relationship_new(request):
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")

        # 从请求中获取节点和关系信息
        start_point = request.POST.get("StartPoint")
        end_point = request.POST.get("EndPoint")
        relationship_type = request.POST.get("Relationship")

        node1 = graph.nodes.match(name=start_point).first()
        node2 = graph.nodes.match(name=end_point).first()

        if node1 and node2:
            # 创建关系
            relation = Relationship(node1, relationship_type, node2)
            graph.create(relation)

        print(start_point)
        print(end_point)
        print(relationship_type)

    return render(request, './system/relationship_new.html')
