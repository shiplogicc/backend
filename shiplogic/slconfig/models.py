from django.db import models

class Mode(models.Model):
    mode = models.IntegerField(max_length=1)
    name = models.CharField(max_length=50)

class ShipmentStatusMaster(models.Model):
    code = models.IntegerField(max_length=5)
    code_description = models.CharField(max_length=200)
    code_redirect = models.IntegerField(null=True, blank=True)
    closure_code = models.BooleanField(default=False)
    parent_code = models.CharField(max_length=5)
    parent_description = models.CharField(max_length=200)
    updation_mode = models.CharField(max_length=10)
    attributed_to = models.CharField(max_length=10)
    failure_off = models.CharField(max_length=10)
    active_status = models.IntegerField(default=1, db_index=True)
    rad_allowed = models.BooleanField(default=True, db_index=True)
    def __unicode__(self):
        return str(self.code) + " - " + self.code_description

    class Meta:
        ordering = ["code"]


class HolidayMaster(models.Model):
    date=models.DateField()
    name=models.CharField(max_length=50)
    description=models.CharField(max_length=300, null=True, blank=True)
