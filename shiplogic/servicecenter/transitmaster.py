#from service_centre.models import *
from location.models import TransitMasterClusterBased
from slconfig.models import HolidayMaster
import datetime
def get_expected_dod(origin, destination, pickup_date, customer=None, mode=1):
    ogroup = []
    dgroup = []
    for stmg in origin.servicecentertransitmastergroup_set.filter():
        ogroup.append(stmg.transit_master_group)

    for stmg in destination.servicecentertransitmastergroup_set.filter():
        dgroup.append(stmg.transit_master_group)

    transitmaster_cb = TransitMasterClusterBased.objects.filter(
        transit_master_orignal__in=ogroup,
        transit_master_dest__in=dgroup,
        #transit_master_orignal__in=origin.servicecentertransitmastergroup_set.filter(), 
        #transit_master_dest__in=destination.servicecentertransitmastergroup_set.filter(), 
        mode=mode, customer=customer)
    if not transitmaster_cb :
        transitmaster_cb = TransitMasterClusterBased.objects.filter(
            transit_master_orignal__in=ogroup,
            transit_master_dest__in=dgroup, 
            mode=mode)

    if transitmaster_cb:
        transitmaster_cb = transitmaster_cb[0]
        transit_duration = transitmaster_cb.duration
        cutoff_str = transitmaster_cb.cutoff_time
    else:
        transit_duration = 3
        cutoff_str = "1900"

    added_on_str  = pickup_date.strftime("%Y-%m-%d")
    cutoff = datetime.datetime.strptime(added_on_str+cutoff_str,"%Y-%m-%d%H%M")
    
    if pickup_date.time() > cutoff.time():
        transit_duration = transit_duration + 1

    print ("-------",pickup_date)
    print (datetime.timedelta(days=transit_duration))
    expected_dod = pickup_date + datetime.timedelta(days=transit_duration)
    if HolidayMaster.objects.filter(date=expected_dod.date()):
        expected_dod = expected_dod + datetime.timedelta(days=1)
    
    # check if expected_dod is a Sunday:6
    if expected_dod.weekday() == 6:
        expected_dod = expected_dod + datetime.timedelta(days=1)

    return expected_dod
