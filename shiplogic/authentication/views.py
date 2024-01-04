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
from rest_framework import status
from rest_framework.authtoken.models import Token
import requests
import random
import string
from rest_framework.permissions import IsAuthenticated
from django.contrib import auth
import jsonschema
from jsonschema import validate
from api.utils import validateJsonSchema
from django.forms.models import model_to_dict
from django.db import IntegrityError
from django.db.models import Q



######### Write your schemas here



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


@authentication_classes([])
@permission_classes([])
class PasswordresetOtp(APIView):
    def post(self,request):
        ResetOtpSchema = JsonSchema.objects.get(name = "ResetOtpSchema").schema
        validate,message = validateJsonSchema(request.data,ResetOtpSchema)
        if not validate == True:
            return Response({"status":"False","message":message})

        
        cur_date = str(datetime.now().date())
        now = datetime.now()
        resp = {}
        username = request.data.get('username')
        request_type = request.data.get('request_type')
       
        try:
            user = User.objects.get(username = username)
        except:
            resp['status'] = "False"
            resp['message'] = "Invalid Username"
            return Response(resp)
        emp = user.employeemaster
        mobile = emp.mobile_no
       # otp = str(random.randint(10000, 99999))
        otp = 5151
        if request_type == "fetch_otp":
            if PasswordResetOtp.objects.filter(user = user,added_on__range = [str(now.date()) + " 00:00:00",str(now.date()) + " 23:59:59"]):
                otp = int(PasswordResetOtp.objects.filter(user = user,added_on__range = [str(now.date()) + " 00:00:00",str(now.date()) + " 23:59:59"]).latest('id').otp)
            else:
                PasswordResetOtp.objects.filter(user = user,active = True).update(active = False)
                PasswordResetOtp.objects.create(otp = otp,user = user,)
            resp['status'] = "True"
            resp['message'] = "Password Reset Otp has been sent to you number"
            resp['otp'] = otp
            return Response(resp)    
        if request_type == "verify_otp":
            otp = request.data.get('otp')
            if not otp:  
                resp['status'] = "False"
                resp['message'] = "Password Reset Otp is required"
                return Response(resp)
            if PasswordResetOtp.objects.filter(user = user,active = True): 
                if int(PasswordResetOtp.objects.filter(user = user,active = True).latest('id').otp) == int(otp): 
                    PasswordResetOtp.objects.filter(user = user,active = True).update(active = False)
                    resp['status'] = "True"
                    resp['message'] = "Password Reset Otp has been verified "
                    return Response(resp)
                else:
                    resp['status'] = "False"
                    resp['message'] = "Password Reset Otp is Invalid "
                    return Response(resp)
            else:
                resp['status'] = "False"
                resp['message'] = "Please fetch otp first"
                return Response(resp)








@authentication_classes([])
@permission_classes([])
class PasswordReset(APIView):
    def post(self,request):
        PasswordResetSchema = JsonSchema.objects.get(name = "PasswordResetSchema").schema
        validate,message = validateJsonSchema(request.data,PasswordResetSchema)
        if validate == False:
            return Response({"success":"False","message":message})

        resp_dict = {}
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username = username)
        except:
            resp_dict['success'] = "False"
            resp_dict['message'] = "Invalid Username"
            return Response(resp_dict)
        user.set_password(password)
        user.save()
        resp_dict['success'] = "True"
        resp_dict['message'] = "Password Is updated"
        return Response(resp_dict)


class ShowEmployee(APIView):
    def post(self,request):
        resp_dict = {}
        emp_data = []
        employee = EmployeeMaster.objects.filter()
        for emp in employee:
            employee_details = model_to_dict(emp)
            emp_data.append(employee_details)
         
        resp_dict['success'] = "True"
        resp_dict['employee_data'] = emp_data
        return Response(resp_dict)
    


class CreateUpdateEmployee(APIView):
    def post(self,request):
        resp_dict = {}
        emp_data = []
        error_data = []
        emp_json = request.data.get('emp_json')
        request_type = request.data.get('request_type')
        for emp in emp_json:
            EmployeeCreateSchema = JsonSchema.objects.get(name = "EmployeeCreateSchema").schema
            validate,message = validateJsonSchema(emp,EmployeeCreateSchema)
            if validate == False:
                error_data.append(message)
                continue
            emp_details = {}
            email = emp['email']
            mobile = emp['mobile_no']
            employee_code = emp['employee_code']
            employee = EmployeeMaster.objects.filter(email = email,mobile_no = mobile )
            if not employee:
                usr = User.objects.filter(username = email,email = email)
                if usr:
                    emp_details['success'] = "False"
                    emp_details['message'] = "User with same email already exist"
                    error_data.append(emp_details)
                    continue
                if EmployeeMaster.objects.filter(employee_code = employee_code ):
                    emp_details['success'] = "False"
                    emp_details['message'] = "Employee with similar employee code already exist."
                    error_data.append(emp_details)
                    continue
                employee = EmployeeMaster.objects.create(**emp)

                password = ''.join(random.choice(string.ascii_lowercase+string.digits)for _ in range(10))
                usr = User.objects.create_user(username=email,email=email,password=password)
                employee.user = usr
                employee.save()
                
                emp_details['success'] = "True"
                emp_details['message'] = "Employee successfully created"
                emp_data.append(emp_details)
                continue
            else:
                employee = EmployeeMaster.objects.filter(email = email)
                employee.update(**emp)
                emp_details['success'] = "True"
                emp_details['message'] = "Employee successfully updated"
                emp_data.append(emp_details)

                continue
        resp_dict['success'] = "True"
        resp_dict['success_data'] = emp_data
        resp_dict['error_data'] = error_data
        return Response(resp_dict)



class FetchMenu(APIView):
    def post(self,request):
        resp_dict = {}
        emp = request.user.employeemaster
        department = emp.department
        user_type = emp.user_type
        role = Role.objects.filter(department = department,usertype = user_type)
        sub_menu_data = []
        menu_data = []
        menu_ids = role.latest('id').sub_menu.filter(active = True,menu__active = True).values_list('menu_id',flat = True)
        sub_menu_ids = role.latest('id').sub_menu.filter(active = True).values_list('id',flat = True)
        for menu in Menu.objects.filter(id__in = menu_ids):
            menu_details = {}
            menu_details['name'] = menu.name
            menu_details['code'] = menu.code
            menu_details['icon'] = menu.icon
            menu_details['url'] = menu.url
            sub_menu = menu.submenu_set.filter(active = True,id__in = sub_menu_ids)
            for sub in sub_menu:
                sub_menu_details = {}
                sub_menu_details['name'] = sub.name
                sub_menu_details['code'] = sub.code
                sub_menu_details['icon'] = sub.icon
                sub_menu_details['url'] = sub.url
                sub_menu_data.append(sub_menu_details)
            menu_details['sub_menu_data'] = sub_menu_data
            menu_data.append(menu_details)
        resp_dict['success'] = "True" 
        resp_dict['data'] = menu_data

         
        return Response(resp_dict)


class SearchEmployee(APIView):
    def get(self,request):
        resp_dict = {}
        q = Q()
        employee_code = request.GET.get('ec')
        mobile = request.GET.get('mn')
        email = request.GET.get('em')
        name = request.GET.get('nm')
        q = q & Q ()
        return Response({})


