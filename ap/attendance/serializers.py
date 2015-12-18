
from rest_framework import serializers
from .models import Roll
from accounts.models import User, Trainee
from schedules.models import Event
from leaveslips.models import LeaveSlip, IndividualSlip

class EventSerializer(serializers.ModelSerializer):
	class Meta:
		model = Event

class RollSerializer(serializers.ModelSerializer):  
    event = EventSerializer()
    class Meta:
        model = Roll

class IndividualSlipSerializer(serializers.ModelSerializer):
	class Meta:
		model = IndividualSlip

class TraineeSerializer(serializers.ModelSerializer):
    rolls = RollSerializer(many=True)
    individualslip = IndividualSlipSerializer(many=True)

    class Meta:
        model = Trainee
        fields = ('id', 'rolls', 'individualslip')


