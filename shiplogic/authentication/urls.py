from django.urls import path
from .views import *

urlpatterns = [
        path("login/", LoginAPI.as_view()),
    path("generate_otp/", OtpLogin.as_view()),
    path("password_reset_otp/", PasswordresetOtp.as_view()),
    path("passwordreset/",PasswordReset.as_view()),
    path("ShowEmployee/", ShowEmployee.as_view()),
    path("CreateUpdateEmployee/",CreateUpdateEmployee.as_view()),
    path("FetchMenu/",FetchMenu.as_view()),
    path("ValidateSession/",ValidateSession.as_view()),
]


