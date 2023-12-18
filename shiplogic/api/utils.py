from basicauth import decode
from customer.models import CustomerAPI
class customerAuthenticate(APIView):
     def authApi(self,request):
         authBasic = request.META.get('HTTP_AUTHORIZATION',None)
         if auth_basic:
             username, password = decode(auth_basic.split(" ")[1])
             try:
                 customer_api = CustomerAPI.objects.get(username=username, customer__activation_status=True)
                 if customer_api.password == password:
                     if customer_api.ipaddress != "0":
                         if not  request.META.get('HTTP_X_FORWARDED_FOR'):
                             request_ip =  request.META.get('REMOTE_ADDR').strip()
                         else:
                             request_ip =  request.META.get('HTTP_X_FORWARDED_FOR').strip()
                         ip_list    =  customer_api.ipaddress.split(",")
                         if request_ip in ip_list:
                             return customer_api
                         else:
                             return False
                     else:
                         return customer_api
             except CustomerAPI.DoesNotExist:
                 return False
         else:
             return False
                  
