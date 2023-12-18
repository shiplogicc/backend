from django.db import models

# Create your models here.


from django.contrib.auth.models import User
from location.models import *
#import unidecodedata


class UserSecretCredentials(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    client_id = models.CharField(max_length =250, null=True, blank=True)

    client_secret = models.CharField(max_length =250, null=True, blank=True)

    status = models.IntegerField(default=1, db_index=True)

    added_on = models.DateTimeField(auto_now_add=True, db_index=True)

    updated_on = models.DateTimeField(null=True, blank=True, db_index=True)
 


DEPARTMENT_LIST = (
        ('Account', 'Account'),
        ('Customer Service', 'Customer Service'),
        ('Customer Service Accounts', 'Customer Service Accounts'),
        ('Finance', 'Finance'),
        ('HR', 'HR'),
        ('Hub', 'Hub'),
        ('IT','IT'),
        ('Operations','Operations'),
        ('Sale', 'Sale'),
        ) 


LOGIN_CHOICES = (
    (0, "Allow Concurrent Login (Required)"),
    (0, 'False'),
    (1, 'True')
)



class Department(models.Model):
    name = models.CharField(max_length=150, choices=DEPARTMENT_LIST)
    added_on = models.DateTimeField(auto_now = True)

    def __str__(self):
       return self.name



class UserType(models.Model):
    name = models.CharField(max_length = 20,db_index = True,)
    code = models.CharField(max_length = 10,db_index = True)
    active = models.BooleanField(default = True)
    added_on = models.DateTimeField(auto_now_add = True)
    updated_on = models.DateTimeField(auto_now = True)

class EmployeeMaster(models.Model):
    user = models.OneToOneField(User, null=True, blank=True,on_delete=models.CASCADE,)
    employee_code = models.CharField(max_length=10, null=True, blank=True)
    firstname = models.CharField(max_length=60)
    lastname = models.CharField(max_length=60)
    user_type = models.ForeignKey(UserType,db_index = True,on_delete=models.CASCADE)
    email = models.CharField(max_length=100, null=True, blank=True)
    address1 = models.CharField(max_length=200, null=True, blank=True)
    address2 = models.CharField(max_length=200, null=True, blank=True)
    address3 = models.CharField(max_length=200, null=True, blank=True)
    service_centre = models.ForeignKey('location.ServiceCenter', null=True, blank=True,on_delete=models.CASCADE)
    mobile_no = models.CharField(max_length=60)
    department = models.ForeignKey(Department,on_delete=models.CASCADE,)
    login_active = models.IntegerField(max_length=2, default=0)
    staff_status = models.IntegerField(max_length=2, default=0) #0:perm, 1:temp, 2:deact
    allow_concurent_login = models.IntegerField(max_length=2, choices=LOGIN_CHOICES, null=True, blank=True, default=0)
    query_limit = models.IntegerField(max_length=5, null=True, blank=True, default=50)
    ebs = models.BooleanField(default=False)
    customer = models.ForeignKey('customer.Customer',null = True,blank = True,db_index = True,on_delete=models.CASCADE)
    api_user = models.BooleanField(default=False)
    def __str__(self):
        firstname = str(self.firstname.encode('ascii'))
        lastname = str(self.lastname.encode('ascii'))
        employee_code = str(self.employee_code.encode('ascii'))
        return firstname+"-"+lastname+"-"+employee_code

    def get_name_with_email(self):
        return str(self.firstname) + " -  " + str(self.lastname) + " - " + str(self.email)

    def get_name_with_employee_code(self):
        firstname = self.firstname.encode('ascii', 'ignore')
        lastname = self.lastname.encode('ascii','ignore')
        employee_code = self.employee_code.encode('ascii', 'ignore') if self.employee_code else ''
        return firstname + " - " + employee_code
    def save(self,*args, **kwargs):

        if not self.query_limit:
            self.query_limit = 50
        super(EmployeeMaster, self).save(*args, **kwargs)



class PasswordPeriod(models.Model):
    user = models.ForeignKey(EmployeeMaster,on_delete=models.CASCADE,)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class DisablePasswords(models.Model):
    password_pattern = models.CharField(max_length = 30, db_index = True)
    active_status    = models.BooleanField(default = True,db_index = True)
    addedOn          = models.DateTimeField(auto_now_add = True, db_index = True)
    updatedOn        = models.DateTimeField(auto_now = True, db_index = True)
    added_by         = models.ForeignKey('authentication.EmployeeMaster', db_index = True, null= True, blank = True, related_name = 'added_by',on_delete=models.CASCADE,)


class OldPasswords(models.Model):
    password_pattern = models.CharField(max_length = 200, db_index = True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,)
    addedOn          = models.DateTimeField(auto_now_add = True, db_index = True)
    updatedOn        = models.DateTimeField(auto_now = True, db_index = True)
    active_status    = models.BooleanField(default = True,db_index = True)


class UserLoginOtp(models.Model):
    otp              = models.CharField(max_length = 30, db_index = True)
    user             = models.ForeignKey(User,on_delete=models.CASCADE,)
    active    = models.BooleanField(default = True,db_index = True)
    added_on         = models.DateTimeField(auto_now_add = True, db_index = True)
    updatedOn        = models.DateTimeField(auto_now = True, db_index = True)
    resend_count     = models.IntegerField(default = 0,db_index = True)


class ResetPasswords(models.Model):
    password_pattern = models.CharField(max_length = 200, db_index = True)
    user             = models.ForeignKey(User,on_delete=models.CASCADE,)
    addedOn          = models.DateTimeField(auto_now_add = True, db_index = True)
    updatedOn        = models.DateTimeField(auto_now = True, db_index = True)
    active_status    = models.BooleanField(default = True,db_index = True)
    updated_by = models.ForeignKey(EmployeeMaster, db_index = True, null= True, blank = True,on_delete=models.CASCADE,)    
    


class EmployeeAdditionalInformation(models.Model):
    employee = models.ForeignKey(EmployeeMaster,on_delete=models.CASCADE,)
    add_info_key = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    add_info_value = models.CharField(null=True, blank=True, max_length=250, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on = models.DateTimeField(auto_now_add = True, db_index = True)
    activation_status = models.BooleanField(default = True,  db_index = True)

class OutscanEmployee(models.Model):
    employee = models.ForeignKey(EmployeeMaster, null=True, blank=True, db_index=True,on_delete=models.CASCADE,)
    present = models.BooleanField(default=True, db_index=True)
    status = models.IntegerField(default=0, db_index=True)
    intime = models.DateTimeField(db_index=True, null=True, blank=True)
    outtime = models.DateTimeField(db_index=True, null=True, blank=True)
    attendance_date = models.DateField(db_index=True, null=True, blank=True)
    added_on=models.DateTimeField(auto_now_add= True, db_index=True)
    updated_on=models.DateTimeField(db_index=True, null=True, blank=True)


class OtpConfig(models.Model):
    daywise_otp = models.BooleanField(default= False, db_index = True)
    otp_with_pass = models.BooleanField(default= False, db_index = True)



class Menu(models.Model):
    name = models.CharField(max_length = 100,db_index = True,null =False)
    code = models.CharField(max_length = 10,db_index = True,null =False)
    url = models.CharField(max_length = 100,db_index = True,null =False)
    active = models.BooleanField(default = True,db_index = True)
    icon = models.CharField(max_length = 100,db_index = True,null = True,blank = True)
    added_on=models.DateTimeField(auto_now_add= True, db_index=True)
    updated_on=models.DateTimeField(db_index=True, null=True, blank=True)
    def __str__(self):
        return self.name

class SubMenu(models.Model):
    menu = models.ForeignKey(Menu,null = False,db_index = True,on_delete=models.CASCADE)
    name = models.CharField(max_length = 100,db_index = True,null =False)
    code = models.CharField(max_length = 10,db_index = True,null =False)
    url = models.CharField(max_length = 100,db_index = True,null =False)
    active = models.BooleanField(default = True,db_index = True)
    icon = models.CharField(max_length = 100,db_index = True,null = True,blank = True)
    added_on = models.DateTimeField(auto_now_add= True, db_index=True)
    updated_on = models.DateTimeField(db_index=True, null=True, blank=True)    
    def __str__(self):
        return self.name
    

class Role(models.Model):
    name = models.CharField(max_length = 100,db_index = True,null =False)
    code = models.CharField(max_length = 10,db_index = True,null =False)
    department = models.ForeignKey(Department,null = False,db_index = True,on_delete=models.CASCADE,related_name = "department")
    usertype = models.ForeignKey(UserType,null = False,db_index = True,on_delete=models.CASCADE,related_name = 'usertype')
    added_on = models.DateTimeField(auto_now_add= True, db_index=True)
    updated_on = models.DateTimeField(db_index=True, null=True, blank=True)
    def __str__(self):
        return self.name
