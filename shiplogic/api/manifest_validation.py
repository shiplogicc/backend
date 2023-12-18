from location.models import Pincode, PincodeVirtualDCMapping, AdhocCityMapping, PincodeEmbargo, PincodeEmbargoBehaviour
from servicecenter.models import PincodeEmbargoLog
from integration_services.models import ManifestAPIConfiguration
import datetime
from customer.models import CustomerAdditionalInformation
now = datetime.datetime.now()

class ManifestAPIValidation():
    def __init__(self,*args,**kwargs):
        self.customerId = kwargs.get('customerId')

    def validatePincodeVirtualDc(self,*args,**kwargs):
        self.destinationPincode = kwargs.get('destinationPincode', None)
        self.essentialProduct = kwargs.get('essentialProduct', None)
        validationResponse = (True, "")
        dest_pincode = Pincode.objects.get(pincode = self.destinationPincode)
        if self.essentialProduct and not PincodeVirtualDCMapping.objects.filter(pincode = dest_pincode, activation_status = True):
            validationResponse = False, "Deliveries on this Destination Pincode are not operational at this moment !"
        else:

            dest_dc = PincodeVirtualDCMapping.objects.filter(pincode = dest_pincode, activation_status = True).latest('id').virtual_dc
            validationResponse = True,dest_dc
        return validationResponse 

    def validateAdhocCityMapping(self,*args,**kwargs):
        self.pickupPincode = kwargs.get('pickupPincode', None)
        self.destinationPincode = kwargs.get('destinationPincode', None)
        self.essentialProduct = kwargs.get('essentialProduct', None)
        validationResponse = (True, "")
        pickupPincode = Pincode.objects.get(pincode = self.pickupPincode)
        destinationPincode = Pincode.objects.get(pincode = self.destinationPincode)
        #print pickupPincode.city, destinationPincode.city,self.customerId
        #if self.essentialProduct and not AdhocCityMapping.objects.filter(origin_city = pickupPincode.city, destination_city = destinationPincode.city, activation_status = True):
        if self.essentialProduct and not AdhocCityMapping.objects.filter(origin_city = pickupPincode.pickup_sc.city, destination_city = destinationPincode.city, activation_status = True):
            validationResponse = False, "Deliveries on this lane are not operational at this moment !"
        return validationResponse

    def validateCustomerManifest(self,*args,**kwargs):
        self.processType = kwargs.get('processType', None)
        manifestApiConf = False if ManifestAPIConfiguration.objects.filter(customer_id = self.customerId, configuration_key = self.processType,
                          configuration_value = "False") else True
        if not manifestApiConf:
            return {"success":False,"message":"We have temporarily suspended our business operations owing to the COVID-19 crisis, in accordance with law till March 31st, 2020. We regret any inconvenience caused."}
        return {"success":True,"message":"Validated"}

    def validateIoPincodeServiceability(self, *args, **kwargs):
        now = datetime.datetime.now()
        self.pickupPincode = kwargs.get('pickupPincode', None)
        self.destinationPincode = kwargs.get('destinationPincode', None)
        self.customer = kwargs.get('customer', None)
        self.essential = kwargs.get('essentials', False)
        self.awb = kwargs.get('awb', None)
        #print "EEESSS===",self.essential
        validationResponse = (True, "")
        if not Pincode.objects.filter(pincode = self.pickupPincode):
            return False, "Pickup is not operational on pincode %s at this moment !"%(self.pickupPincode)
        if not Pincode.objects.filter(pincode = self.destinationPincode):
            return False, "Delivery is not operational on pincode %s at this moment !"%(self.destinationPincode)
        pickupPincode = Pincode.objects.get(pincode = self.pickupPincode)
        destinationPincode = Pincode.objects.get(pincode = self.destinationPincode)
        pickupPincodeStatus = pickupPincode.status
        destinationPincodeStatus = destinationPincode.status
        #print "PINCODE_STATUS==",pickupPincodeStatus,destinationPincodeStatus
        pinEmbargo = False
        pinEmbStatus = 0
        custAddInfo = CustomerAdditionalInformation.objects.filter(customer = self.customer, add_info_key = "CUSTOMER_GROUP")
        custGroup = None
        if custAddInfo:
            pinEmbargo = True
            custAddInfo = custAddInfo[0]
            custGroup = custAddInfo.add_info_value
            #print "CUST_GROUP",custGroup
            pickupBeh = False
            deliveryBeh = False
            pincodeEmbargo = PincodeEmbargo.objects.filter(pincode__pincode = self.pickupPincode, activation_status = True, start_date__lte = now).order_by('start_date')
            if pincodeEmbargo:
                pincodeEmbargo = pincodeEmbargo.latest('id')
                if now.date() >= pincodeEmbargo.start_date and now.date() <= pincodeEmbargo.end_date:
                    pincodeEmbBeh = PincodeEmbargoBehaviour.objects.filter(pincode_status = pincodeEmbargo.status)
                    if pincodeEmbBeh:
                        pincodeEmbBeh = pincodeEmbBeh[0]
                        if custGroup == "G1":
                            pickupPincodeStatus = pincodeEmbBeh.g1_behaviour
                        elif custGroup == "G2":
                            pickupPincodeStatus = pincodeEmbBeh.g2_behaviour
                        elif custGroup == "G3":
                            pickupPincodeStatus = pincodeEmbBeh.g3_behaviour
                pinEmbStatus = pincodeEmbargo.status            
            pincodeEmbargo = PincodeEmbargo.objects.filter(pincode__pincode = self.destinationPincode, activation_status = True, start_date__lte = now).order_by('start_date')
            #print ("pincodeEmbargo", pincodeEmbargo)
            if pincodeEmbargo:
                pincodeEmbargo = pincodeEmbargo.latest('id')
                if now.date() >= pincodeEmbargo.start_date and now.date() <= pincodeEmbargo.end_date:
                    pincodeEmbBeh = PincodeEmbargoBehaviour.objects.filter(pincode_status = pincodeEmbargo.status)
                    if pincodeEmbBeh:
                        pincodeEmbBeh = pincodeEmbBeh[0]
                        print ("pincodeEmbBeh", pincodeEmbBeh.__dict__)
                        if custGroup == "G1":
                            destinationPincodeStatus = pincodeEmbBeh.g1_behaviour
                        elif custGroup == "G2":
                            destinationPincodeStatus = pincodeEmbBeh.g2_behaviour
                        elif custGroup == "G3":
                            destinationPincodeStatus = pincodeEmbBeh.g3_behaviour
                        if pincodeEmbargo.status == 61 and not self.essential:
                            destinationPincodeStatus = 0
                pinEmbStatus = pincodeEmbargo.status            

        #print "pickupPincode", pickupPincode, "pickupPincodeStatus", pickupPincodeStatus
        #print "destinationPincode", destinationPincode, "destinationPincodeStatus", destinationPincodeStatus
        pickupAllowed = pickupPincodeStatus in [1,2]
        delivertAllowed = destinationPincodeStatus in [1,3]
        if not pickupAllowed:
            if pinEmbargo:
                PincodeEmbargoLog.objects.create(awb = self.awb, customer = self.customer, pincode = self.pickupPincode, pincode_type = "ORG", embargo_status = pinEmbStatus, timestamp = now)
            validationResponse = False, "Pickup is not operational on pincode %s at this moment !"%(self.pickupPincode)
        if not delivertAllowed:
            if pinEmbargo:
                PincodeEmbargoLog.objects.create(awb = self.awb, customer = self.customer, pincode = self.destinationPincode, pincode_type = "DEST", embargo_status = pinEmbStatus, timestamp = now)
            validationResponse = False, "Delivery is not operational on pincode %s at this moment !"%(self.destinationPincode)
        if not pickupAllowed and not delivertAllowed:
            if pinEmbargo:
                PincodeEmbargoLog.objects.create(awb = self.awb, customer = self.customer, pincode = self.pickupPincode, pincode_type = "ORG", embargo_status = pinEmbStatus, timestamp = now)
                PincodeEmbargoLog.objects.create(awb = self.awb, customer = self.customer, pincode = self.destinationPincode, pincode_type = "DEST", embargo_status = pinEmbStatus, timestamp = now)
            validationResponse = False, "Pickup/Deliveries are not operational on pincodes %s/%s at this moment !"%(self.pickupPincode, self.destinationPincode)
        #if pickupPincode.status not in [1,2] or destinationPincode.status not in [1,3]:
        #    validationResponse = False, "Pincode I/O is not serviceable at this moment !"
        return validationResponse


    def validateAwbSeries(self,*args,**kwargs):
        self.awbNumber = kwargs.get('awbNumber', None)
        self.productType = kwargs.get('productType', None)
        validationResponse = (True, "")
        productTypeDict = {"ppd":["1","10"], "cod":["2","11"]}
        if not AirwaybillNumbers.objects.filter(airwaybill_number = self.awbNumber, awbc_info__type__in = productTypeDict.get(self.productType)):
            validationResponse = False, "Incorrect AWB Series for %s shipment !"%(self.productType)
        return validationResponse

#ManifestAPIValidation()    
