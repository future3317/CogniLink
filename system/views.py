from django.shortcuts import render, HttpResponse, redirect, reverse
from system.models import Account
from django.http import JsonResponse
import py2neo
from py2neo import Graph, Node, Relationship, RelationshipMatcher, NodeMatcher
import pandas as pd
from django.shortcuts import render
from util.pre_load import neo4jconn, course_dict
import json


yes = 0
bookname = "Hello World"
# Create your views here.

def login(request):
    if request.method == 'POST':
        #print("进入页面")
        email = request.POST.get('username')
        password = request.POST.get('password')
        corr_email = Account.objects.filter(email=email).first()
        #print("获取到信息")
        #print(email)
        #print(password)
        #print(corr_email)
        #print(len(email))

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



#输入两个节点的名字，漫游查询他们的路径
def wander(request):
    neo4j_data = {'data': [], 'links': []}
    if request.method == "POST":
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
        StartPoint = request.POST.get("StartPoint")
        EndPoint = request.POST.get("EndPoint")
        node_matcher = NodeMatcher(graph)  # 节点匹配器
        relation_matcher = RelationshipMatcher(graph)  # 关系匹配器

        # 找到查询关系中的两个节点，
        start_node = node_matcher.match(name=StartPoint).first()
        end_node = node_matcher.match(name=EndPoint).first()

        # 定义data数组，存放节点信息
        data = []
        # 定义关系数组，存放节点间的关系
        links = []

        # 定义开始节点和结束节点的名称
        start_node_name = StartPoint
        end_node_name = EndPoint

        # 获取需要查询的标签

        label = start_node.labels

        # 执行Cypher查询
        query = """
        MATCH p = (a)-[r*]-(b)
        WHERE a.name = $start_node_name and b.name = $end_node_name
        AND ALL(n1 in nodes(p) WHERE size([n2 in nodes(p) WHERE id(n1) = id(n2)])=1)
        RETURN p
        """
        result = graph.run(query, start_node_name=start_node_name, end_node_name=end_node_name)

        print(result)

        # node_name = [node["name"] for record in result for node in record["p"].nodes]

        # 从路径p中取出所有的节点名称
        data1 = []
        node_detail=[]
        for record in result:
            data1= [node["name"] for node in record["p"].nodes]
            node_detail = [node["detail"] for node in record["p"].nodes]

        # 查询指定标签的所有节点，并将节点信息取出存放在data数组中
        for i in range(len(data1) ):
            # 构造字典，存储单个节点信息
            dict = {
                'name': data1[i],
                'symbolSize': 80 if data1[i] in [start_node_name, end_node_name] else 50,
                'category': 0 if data1[i] in [start_node_name, end_node_name] else 1,
                'des': node_detail[i]
            }
            # 将单个节点信息存放在data数组中
            data.append(dict)

            # 查询指定标签的所有关系，并将关系信息存放在links数组中
        query = """
        MATCH p = (a)-[r*]-(b)
        WHERE a.name = $start_node_name and b.name = $end_node_name
        AND ALL(n1 in nodes(p) WHERE size([n2 in nodes(p) WHERE id(n1) = id(n2)]) = 1)
        RETURN relationships(p) AS relationships
        """
        result = graph.run(query, start_node_name=start_node_name, end_node_name=end_node_name)

        # 从结果中提取关系
        result_data = result.data()
        if result_data:
            relationships_list = result_data[0]['relationships']

            # 遍历关系并提取必要的信息
            for relationship in relationships_list:
                source = relationship.start_node['name']
                target = relationship.end_node['name']
                name = type(relationship).__name__

                # 为每个关系构造字典并添加到links中
                dict = {
                    'source': source,
                    'target': target,
                    'name': name,

                }
                links.append(dict)
        # 将所有的节点信息和关系信息存放在一个字典中
        neo4j_data = {
            'data': data,
            'links': links,
        }
        neo4j_data = json.dumps(neo4j_data)

    return render(request, './system/wander.html', {'neo4j_data': neo4j_data})



