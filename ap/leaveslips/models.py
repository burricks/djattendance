from django.db import models
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta

from schedules.models import Event
from accounts.models import Trainee, TrainingAssistant


""" leaveslips models.py
The leavelslip module takes care of all logic related to... you guessed it, leave slips.


DATA MODELS:
    - LeaveSlip: an abstract class that contains information common to all leave
    leave slips. Extended by Individual and Group slips.

    - IndividualSlip: extends LeaveSlip generic class. A leave slip that only
    applies to one trainee (but can apply to multiple events)

    - GroupSlip: extends LeaveSlip generic class. A leaveslip that can apply to
    a group of trainees, and covers a time range (rather than certain events).
"""


class LeaveSlip(models.Model):

    LS_TYPES = (
        ('CONF', 'Conference'),
        ('EMERG', 'Family Emergency'),
        ('FWSHP', 'Fellowship'),
        ('FUNRL', 'Funeral'),
        ('GOSP', 'Gospel'),
        ('INTVW', 'Grad School/Job Interview'),
        ('GRAD', 'Graduation'),
        ('MEAL', 'Meal Out'),
        ('NIGHT', 'Night Out'),
        ('OTHER', 'Other'),
        ('SERV', 'Service'),
        ('SICK', 'Sickness'),
        ('SPECL', 'Special'),
        ('WED', 'Wedding'),
        ('NOTIF', 'Notification Only'),
    )

    LS_STATUS = (
        ('A', 'Approved'),
        ('P', 'Pending'),
        ('F', 'Fellowship'),
        ('D', 'Denied'),
        ('S', 'TA sister approved'),
    )

    type = models.CharField(max_length=5, choices=LS_TYPES)
    status = models.CharField(max_length=1, choices=LS_STATUS, default='P')

    TA = models.ForeignKey(TrainingAssistant)
    trainee = models.ForeignKey(Trainee, related_name='%(class)s')  #trainee who submitted the leaveslip

    submitted = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    finalized = models.DateTimeField(blank=True, null=True)  # when this leave-slip was approved/denied

    description = models.TextField(blank=True, null=True)  # trainee-supplied
    comments = models.TextField(blank=True, null=True)  # for TA comments

    texted = models.BooleanField(default=False)  # for sisters only

    informed = models.BooleanField(blank=True, default=False)  # not sure, need to ask

    def _classname(self):
        # returns whether slip is individual or group
        return str(self.__class__.__name__)[:-4].lower()

    classname = property(_classname)

    def __init__(self, *args, **kwargs):
        super(LeaveSlip, self).__init__(*args, **kwargs)
        self.old_status = self.status

    def save(self, force_insert=False, force_update=False):
        #records the datetime when leaveslip is either approved or denied
        if (self.status == 'D' or self.status == 'A') and (self.old_status == 'P' or self.old_status == 'F' or self.old_status == 'S'):
            self.finalized = datetime.now()
        super(LeaveSlip, self).save(force_insert, force_update)
        self.old_status = self.status

    def __unicode__(self):
        return "[%s] %s - %s" % (self.submitted.strftime('%m/%d'), self.type, self.trainee)

    class Meta:
        abstract = True


class IndividualSlip(LeaveSlip):

    events = models.ManyToManyField(Event, related_name='leaveslip')

    def get_update_url(self):
        return reverse('leaveslips:individual-update', kwargs={'pk': self.id})

    def _late(self):
        end_date = self.events.all().order_by('-end')[0].end
        if self.submitted > end_date+timedelta(days=2):
            return True
        else:
            return False

    late = property(_late)  # whether this leave slip was submitted late or not

    def get_absolute_url(self):
        return reverse('leaveslips:individual-detail', kwargs={'pk': self.id})

    @property
    def get_start(self):  # determines the very first date of all the events
        events=self.events.all()
        start=datetime.now()
        for event in events:
            if event.start < start:
                start=event.start
        return start


class GroupSlip(LeaveSlip):

    start = models.DateTimeField()
    end = models.DateTimeField()
    trainees = models.ManyToManyField(Trainee, related_name='group')  #trainees included in the leaveslip

    def get_update_url(self):
        return reverse('leaveslips:group-update', kwargs={'pk': self.id})

    def get_absolute_url(self):
        return reverse('leaveslips:group-detail', kwargs={'pk': self.id})

    def _events(self):
        """ equivalent to IndividualSlip.events """
        return Event.objects.filter(start__gte=self.start).filter(end__lte=self.end)

    events = property(_events)
