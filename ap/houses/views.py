from django.core.urlresolvers import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from .models import Bunk
from .forms import BunkForm


class BunkListView(ListView):
	model = Bunk
	context_object_name = 'bunks'
	template_name = 'houses/bunk_list.html'


class BunkFormView(FormView):
	form_class = BunkForm
	template_name = 'houses/bunk_update.html'
	success_url = reverse_lazy('houses:bunk_list')

	def get_context_data(self, **kwargs):
		context = super(BunkFormView, self).get_context_data(**kwargs)
		context['bunk'] = Bunk.objects.get(pk=self.kwargs['pk'])
		return context

	def form_valid(self, form):
		if form.is_valid():
			bunk = Bunk.objects.get(pk=self.kwargs['pk'])
			new_occupant = form.cleaned_data['trainee']

			# if bunk were to be assigned to 'vacant'
			if new_occupant == None:
				if hasattr(bunk, 'trainee'):
					old_occupant = bunk.trainee
					old_occupant.bunk = None
					old_occupant.save()
			# if bunk is vacant	
			elif not hasattr(bunk, 'trainee'):
				new_occupant.bunk = bunk
				new_occupant.save()
			# if new_occupant is to replace the old occupant
			elif hasattr(bunk, 'trainee') and new_occupant.bunk == None:
				old_occupant = bunk.trainee
				old_occupant.bunk = None
				new_occupant.bunk = bunk
				old_occupant.save()
				new_occupant.save()
			# if new_occupant were to swap with old occupant
			elif hasattr(bunk, 'trainee') and new_occupant.bunk != None:
				old_occupant = bunk.trainee
				old_occupant.bunk = new_occupant.bunk
				new_occupant.bunk = bunk
				old_occupant.save()
				new_occupant.save()

		return super(BunkFormView, self).form_valid(form)
