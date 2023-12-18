from django.db import models
from customer.models import Customer

AWB_TYPES = [
    ('1', 'PPD'),
    ('2', 'COD'),
    ('3', 'Reverse Shipment'),
]


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-
    .
    updating ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class AirwaybillNumbers(TimeStampedModel):
    airwaybill_number = models.BigIntegerField(unique=True)
    status = models.BooleanField(default=False)#0 unused, 1 used
    

class AirwaybillCustomer(TimeStampedModel):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=AWB_TYPES, blank=True)
    quantity = models.IntegerField(default=0)
    airwaybill_number = models.ManyToManyField('AirwaybillNumbers', related_name="awbc_info")

class PPD(models.Model):
    id = models.AutoField(primary_key=True, default = 80000000)

class COD(models.Model):
    id = models.AutoField(primary_key=True)

class ReversePickup(models.Model):
    id = models.AutoField(primary_key=True, default = 50000000)

