import jsonschema
from jsonschema import validate
from servicecenter.models import Shipment,ShipmentHistory
from django.apps import apps
import datetime
now = datetime.datetime.now()
def validateJsonSchema(data,jsonSchema):

    try:
        validate(instance = data, schema = jsonSchema)
        return True,""

    except jsonschema.exceptions.ValidationError as err:
        exceptionField = ','.join(str(field) for field in err.path)
        field_name = ''
        if err.path:
            field_name = " for field_name {0}".format(err.path.pop())
        message = err.message + field_name
        return False,message

def history_update(shipment, __status, request, remarks="", reason_code=None):
    now = datetime.datetime.now()
    employee_code = request.user.employeemaster
    current_sc = request.user.employeemaster.service_centre
    remarks = remarks
    #upd_time = shipment.added_on
    #monthdir = upd_time.strftime("%Y_%m")
    #shipment_history = apps.get_model('service_centre', 'ShipmentHistory_%s'%(monthdir))
    ship_hist = ShipmentHistory.objects.create(
        shipment=shipment, status=__status, employee_code=employee_code,
        current_sc=current_sc, expected_dod=shipment.expected_dod,
        reason_code=reason_code, remarks=remarks,added_on = datetime.datetime.now(),updated_on = datetime.datetime.now(),partition_month=shipment.added_on)

    Shipment.objects.filter(airwaybill_number=shipment.airwaybill_number).update(updated_on=now)