def detail_edit(request):
    neo4j_data = {'data': [], 'links': []}
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
        Pointname = request.POST.get("Pointname")
        Pointtype = request.POST.get("Pointtype")
        Pointdetail = request.POST.get("detail")

        matcher = NodeMatcher(graph)
        person = matcher.match(Pointtype, name=Pointname).first()
        person["detail"] = Pointdetail
        graph.push(person)

        label = person.labels
        print(label)
        # 定义data数组，存放节点信息
        data = []
        # 定义关系数组，存放节点间的关系
        links = []

        # 查询指定标签的所有节点，并将节点信息取出存放在data数组中
        query = f"MATCH (n{label}) RETURN n"
        result = graph.run(query)
        for record in result:
            # 取出节点的name
            node_name = record["n"]["name"]
            node_detail = record["n"]["detail"]
            # 构造字典，存储单个节点信息
            dict = {
                'name': node_name,
                'symbolSize': 50,
                'category': 1,
                'des': node_detail
            }
            # 将单个节点信息存放在data数组中
            data.append(dict)

        # 查询指定标签的所有关系，并将关系信息存放在links数组中
        query = f"MATCH (n{label})-[r]->() RETURN r"
        result = graph.run(query)
        for record in result:
            # 取出开始节点的name
            source = record["r"].start_node["name"]
            # 取出结束节点的name
            target = record["r"].end_node["name"]
            # 取出开始节点的结束节点之间的关系
            name = type(record["r"]).__name__
            # 构造字典存储单个关系信息
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            # 将单个关系信息存放进links数组中
            links.append(dict)

        # 将所有的节点信息和关系信息存放在一个字典中

        neo4j_data = {
            'data': data,
            'links': links,
        }
        neo4j_data = json.dumps(neo4j_data)
    return render(request, './system/detail_edit.html', {'neo4j_data': neo4j_data})



def add_book(request):
    neo4j_data = {'data': [], 'links': []}
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")
        BookName = request.POST.get("BookName")
        bookname = BookName;
        BookIntro = request.POST.get("BookIntro")
        InitNode = request.POST.get("InitNode")
        InitNodeType = request.POST.get("InitNodeType")
        InitNodeDetail = request.POST.get("InitNodeDetail")

        zero_node = Node(InitNodeType, name=BookName,detail=BookIntro)
        graph.create(zero_node)

        init_node = Node(InitNodeType, name=InitNode,detail=InitNodeDetail)
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


        # 输入要查询的标签
        label = InitNodeType

        # 定义data数组，存放节点信息
        data = []
        # 定义关系数组，存放节点间的关系
        links = []

        # 查询指定标签的所有节点，并将节点信息取出存放在data数组中
        query = f"MATCH (n:{label}) RETURN n"
        result = graph.run(query)
        for record in result:
            # 取出节点的name
            node_name = record["n"]["name"]
            # 构造字典，存储单个节点信息
            dict = {
                'name': node_name,
                'symbolSize': 50,
                'category': '1'
            }
            # 将单个节点信息存放在data数组中
            data.append(dict)

        # 查询指定标签的所有关系，并将关系信息存放在links数组中
        query = f"MATCH (n:{label})-[r]->() RETURN r"
        result = graph.run(query)
        for record in result:
            # 取出开始节点的name
            source = record["r"].start_node["name"]
            # 取出结束节点的name
            target = record["r"].end_node["name"]
            # 取出开始节点的结束节点之间的关系
            name = type(record["r"]).__name__
            # 构造字典存储单个关系信息
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            # 将单个关系信息存放进links数组中
            links.append(dict)

        # 将所有的节点信息和关系信息存放在一个字典中
        neo4j_data = {
            'data': data,
            'links': links
        }
        neo4j_data = json.dumps(neo4j_data)
        return render(request, './system/wander.html', {'neo4j_data': neo4j_data})
    return render(request, './system/add_book.html')
