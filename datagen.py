import logging
import logging.handlers
import sys
import threading
import os
from satori.rtm.client import make_client, SubscriptionMode

reload(sys)
sys.setdefaultencoding("utf-8")

counter = 0
filename = '/home/largetext_1GB/DATAGEN_INSTANCE_' + str(sys.argv[1])


channel = "world"
endpoint = "wss://open-data.api.satori.com"
appkey = "d0e302F4CAb4C2266b8f5Fd458076056"


def main():

    counter = 0
    filepath = 'DATAGEN'

    # Rotate file after 1GB
    logger = logging.getLogger('logger')
    handler = logging.handlers.RotatingFileHandler(filename, maxBytes=1073741824, backupCount=700)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


    while True:
        with make_client(
                endpoint=endpoint, appkey=appkey) as client:

            print('Connected!')

            mailbox = []
            got_message_event = threading.Event()

            class SubscriptionObserver(object):
                def on_subscription_data(self, data):
                    for message in data['messages']:
                        mailbox.append(message)
                    got_message_event.set()

            subscription_observer = SubscriptionObserver()
            client.subscribe(
                channel,
                SubscriptionMode.SIMPLE,
                subscription_observer)


            if not got_message_event.wait(10):
                print("Timeout while waiting for a message")
                sys.exit(1)

            for message in mailbox:
		try:
                    print('Got message "{0}"'.format(message))
                    logger.info(message)
		except UnicodeDecodeError:
		    continue

if __name__ == '__main__':
    main()
