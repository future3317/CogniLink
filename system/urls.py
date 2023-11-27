from .views import logout,logon,delete_nodes_by_name,login,node_new,person,node_edit,relationship_edit,relationship_new,wander,add_book,detail_edit,home,course
from django.urls import path
from django.conf.urls import url

urlpatterns = [
    path('login/',login,name='login'),
    path('logon/',logon,name='logon'),
    path('logout/', logout, name='logout'),
    path('course/', course, name='course'),
    path('home/', home, name='home'),
    path('wander/', wander, name='wander'),
    path('detail_edit/', detail_edit, name='detail_edit'),
    path('add_book/', add_book, name='add_book'),
    path('node_new/', node_new, name='node_new'),
    path('node_edit/', node_edit, name='node_edit'),
    path('relationship_edit/', relationship_edit, name='relationship_edit'),
    path('relationship_new/', relationship_new, name='relationship_new'),
    path('person/', person, name='person'),
    path('delete_nodes_by_name/', delete_nodes_by_name, name='delete_nodes_by_name'),
]
