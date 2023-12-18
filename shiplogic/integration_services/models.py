from django.db import models
from customer.models import *

class ManifestAPIConfiguration(models.Model):
    configuration_key = models.CharField(null=True, blank=True, max_length = 100, db_index = True)
    configuration_value = models.CharField(null=True, blank=True, max_length = 250, db_index = True)
    customer = models.ForeignKey(Customer, blank = True, null = True, db_index = True,on_delete=models.CASCADE)
    status = models.IntegerField(default = 1, db_index = True)
    added_on = models.DateTimeField(auto_now_add = True, db_index = True)
    updated_on = models.DateTimeField(auto_now = True, db_index = True)
    def __unicode__(self):
        return self.configuration_key+" - "+self.configuration_value

