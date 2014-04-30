from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView, TemplateView, DetailView, ArchiveIndexView, CreateView, DeleteView
from .models import Syllabus, Session
from terms.models import Term
from django.shortcuts import render_to_response
from django.template import RequestContext
from .forms import NewSyllabusForm
from django.core.urlresolvers import reverse_lazy

from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django import http
from django.template import Context
import ho.pisa as pisa
import cStringIO as StringIO
import cgi

class HomeView(ListView):
    template_name = "syllabus/termlist.html"
    model = Term
    context_object_name = 'termlist'

class CLView(ListView):
    template_name = "syllabus/classlist.html"
    context_object_name = 'list'
    model = Syllabus

    """this is to get ?P<term> from urls.py 
    and make it accessible to the template classlist.html 
    by using {{term}}"""
    def get_context_data(self, **kwargs):
        context = super(CLView, self).get_context_data(**kwargs)
        context['term'] = self.kwargs['term']
        return context

class DetailView(DetailView):
    template_name = "syllabus/details.html"
    model = Syllabus
    context_object_name = 'syllabus'
    slug_url_kwarg = 'term','kode'
 
    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['term'] = self.kwargs['term']
        context['kode'] = self.kwargs['kode']
        context['pk'] = self.kwargs['pk']
        return context

class AddSyllabusView(CreateView):
    model = Syllabus
    template_name = 'syllabus/new_syllabus_form.html'
    form_class = NewSyllabusForm

    def get_context_data(self, **kwargs):
        context = super(AddSyllabusView, self).get_context_data(**kwargs)
        context['term'] = self.kwargs['term']
        return context

    def get_success_url(self):
        term = self.kwargs['term']
        return reverse_lazy('classlist-view', args=[term])

class DeleteSyllabusView(DeleteView):
    model = Syllabus
    template_name = 'syllabus/delete_syllabus_confirm.html'

    def get_success_url(self):
        term = self.kwargs['term']
        return reverse_lazy('classlist-view', args=[term])

class SyllabusDetailView(ListView):
    model = Syllabus
    template_name = "syllabus/detail.html"  
    context_object_name = 'syllabus'
    slug_field = 'code'
    slug_url_kwarg = 'code'

class AddSessionView(CreateView):
    model = Session
    template_name = 'session/new_session_form.html'

    def get_success_url(self):
        term = self.kwargs['term']
        kode = self.kwargs['kode']
        pk = self.kwargs['pk']
        return reverse_lazy('detail-view', args=[term,kode,pk])

class DeleteSessionView(DeleteView):
    model = Session
    template_name = 'session/delete_session_confirm.html'

    def get_success_url(self):
        term = self.kwargs['term']
        kode = self.kwargs['kode']
        syllabus_pk = self.kwargs['syllabus_pk']
        return reverse_lazy('detail-view', args=[term,kode,syllabus_pk])

"""TODO: to display the sessions in chronological order in pdf"""
def pdf_view(request, term, kode, syllabus_pk):
    syllabus = get_object_or_404(Syllabus, pk=syllabus_pk)
    return write_pdf('syllabus/syllabus_pdf.html',{
        'pagesize' : 'A4',
        'syllabus' : syllabus})

def write_pdf(template_src, template_context):
    template = get_template(template_src)
    context = Context(template_context)
    html = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(
        html.encode("UTF-8")), result)
    if not pdf.err:
        return http.HttpResponse(result.getvalue(), \
            mimetype='application/pdf')
    else:
        return http.HttpResponse('Yesh! %s' % cgi.escape(html))

