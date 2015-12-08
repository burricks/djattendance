from django.db import models
from django.contrib.auth.models import Group


""" SERVICES models.py 
This data model defines services in the training. We organize services in the following way:
    Category: this is a broad category that contains specific services. For example,
    Cleanup is a category that contains services such as Tuesday Breakfast Cleanup or
    Saturday Lunch Cleanup. Guard contains Guards A, B, C, and D. 

    Service: this refers to a specific service that repeats on a weekly basis.
    I.e. Tuesday Breakfast Prep is a service. It repeats every week. A specific instance
    of that service is defined in the service scheduler module as a service Instance.

    Period: this is a period in which services are active and generally changes with
    the schedule of the training. Most of the time, the regular FTTA schedule will be in
    effect, but there are exceptions such as Service Week and the semiannual training.

"""

class Category(Group):
    """
    Defines a service category such as Cleanup, Guard, Mopping, Chairs, etc.
    """
    # name = models.CharField(max_length=75)
    description = models.TextField(blank=True, null=True)

    #return services of this Category
    def getServices(self):
        #return Service.objects.filter(category=self)
        return self.service_set.all()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Service(Group):
    """" FTTA service class to define service such as
    Tues. Breakfast Cleanup, Dinner Prep, Guard A, Wednesday Chairs, etc.

    This also includes designated services such as Accounting or Lights.
    """

    

    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category)
    isActive = models.BooleanField(default=True)

    # every service have different workload,
    # for example guard is much more intense than cleaning
    workload = models.IntegerField()

    def __unicode__(self):
        return self.name


class Period(models.Model):
    """define Service Period such as Pre-Training, FTTA regular week, etc"""

    name = models.CharField(max_length=200)
    description = models.TextField()

    #which Service is on this Period
    service = models.ManyToManyField(Service)

    startDate = models.DateField('start date')
    endDate = models.DateField('end date')

    #return the services of this Period
    def getServices(self):
        return self.service.all()

    def __unicode__(self):
        return self.name
