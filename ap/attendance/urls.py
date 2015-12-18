from django.conf.urls import url, include, patterns
from django.conf import settings
from attendance import views
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'roll', views.RollViewSet)
router.register(r'trainee_roll', views.TraineeViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'submit/$', views.AttendancePersonal.as_view(), name='attendance-submit'),
]
