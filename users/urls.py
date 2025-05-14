from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CreateUserView

router = DefaultRouter()
router.register(r'users', CreateUserView,basename='user')

urlpatterns = [
   path('',include(router.urls))
]
