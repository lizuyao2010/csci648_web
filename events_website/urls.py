from django.conf.urls import include, url
from django.contrib import admin
from events.views import EventsListView
from events import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'events_website.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    # url(r'^list/$',views.list),
    # url(r'^detail/$',views.detail),
    url(r'^$',views.search),
    url(r'^search/$',views.search),
    # url(r'^$', EventsListView.as_view(model=Post), name='events-list'),
    url(r'^events/(?P<event_id>[a-z\d-]+)/$', views.event_detail),
    url(r'^map/$',views.map),
]
