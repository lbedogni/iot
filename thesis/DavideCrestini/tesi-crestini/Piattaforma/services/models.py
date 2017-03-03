from __future__ import unicode_literals

from django.db import models
import hashlib, uuid
from django.contrib.auth.models import UserManager

class User(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    username = models.CharField(max_length=16,unique=True)
    description = models.CharField(max_length=64, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=250, blank=True, null=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email',]


    objects = UserManager()

    def check_password(self,pw):
        if self.password == hashlib.sha512(pw).hexdigest():
            return True
        else:
            return False

    def set_password(self,pw):
        self.password =  hashlib.sha512(pw).hexdigest()

    @property
    def is_staff(self):
        return False

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_authenticated(self):
        return False

    class Meta:
        managed = False
        db_table = 'Participants'



class Customservicestemplate(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    participant_id = models.IntegerField(db_column='participant_ID')  # Field name made lowercase.
    output_type = models.CharField(max_length=16)
    expression = models.CharField(max_length=128)
    title = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'CustomServicesTemplate'


class Customservices(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    participant_id = models.ForeignKey(User,db_column='participant_ID')  # Field name made lowercase.
    deployment_center_lat = models.FloatField()
    deployment_center_lon = models.FloatField()
    deployment_radius = models.FloatField()
    title = models.CharField(max_length=100, blank=True, null=False)
    template_id = models.ForeignKey(Customservicestemplate,db_column='template_ID')  # Field name made lowercase.


    class Meta:
        managed = False
        db_table = 'CustomServices'




class Dataclasses(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=4)  # Field name made lowercase.
    data_type = models.CharField(max_length=16)
    unit_of_measure = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'DataClasses'


class Datastreams(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=32)
    data_class = models.CharField(max_length=4)
    creation_timestamp = models.DateTimeField()
    last_update_timestamp = models.DateTimeField()
    description = models.CharField(max_length=64, blank=True, null=True)
    elevation = models.FloatField(blank=True, null=True)
    url = models.CharField(max_length=32, blank=True, null=True)
    last_entry_id = models.IntegerField(db_column='last_entry_ID')  # Field name made lowercase.
    device_id = models.CharField(db_column='device_ID', max_length=32)  # Field name made lowercase.
    reliability = models.CharField(max_length=32)
    accuracy = models.IntegerField()
    update_rate = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'DataStreams'


class Devices(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=32)  # Field name made lowercase.
    name = models.CharField(max_length=32)
    device_type = models.CharField(max_length=8)
    participant_id = models.IntegerField(db_column='participant_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Devices'


class Measurements(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    data_stream_id = models.ForeignKey(Datastreams,related_name='measurements',db_column='data_stream_ID')  # Field name made lowercase.
    gps_latitude = models.FloatField(db_column='GPS_latitude')  # Field name made lowercase.
    gps_longitude = models.FloatField(db_column='GPS_longitude')  # Field name made lowercase.
    mgrs_coordinates = models.CharField(db_column='MGRS_coordinates', max_length=16)  # Field name made lowercase.
    value = models.FloatField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Measurements'


class Multisensors(models.Model):
    data_stream_id = models.ForeignKey(Datastreams,db_column='data_stream_ID')  # Field name made lowercase.
    custom_service_id = models.ForeignKey(Customservices,db_column='custom_service_ID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MultiSensors'
        unique_together = (('data_stream_id', 'custom_service_id'),)




class Personalservices(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    participant_id = models.IntegerField(db_column='participant_ID')  # Field name made lowercase.
    device_id = models.CharField(db_column='device_ID', max_length=32)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PersonalServices'


class Rules(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    data_class = models.CharField(max_length=4)
    validity_mgrs_area = models.CharField(db_column='validity_MGRS_area', max_length=16)  # Field name made lowercase.
    validity_mgrs_granularity = models.IntegerField(db_column='validity_MGRS_granularity')  # Field name made lowercase.
    expire_count = models.IntegerField()
    expire_time = models.IntegerField()
    sample_time = models.IntegerField()
    sample_mgrs_granularity = models.IntegerField(db_column='sample_MGRS_granularity')  # Field name made lowercase.
    stakeholder_id = models.IntegerField(db_column='stakeholder_ID')  # Field name made lowercase.
    description = models.CharField(max_length=64, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'Rules'


class Stakeholders(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Stakeholders'


class Subscriptions(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    participant_id = models.IntegerField(db_column='participant_ID')  # Field name made lowercase.
    stakeholder_id = models.IntegerField(db_column='stakeholder_ID')  # Field name made lowercase.
    data_class = models.CharField(max_length=4)

    class Meta:
        managed = False
        db_table = 'Subscriptions'
