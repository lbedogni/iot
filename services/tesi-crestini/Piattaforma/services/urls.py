from django.conf.urls import url, include
from services import views
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

# Create a router and register our viewsets with it.
router = DefaultRouter()

router.register(r'users', views.UserViewSet)

#Mostra servizi con autenticazione, ne permette la modifica
router.register(r'user/templates', views.UserTemplateViewSet)

#Mostra servizi senza autenticazione
router.register(r'templates', views.TemplateViewSet)

#Mostra tutte le classi
router.register(r'classes', views.ClassesViewSet)

#Mostra tutte le classi
router.register(r'streams', views.GeoCodingViewSet)

#Mostra tutte le classi
router.register(r'services', views.ServicesViewSet)

#Mostra tutte le classi
router.register(r'datastreams', views.DatastreamsViewSet)

#Gestione Multisensors
router.register(r'multisensors', views.MultisensorsViewSet)

router.register(r'service/streams', views.DataStreamOfService)


urlpatterns = [
    url(r'^api/register/', views.CreateUserView.as_view(),name="user"),
    url(r'^api/login/', obtain_jwt_token),
    url(r'^api/prova', views.Prova.as_view()),
    url(r'^api/', include(router.urls)),
    url(r'^', views.index, name='index'),
]