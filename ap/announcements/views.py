from django.views.generic.base import View
from .forms import NewAnnouncementForm
from django.contrib import messages
from messages_extends import constants as constant_messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from accounts.models import User


class AnnouncementListView(View):
	tempalte_name = 'announcements/announcement_list.html'

class AnnouncementCreateView(View):
	template_name = 'announcements/announcement_create.html'
	form_class = NewAnnouncementForm

	def get(self, request, *args, **kwargs):
		form = self.form_class()
		return render(request, self.template_name, {'form': form})

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.cleaned_data['user']
			send_to_all = form.cleaned_data['send_to_all']
			message = form.cleaned_data['message']
			
			# announcement to individual user
			if user != None and send_to_all == False:
				# sending the message to the user
				user = User.objects.get(pk=user.id)
				messages.add_message(request, constant_messages.INFO_PERSISTENT, message, user=user)
			# announcement to multiple users
			# announcement to all users
			elif send_to_all == True:
				for user in User.objects.all():
					messages.add_message(request, constant_messages.INFO_PERSISTENT, message, user=user)
			return HttpResponseRedirect(reverse_lazy('announcements:announcement_create'))
		return render(request, self.template_name, {'form': form})

	def get_context_data(self, **kwargs):
		context = super(AnnouncementView, self).get_context_data(**kwargs)
		return context

	# def post(self, request, *args, **kwargs):
	# 	if request.method == 'POST':
	# 	# 	form = NewAnnouncementForm(request.POST)
	# 	# 	if form.is_valid():
	# 	# 		print form.cleaned_data['user']
	# 	# 		print form.cleaned_data['send_to_all']
	# 	# 		print form.cleaned_data['message']
	# 	# 		return reverse_lazy('announcement_list')
	# 	# else:
	# 	# 	form = NewAnnouncementForm()
	# 		print "I am in"
	# 	return reverse_lazy('announcement_list')

