from django.db import models
from servicecenter.models import Shipment

# Create your models here.

class ShipmentEwaybill(models.Model):
    shipment = models.ForeignKey(Shipment,related_name='shipment_ewaybill',on_delete=models.CASCADE)
    ewaybill = models.CharField(max_length=20, null = True, blank = True,db_index=True)
    status = models.IntegerField(default=0, db_index=True)
    added_on=models.DateTimeField(auto_now_add = True,db_index=True)
    updated_on=models.DateTimeField(auto_now=True,null=True, blank=True)


