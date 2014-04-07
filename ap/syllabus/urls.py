from django.conf.urls import patterns, url
from syllabus.views import CLView, SyllabusDetailView, HomeView, DetailView, TestView, DeleteSyllabusView, AddSyllabusView, SLView, AddSessionView
from syllabus.models import Syllabus, Session
from terms.models import Term
from terms import views

urlpatterns = patterns('',

	# url(r'^$', HomeView.as_view(), name='home-view'),

	url(r'^$', HomeView.as_view(model=Term), name='home-view'),	

	url(r'^(?P<term>(Fa|Sp)\d{2})/$', CLView.as_view(model=Syllabus,
			context_object_name="list"), name='classlist-view'),

	url(r'^(?P<term>(Fa|Sp)\d{2})/(?P<kode>\D{0,5})/(?P<pk>\d+)$', 
        DetailView.as_view(model=Syllabus), name='detail-view'),

	url(r'^(?P<term>(Fa|Sp)\d{2})/add_syllabus.html$', 
        AddSyllabusView.as_view(), name='add-syllabus'),
 
	url(r'^(?P<term>(Fa|Sp)\d{2})/delete/(?P<pk>\d+)$', 
        DeleteSyllabusView.as_view(), name='delete-syllabus'),	

    url(r'^session$', SLView.as_view(model=Session), name='session-view'),

    url(r'^session/add_session.html$', 
        AddSessionView.as_view(model=Session), name='add-session')

	# url(r'^Term/(?P<kode>\D+)/$', DetailView.as_view(model=Syllabus), name='detail-view'),

)