def node_new(request):
    neo4j_data = {'data': [], 'links': []}
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

        # 输入要查询的标签
        label = NodeType

        # 定义data数组，存放节点信息
        data = []
        # 定义关系数组，存放节点间的关系
        links = []

        # 查询指定标签的所有节点，并将节点信息取出存放在data数组中
        query = f"MATCH (n:{label}) RETURN n"
        result = graph.run(query)
        for record in result:
            # 取出节点的name
            node_name = record["n"]["name"]
            # 构造字典，存储单个节点信息
            dict = {
                'name': node_name,
                'symbolSize': 50,
                'category': 1
            }
            # 将单个节点信息存放在data数组中
            data.append(dict)

        # 查询指定标签的所有关系，并将关系信息存放在links数组中
        query = f"MATCH (n:{label})-[r]->() RETURN r"
        result = graph.run(query)
        for record in result:
            # 取出开始节点的name
            source = record["r"].start_node["name"]
            # 取出结束节点的name
            target = record["r"].end_node["name"]
            # 取出开始节点的结束节点之间的关系
            name = type(record["r"]).__name__
            # 构造字典存储单个关系信息
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            # 将单个关系信息存放进links数组中
            links.append(dict)

        # 将所有的节点信息和关系信息存放在一个字典中
        neo4j_data = {
            'data': data,
            'links': links,
        }
        neo4j_data = json.dumps(neo4j_data)

    return render(request, './system/node_new.html', {'neo4j_data': neo4j_data})

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
    neo4j_data = {'data': [], 'links': []}
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
        #print(result)  # 打印结果，格式一般是 (节点一)-[关系]->(节点二)
        #print(result.nodes)  # 打印节点

        graph.separate(result)  # 删除关系

        # 创建新关系
        if start_node and end_node:
            new_relationship = Relationship(start_node, relationship_type, end_node)
            graph.create(new_relationship)

        # 将新关系添加到图数据库中
        #print(start_point)
        #print(end_point)
        #print(relationship_type)

        label = start_node.labels

        # 定义data数组，存放节点信息
        data = []
        # 定义关系数组，存放节点间的关系
        links = []

        # 查询指定标签的所有节点，并将节点信息取出存放在data数组中
        query = f"MATCH (n{label}) RETURN n"
        result = graph.run(query)
        for record in result:
            # 取出节点的name
            node_name = record["n"]["name"]
            # 构造字典，存储单个节点信息
            dict = {
                'name': node_name,
                'symbolSize': 80 if node_name in [start_point, end_point] else 50,
                'category': 0 if node_name in [start_point, end_point] else 1
            }
            # 将单个节点信息存放在data数组中
            data.append(dict)

        # 查询指定标签的所有关系，并将关系信息存放在links数组中
        query = f"MATCH (n{label})-[r]->() RETURN r"
        result = graph.run(query)
        for record in result:
            # 取出开始节点的name
            source = record["r"].start_node["name"]
            # 取出结束节点的name
            target = record["r"].end_node["name"]
            # 取出开始节点的结束节点之间的关系
            name = type(record["r"]).__name__
            # 构造字典存储单个关系信息
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            # 将单个关系信息存放进links数组中
            links.append(dict)

        # 将所有的节点信息和关系信息存放在一个字典中
        neo4j_data = {
            'data': data,
            'links': links,
        }
        print("**************************")
        print(neo4j_data)
        print("**************************")
        neo4j_data = json.dumps(neo4j_data)
    return render(request, './system/relationship_edit.html', {'neo4j_data': neo4j_data})


def relationship_new(request):
    neo4j_data = {'data': [], 'links': []}
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

        # 指定标签
        label = node1.labels

        # 定义data数组，存放节点信息
        data = []
        # 定义关系数组，存放节点间的关系
        links = []

        # 查询指定标签的所有节点，并将节点信息取出存放在data数组中
        query = f"MATCH (n{label}) RETURN n"
        result = graph.run(query)
        for record in result:
            # 取出节点的name
            node_name = record["n"]["name"]
            # 构造字典，存储单个节点信息
            dict = {
                'name': node_name,
                'symbolSize': 50,
                'category': 1
            }
            # 将单个节点信息存放在data数组中
            data.append(dict)

        # 查询指定标签的所有关系，并将关系信息存放在links数组中
        query = f"MATCH (n{label})-[r]->() RETURN r"
        result = graph.run(query)
        for record in result:
            # 取出开始节点的name
            source = record["r"].start_node["name"]
            # 取出结束节点的name
            target = record["r"].end_node["name"]
            # 取出开始节点的结束节点之间的关系
            name = type(record["r"]).__name__
            # 构造字典存储单个关系信息
            dict = {
                'source': source,
                'target': target,
                'name': name
            }
            # 将单个关系信息存放进links数组中
            links.append(dict)

        # 将所有的节点信息和关系信息存放在一个字典中
        neo4j_data = {
            'data': data,
            'links': links,
        }

        neo4j_data = json.dumps(neo4j_data)

    return render(request, './system/relationship_new.html', {'neo4j_data': neo4j_data})

def wander_1(request):
    if request.method == 'POST':
        graph = Graph("http://localhost:7474/", auth=("neo4j", "futureneo"), name="neo4j")

    return render(request, './system/wander_1.html')