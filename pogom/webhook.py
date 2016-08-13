import requests
import Queue
import logging
from threading import Thread

from .utils import get_args

log = logging.getLogger(__name__)

webhook_data_queue = Queue.Queue()
webhook_enabled = False

def send_to_webhook(message_type, message):
    data = {
        'type': message_type,
        'message': message
    }
    
    if webhook_enabled:
        webhook_data_queue.put(data)

def enable_webhook():
    global webhook_enabled
    webhook_enabled = True
    
def is_webhook_enabled():
    return webhook_enabled

class Webhook_Sender(Thread):

    def __init__(self, webhooks):
        Thread.__init__(self)
        self.webhooks = webhooks
    
    #Threaded loop to process request data from the queue 
    def run(self):
        while True:
            data = webhook_data_queue.get(block=True)
            webhook_data_queue.task_done()
            
            if self.webhooks:
                for w in self.webhooks:
                    try:
                        requests.post(w, json=data, timeout=(None, 5))
                    except requests.exceptions.ReadTimeout:
                        log.error('Response timeout on webhook endpoint %s', w)
                    except requests.exceptions.RequestException as e:
                        log.error(e)