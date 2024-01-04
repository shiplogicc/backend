from track_me.models import CustomerNdrConcerns,CustomerNdrResolutionMaster,CallCentreComment,CallCentreCommentResolution
from servicecenter.models import Shipment,ShipmentHistory,ShipmentStatusUpdate
from slconfig.models import ShipmentStatusMaster
import datetime
def callcentre_comment_entry(emp_code,current_sc,awb,concern,solution,comments=None,delivery_date=None,cust_code=None):
    
    errors = []
    hist_status = 21
    try:
        reason_code=None
        if cust_code:
            cust_code = [cust_code]

        if cust_code:
            shipment = Shipment.objects.filter(airwaybill_number=int(awb),shipper__code__in = cust_code, rts_status=0,product_type__in=['cod','ppd'])
            hist_status=84
        else:
            shipment = Shipment.objects.filter(airwaybill_number=int(awb))
        if shipment:
            shipment = shipment.order_by('-id')[0]

            statusupdate = ShipmentStatusUpdate.objects.filter(shipment=shipment)
            if statusupdate:
                statusupdate = statusupdate.order_by('-id')[0]
                if statusupdate:
                    reason_code = statusupdate.reason_code
                else:
                    reason_code = None

            concern = CustomerNdrConcerns.objects.filter(description=concern)
            if concern:
                concern = concern.order_by('-id')[0]
            else:
                errors.append({'awb':shipment.airwaybill_number,'success':False,'reason':'Invalid concern :{0}'.format(concern)})

            solution = CustomerNdrResolutionMaster.objects.filter(description=solution,concern=concern)
            if solution:
                solution = solution.order_by('-id')[0]

            else:
                errors.append({'awb':shipment.airwaybill_number,'success':False,'reason':'Invalid solution :{0}'.format(solution)})
                


        if errors:
            return False,errors

        remarks = ''
        if comments:
            remarks += "concern was: "+concern.description+". Solution is: "+solution.description+". Comments are: "+comments 
        else:
            remarks += "concern was: "+concern.description+". Solution is: "+solution.description
        if delivery_date!=None:
            remarks+='. Scheduled delivery date: '+delivery_date+' -'

    
        delivery_date = datetime.datetime.strptime(delivery_date,"%Y-%m-%d")
        if solution.reasoncode:
            if solution.reasoncode.code == 1224 and shipment.additional_shipment.filter(add_info_key='SELF_COLLECT', add_info_value = 'YES'):
                return {'status':True}
            if solution.reasoncode.code == 1224:
                reason = ShipmentStatusMaster.objects.get(code=12244)
                ShipmentHistory.objects.create(shipment=shipment,employee_code=emp_code,status=hist_status,current_sc=current_sc,
                    remarks=remarks,reason_code=reason,added_on = datetime.datetime.now(),updated_on = datetime.datetime.now(),partition_month=shipment.added_on)
                shipment.reason_code = reason
                shipment.save()
            else:
                reason = solution.reasoncode
                ShipmentHistory.objects.create(shipment=shipment,employee_code=emp_code,status=hist_status,current_sc=current_sc,
                    remarks=remarks,reason_code=solution.reasoncode,added_on = datetime.datetime.now(),updated_on = datetime.datetime.now(),partition_month=shipment.added_on)
                shipment.reason_code=solution.reasoncode
                shipment.save()
            call_centre_comment = CallCentreComment.objects.create(employee_code=emp_code,date=datetime.datetime.now().date(),
                shipments=shipment,comments=comments)
            cc_comment = CallCentreCommentResolution.objects.create(call_centre_comment=call_centre_comment,resolution=solution,
                scheduled_delivery_date=delivery_date,concern=concern,undelivered_reasoncode=reason_code)
            cc_comment.reason_code = reason
            cc_comment.save()
        else:
            ShipmentHistory.objects.create(shipment=shipment,employee_code=emp_code,status=hist_status,current_sc=current_sc,remarks=remarks,added_on = datetime.datetime.now(),updated_on = datetime.datetime.now(),partition_month=shipment.added_on)


    except Exception as e:
        error = [{'awb':awb,'success':False,'reason':str(e)}]
        return False,error

    return True,""
