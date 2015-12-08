from django import forms
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import Group, User
from django.utils.translation import ugettext_lazy as _
from django_select2 import *

from .models import User, Trainee, TrainingAssistant, Locality
from aputils.admin import VehicleInline, EmergencyInfoInline
from django_extensions.admin import ForeignKeyAutocompleteAdmin


"""" ACCOUNTS admin.py """


class APUserCreationForm(forms.ModelForm):
    """ A form for creating a new user """

    password = forms.CharField(label="Password",
                               widget=forms.PasswordInput)
    password_repeat = forms.CharField(label="Password confirmation",
                                      widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "firstname", "lastname", "gender",)

    def clean(self):
        cleaned_data = super(APUserCreationForm, self).clean()
        password = cleaned_data.get("password")
        password_repeat = cleaned_data.get("password_repeat")
        if password != password_repeat:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

    def save(self, commit=True):
        """ Save the provided password in hashed format """
        user = super(APUserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class APUserChangeForm(forms.ModelForm):
    """ A form for updating users. """

    class Meta:
        model = User
        exclude = ['password']


class APUserAdmin(UserAdmin):
    # Set the add/modify forms
    add_form = APUserCreationForm
    form = APUserChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin that reference
    # specific fields on auth.User
    list_display = ("email", "is_staff", "firstname", "lastname", "gender")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "firstname", "lastname")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")
    fieldsets = (
        (None, {"fields":
                ("email",)}),

        ("Personal info", {"fields":
                           ("firstname", "lastname","gender",)}),
        ("Permissions", {"fields":
                         ("is_active",
                             "is_staff",
                             "is_superuser",
                             "groups",
                             "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "firstname", "lastname", "gender", "password",
                       "password_repeat")}
         ),
    )


class CurrentTermListFilter(SimpleListFilter):
	#Lists the trainees by term
	title = _('current term')

	parameter_name = 'current term'

	def lookups(self, request, model_admin):
		"""
		Returns a list of tuples. The first element in each tuple is the coded value
		for the option that will appear in the URL query. The second element is the human-
		readable name for the option that will appear in the right sidebar.
		"""
		return (
			('1term', _('1st term')),
			('2term', _('2nd term')),
			('3term', _('3rd term')),
			('4term', _('4th term')),
		)

	def queryset(self, request, queryset):
		"""
		"""
		if self.value() == '1term':
			q=queryset
			q_ids = [person.id for person in q if person.current_term==1]
			q = q.filter(id__in=q_ids)
			return q

		if self.value() == '2term':
			q=queryset
			q_ids = [person.id for person in q if person.current_term==2]
			q = queryset.filter(id__in=q_ids)
			return q

		if self.value() == '3term':
			q=queryset
			q_ids = [person.id for person in q if person.current_term==3]
			q = queryset.filter(id__in=q_ids)
			return q

		if self.value() == '4term':
			q=queryset
			q_ids = [person.id for person in q if person.current_term==4]
			q = queryset.filter(id__in=q_ids)
			return q

class FirstTermMentorListFilter(SimpleListFilter):
	#Make list of 1st term mentors for email notifications
	title = _('mentors')

	parameter_name = 'mentor'

	def lookups(self, request, model_admin):
		"""
		Returns a list of tuples. The first element in each tuple is the coded value
		for the option that will appear in the URL query. The second element is the human-
		readable name for the option that will appear in the right sidebar.
		"""
		return (
			('1termmentor', _('1st term mentors')),
			('2termmentor', _('2nd term mentors')),
			('3termmentor', _('3rd term mentors')),
			('4termmentor', _('4th term mentors')),
		)

	def queryset(self, request, queryset):
		"""
		"""
		if self.value() == '1termmentor':
			"""queryset of 1st term mentors """
			q=queryset.filter(mentor__isnull=False)
			q_ids = [person.mentor.id for person in q if person.current_term==1]
			q = q.filter(id__in=q_ids)
			return q

		if self.value() == '2termmentor':
			"""queryset of 2nd term mentors """
			q=queryset.filter(mentor__isnull=False)
			q_ids = [person.mentor.id for person in q if person.current_term==2]
			q = q.filter(id__in=q_ids)
			return q

		if self.value() == '3termmentor':
			"""queryset of 3rd term mentors """
			q=queryset.filter(mentor__isnull=False)
			q_ids = [person.mentor.id for person in q if person.current_term==3]
			q = q.filter(id__in=q_ids)
			return q

		if self.value() == '4termmentor':
			"""queryset of 4th term mentors """
			q=queryset.filter(mentor__isnull=False)
			q_ids = [person.mentor.id for person in q if person.current_term==4]
			q = q.filter(id__in=q_ids)
			return q


# Adding a custom TraineeAdminForm to use prefetch_related all the locality many-to-many relationship
# to pre-cache the relationships and squash all the n+1 sql calls.
class TraineeAdminForm(forms.ModelForm):
  class Meta:
    model = Trainee
    fields = '__all__'
  locality = ModelSelect2MultipleField(queryset=Locality.objects.prefetch_related('city__state'),
        required=False,
        search_fields=['^city'],
        widget=Select2MultipleWidget(
            select2_options={
                'width': '220px',
            }
        )) # could add state and country


class TraineeAdmin(ForeignKeyAutocompleteAdmin):
  form = TraineeAdminForm

  # User is your FK attribute in your model
  # first_name and email are attributes to search for in the FK model
  related_search_fields = {
      'account': ('firstname', 'lastname', 'email'),
      'TA': ('account__firstname', 'account__lastname', 'account__email'),
      'mentor': ('account__firstname', 'account__lastname', 'account__email'),
      'spouse': ('account__firstname', 'account__lastname', 'account__email'),
  }

  search_fields = ['account__email', 'account__firstname', 'account__lastname']

  fieldsets = (
      (None, {
          'fields': (('account', 'active',), 'type', 'locality', 'term',
              ('date_begin', 'date_end',), ('married', 'spouse',),
              ('TA', 'mentor',), 'team', ('house', 'bunk',), 'address',
              'self_attendance', 'services')
      }),
  )
  list_display = ('__unicode__','current_term','_trainee_email','team', 'house',)
  list_filter = ('active', CurrentTermListFilter,FirstTermMentorListFilter,)
  inlines = [
      VehicleInline, EmergencyInfoInline,
  ]

# Register the new Admin
admin.site.register(User, APUserAdmin)
admin.site.register(Trainee, TraineeAdmin)
admin.site.register(TrainingAssistant)
