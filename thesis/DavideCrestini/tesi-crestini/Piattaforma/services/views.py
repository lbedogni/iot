from django.shortcuts import render

from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.db import connection
from django.shortcuts import get_list_or_404, get_object_or_404


from services.models import Customservicestemplate,User,Dataclasses,Measurements,Datastreams,Customservices, Multisensors
from services.serializers import CustomservicestemplateSerializer, UserSerializer, ClassesSerializer,MeasurementsSerializer,DatastreamsSerializer, CustomservicesSerializer,MultisensorsSerializer


from rest_framework import generics,permissions, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import api_view, detail_route
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.generics import CreateAPIView

from permissions import IsOwnerOrReadOnly


def index(request):
    return render(request, 'app/index.html')


#Vista relativa a tutti i service_template. Ne permette solo la visualizzazione
class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides `list` and `retrieve` actions.
    """

    permission_classes = (AllowAny,)
    queryset = Customservicestemplate.objects.all()
    serializer_class = CustomservicestemplateSerializer


#Vista relativa ai service_template creati dall'utente
class UserTemplateViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Customservicestemplate.objects.all()
    serializer_class = CustomservicestemplateSerializer

    def list(self, request):
        queryset = Customservicestemplate.objects.filter(participant_id=self.request.user.id)
        serializer = CustomservicestemplateSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Customservicestemplate.objects.filter(participant_id=self.request.user.id)
        user = get_object_or_404(queryset, pk=pk)
        serializer = CustomservicestemplateSerializer(user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(participant_id=self.request.user.id)




class UserViewSet(viewsets.ModelViewSet):
    
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CreateUserView(CreateAPIView):
    model = User
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer


#Restituisce tutte le classi presenti nella tabella DataClasses
class ClassesViewSet(viewsets.ReadOnlyModelViewSet):
    
    permission_classes = (AllowAny,)
    queryset = Dataclasses.objects.all()
    serializer_class = ClassesSerializer


#Funziona che controlla che tutte le classi necessarie siano state trovate
def check_classes(checking_classes,streams):

    print "check"
    print checking_classes
    classes_copy = list(checking_classes)
    if streams is not None:
        #print streams.data
        for stream in streams.data:
            if(stream['data_class'] in classes_copy):
                classes_copy.remove(stream['data_class'])

        if len(classes_copy) == 0:
            print "ZERO"
            print classes_copy
            return True
        else:
            return False
    else:
        return False


class GeoCodingViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = (AllowAny,)
    queryset = Datastreams.objects.all()
    serializer_class = DatastreamsSerializer


    def list(self,request):
        streams_serializer = None

        classes = request.GET.getlist('classes')
        
        #Raggio espresso in kilometri
        current_radius = 0.1
        while not check_classes(classes,streams_serializer) and current_radius < 50:
            print "eseguo con raggio"
            print current_radius
            query = """SELECT ID, (6367*acos(cos(radians(%2f)) *cos(radians(GPS_latitude))*cos(radians(GPS_longitude)-radians(%2f))
                       +sin(radians(%2f))*sin(radians(GPS_latitude))))AS distance 
                       FROM Measurements
                       WHERE (ID,data_stream_id) IN (SELECT MIN(ID), data_stream_id FROM Measurements GROUP BY data_stream_id)
                       HAVING distance < %2f ORDER BY distance"""%(float(request.query_params['lat']),
                       float(request.query_params['lng']),float(request.query_params['lat']),current_radius)
 
            #Le meausurements ritornate sono solo quelle presenti nel raggio cercato
            queryset = Measurements.objects.raw(query)
            serializer = MeasurementsSerializer(queryset, many=True)

            datastreams = []

            #Seleziono gli id degli stream relativi alle misurazioni trovate precedentemente
            for measurement in serializer.data:
                datastreams.append(measurement['data_stream_id'])


            #Ritorno i datastreams comprensivi di una misurazione, per avere anche il punto in cui si trovano
            streams_queryset = Datastreams.objects.filter(pk__in=datastreams).filter(data_class__in=classes)
            streams_serializer = DatastreamsSerializer(streams_queryset,many=True)

            #Per ogni stream prendo una sola misuarazione per ridurre il carico di dati
            for stream in streams_serializer.data:
                stream['measurements'] = stream['measurements'][:1]

            current_radius = current_radius * 2

        if check_classes(classes,streams_serializer):
            return Response(streams_serializer.data)
        else:
            return Response([])



#Restituisce tutte le classi presenti nella tabella DataClasses
class DatastreamsViewSet(viewsets.ReadOnlyModelViewSet):
    
    permission_classes = (AllowAny,)
    queryset = Datastreams.objects.all()
    serializer_class = DatastreamsSerializer


#Vista relativa ai service_template creati dall'utente
class ServicesViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """

    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Customservices.objects.all()
    serializer_class = CustomservicesSerializer

    def list(self, request):
        queryset = Customservices.objects.filter(participant_id=self.request.user.id)
        serializer = CustomservicesSerializer(queryset, many=True)
        return Response(serializer.data)
    

    def retrieve(self, request, pk=None):
        queryset = Customservices.objects.filter(participant_id=self.request.user.id)
        service = get_object_or_404(queryset, pk=pk)
        serializer = CustomservicesSerializer(service)
        return Response(serializer.data)

    def perform_create(self, serializer):
        print serializer.save(participant_id=self.request.user)



class MultisensorsViewSet(viewsets.ModelViewSet):

    authentication_classes = (JSONWebTokenAuthentication,)
    permission_classes = (IsOwnerOrReadOnly,)
    queryset = Multisensors.objects.all()
    serializer_class = MultisensorsSerializer


class DataStreamOfService(viewsets.ModelViewSet):

    permission_classes = (AllowAny,)
    queryset = Datastreams.objects.all()
    serializer_class = DatastreamsSerializer

    def list(self,request):
        service = request.query_params['service']
        
        #Obbligato a fare questo perche le raw query richiedono la chiave primaria
        query = """SELECT ID
                   FROM MultiSensors JOIN DataStreams ON MultiSensors.data_stream_ID = DataStreams.ID
                   WHERE MultiSensors.custom_service_ID={}""".format(service)


        
        queryset = Datastreams.objects.raw(query)
        serializer = DatastreamsSerializer(queryset, many=True)

        #Per ogni stream prendo solo l'ultima misurazione che e' quella rilevante
        for stream in serializer.data:
                stream['measurements'] = [stream['measurements'][-1]]

        return Response(serializer.data)


#Sulla base di questa ridefinire la query che fa la ricerca delle dei sensori vicini
class Prova(APIView):
    permission_classes = (AllowAny,)

    def get(self,request):
        service = request.GET.get('id', None)
        query = """SELECT *
        FROM DataStreams
        WHERE ID={}""".format(service)

        cursor = connection.cursor()
        cursor.execute(query)

        result = cursor.fetchone()

        print result[1]
        Response(result)