from rest_framework import serializers
from services.models import Customservicestemplate, User, Dataclasses, Measurements, Datastreams,Customservices, Multisensors
#from django.contrib.auth.models import User


class CustomservicestemplateSerializer(serializers.ModelSerializer):
	#participant_id = serializers.ReadOnlyField(source='participant_id.id')
	class Meta:
		model = Customservicestemplate
		fields = ('id', 'title','output_type','expression')


class CustomservicesSerializer(serializers.ModelSerializer):
	participant_id = serializers.ReadOnlyField(source='participant_id.id')
	deployment_radius= serializers.FloatField(required=False)

	class Meta:
		model = Customservices
		fields = ('id', 'participant_id','deployment_center_lat', 'deployment_center_lon', 'deployment_radius', 'template_id','title')

		

class MultisensorsSerializer(serializers.ModelSerializer):
	#participant_id = serializers.ReadOnlyField(source='participant_id.id')
	class Meta:
		model = Multisensors
		fields = ('data_stream_id','custom_service_id')
		



class UserSerializer(serializers.ModelSerializer):
	#services = serializers.PrimaryKeyRelatedField(many=True, queryset=Service.objects.all(),required=False,)
	password = serializers.CharField(required=True,write_only=True)


	def create(self,validated_data):
		user = User.objects.create(
			username = validated_data['username'],
			email = validated_data['email']
		)

		user.set_password(validated_data['password'])
		user.save()
		return user
	class Meta:
		model = User
		fields = ('id', 'username','password','email')


class ClassesSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Dataclasses
		fields = ('id','data_type','unit_of_measure')

class MeasurementsSerializer(serializers.ModelSerializer):

	class Meta:
		model = Measurements
		fields = ('id','data_stream_id','gps_latitude','gps_longitude','mgrs_coordinates','value','timestamp')


class DatastreamsSerializer(serializers.ModelSerializer):
	measurements = MeasurementsSerializer(many=True)

	class Meta:
		model = Datastreams
		fields = ('id','name','data_class','creation_timestamp','last_update_timestamp','description','elevation','url','last_entry_id','device_id','reliability','accuracy','update_rate','measurements')
		 