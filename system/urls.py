from .views import logout,logon,login,basic,graph,edit_node,check_node,home,course,search_course_knowledgepoint,search_question_knowledgepoint,search_relation
from django.urls import path
from django.conf.urls import url

urlpatterns = [
    path('login/',login,name='login'),
    path('logon/',logon,name='logon'),
    path('logout/', logout, name='logout'),
    path('graph/', graph, name='graph'),
    path("check_node", check_node, name="check_node"),
    path('edit_node/', edit_node, name='edit_node'),
    path('search_course_knowledgepoint/', search_course_knowledgepoint, name='search_course_knowledgepoint'),
    path('search_relation/', search_relation, name='search_relation'),
    path('edit_node/', edit_node, name='edit_node'),
    path('course/', course, name='course'),
    path('home/', home, name='home'),
    path('basic/', basic, name='basic'),
]
