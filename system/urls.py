from .views import logout,logon,login,node_new,node_edit,relationship_edit,relationship_new,wander,graph,edit_node,add_book,detail_edit,check_node,home,course,search_course_knowledgepoint,search_question_knowledgepoint,search_relation
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
    path('wander/', wander, name='wander'),
    path('detail_edit/', detail_edit, name='detail_edit'),
    path('add_book/', add_book, name='add_book'),
    path('node_new/', node_new, name='node_new'),
    path('node_edit/', node_edit, name='node_edit'),
    path('relationship_edit/', relationship_edit, name='relationship_edit'),
    path('relationship_new/', relationship_new, name='relationship_new'),
]
