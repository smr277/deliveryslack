import requests
import json 
from tinydb import TinyDB, Query
import deliveryslack as ds

class Package():
    def __init__(self, tracking_num, sender):
        self.tracking_num = tracking_num
        #status of the package
        self.status = None
        #Estimated delivery date
        self.est_delivery = None
        #if status changed, and hasn't printed yet, true. else false. 
        self.need_to_print = True
        #sender
        self.sender = sender
        #Time since it's been delivered
        # self.time_since_delivered

    def check(self):
        url = 'http://api.boxoh.com/v2/rest/key/{}/track/{}'.format(ds.BOXOH_TOKEN,self.tracking_num)
        r = requests.get(url)
        j_data = r.json()
        data = j_data['data']
        old_status = self.status
        self.status = None if data['shipmentStatus'] == 'error' else data['shipmentStatus']
        self.need_to_print = (old_status != self.status)
        delivery = None if data['deliveryEstimate'] == 'error' else data['deliveryEstimate']
        if delivery:
            self.est_delivery = datetime.fromtimestamp(int(delivery))

    def print_changed_status(self):
        if self.need_to_print:
            self.need_to_print = False
            return self.__str__()
        else:
            return None

    def __eq__(self, other):
        return self.tracking_num == other.tracking_num

    def __str__(self):
        return '*Package from:* {} \n \t *Tracking:* {} \n \t *Status:* {} \n \t *Estimated date:* {} \n'.format(self.sender, self.tracking_num, self.status, self.est_delivery)
