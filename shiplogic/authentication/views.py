from django.shortcuts import render
from datetime import datetime
from email.mime import application
import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from rest_framework import generics, permissions, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from .models import *
from oauth2_provider.models import Application, AccessToken, RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes
import requests
import random
import string
from rest_framework.permissions import IsAuthenticated
from django.contrib import auth

# Create your views here.

###### for login_required  --- permission_classes = [IsAuthenticated] inside method


@authentication_classes([])
@permission_classes([])
class LoginAPI(APIView):
    def _handleLogin(self, user, request, username, password):


        hostname = request.get_host()
        if not Application.objects.filter(user=user).exists():
            appObj = Application()
            clientId = appObj.client_id
            clientSecret = appObj.client_secre
            appObj.user=user
            appObj.authorization_grant_type="password"
            appObj.client_type="confidential"
            appObj.save()
            UserSecretCredentials.objects.create(user = user, client_id = clientId, client_secret = clientSecret)
        #appObj = Application.objects.filter(user = user)
        usc = UserSecretCredentials.objects.filter(user = user)
        if usc:
            usc = usc.latest('id')
            client_id = usc.client_id
            client_secert = usc.client_secret
            #url = settings.BASE_API_URL+'/o-auth/token/'
            url = "http://"+hostname+'/o/token/'
            data_dict = {"grant_type":"password","username":username,"password":password, "client_id":client_id,"client_secret":client_secert}
            print ("oauth_request", url, data_dict)
            aa = requests.request("POST", url, data=data_dict, verify=False)
            data = json.loads(aa.text)
            print ("oauth_response", data)
            data.pop('scope', None)
            data.pop('refresh_token', None)
            if data.get("access_token", None):
                token_obj = AccessToken.objects.filter(user_id = user, token = data.get("access_token", None))
                if token_obj:
                    data["expires"] = token_obj[0].expires
                data["status"] = "success"
            return data

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        otp = request.data.get('otp',None)
        if not username and password:
            return Response({"status":"failed", "message":"Incorrect username/password!"})
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                otp_config = OtpConfig.objects.get(id = 1)
                if otp_config.daywise_otp:
                    if not otp:
                        return Response({"status":"Failed","message":"Otp required"})
                    login_otp = UserLoginOtp.objects.filter(user = user).latest('id')
                    if str(otp) == str(login_otp.otp):

                        UserLoginOtp.objects.filter(user = user).update(active_status = False)
                    else:
                        return Response({"status":"Failed","message":"Otp"})
                        
                print("-------",login(request, user))
                expire_time = datetime.now()
                token = ''

                token_obj = AccessToken.objects.filter(user_id = user, expires__gt = expire_time)
                print (token_obj)
                if token_obj:
                    token_obj = token_obj.latest('id')
                    token = token_obj.token
                    print (user, token)
                    token_obj.expres = datetime.now()
                    return Response(self._handleLogin(user, request, username, password))
                else:
                    return Response(self._handleLogin(user, request, username, password))

            else:
                return Response({"status":"failed", "message":"User deactivated!"})
        else:
            return Response({"status":"failed", "message":"Incorrect username/password!"})

class ValidateSession(APIView):
    def get(self, request):
        return Response({"status": "success", "message": "Authorized"})

class LogoutApi(APIView):
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION',None)
        print (request.user, token)
        if token:
            token = token.split(' ')[1]
            token_obj = AccessToken.objects.filter(user_id = request.user, token = token)
            if token_obj:token_obj.delete()
        logout(request)
        return Response({"status": "success", "message": "LoggedOut"})



#@authentication_classes([])
@permission_classes([])
class OtpLogin(APIView):
    def post(self,request):
        cur_date = str(datetime.now().date())
        now = datetime.now()
        resp = {}
        username = request.data.get('username')
        try:
            user = User.objects.get(username = username)
        except:
            resp['success'] = "False"
            resp['message'] = "Invalid Username"
            return Response(resp)
        emp = user.employeemaster
        mobile = emp.mobile_no
       # otp = str(random.randint(10000, 99999))
        otp = 5151
        if UserLoginOtp.objects.filter(user = user,added_on__range = [str(now.date()) + " 00:00:00",str(now.date()) + " 23:59:59"]):
            otp = int(UserLoginOtp.objects.filter(user = user,added_on__range = [str(now.date()) + " 00:00:00",str(now.date()) + " 23:59:59"]).latest('id').otp)
        else:    
            UserLoginOtp.objects.filter(user = user,active = True).update(active = False)
            UserLoginOtp.objects.create(otp = otp,user = user,)
        resp['success'] = "True"
        resp['message'] = "Otp has been sent to you number"
        resp['otp'] = otp
        return Response(resp)    



