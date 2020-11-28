import pika, requests, json, threading, os,logging
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

GEO_URL = 'https://www.googleapis.com/geolocation/v1/geolocate?key={}'.format(os.getenv('YOUR_API_KEY'))


def callback(ch, method, properties, body):
    threading.Thread(target=getGEO, args=(method, body)).start()

def toNext(routing_key, exchange_info):
    global channel
    routing_key_P = 'tracker.' + routing_key + '.event.respond.' + exchange_info['Response']
    
    #   publish message is JSON format not str
    channel.basic_publish(exchange='tracker-event', routing_key=routing_key_P, body=json.dumps(exchange_info))
    logging.info('transfer result to tracker-event & RK: '+str(routing_key_P))
    logging.info(exchange_info)


def getGEO(method, body):

    
    exchange_info = json.loads(body)
  
    wifi_info = dict()
    wifi_info['wifiAccessPoints'] = exchange_info['Result']['Wifis']

    
    response = requests.post(GEO_URL, data=json.dumps(wifi_info))
    result = json.loads(response.text) # str -> dict
    logging.info('geolocation result ',result['location'])
    if result.get('location'):
        exchange_info['Response'] = 'ScanWifiSignal_Resolved'
        exchange_info['Result']['Longitude'] = result['location']['lng']
        exchange_info['Result']['Latitude'] = result['location']['lat']
        exchange_info["Result"]["Radius"] = result["accuracy"]
    elif result.get('error'):
        exchange_info['Response'] = 'ScanWifiSignal_Resolved_Failure'
        exchange_info['Result']['errors'] = result['error']['errors']
        exchange_info['Result']['code'] = result['error']['code']
        exchange_info["Result"]["message"] = result['error']['message']
    logging.info('---------------------------------')
    
    toNext(method.routing_key,exchange_info)



if __name__ == '__main__':
    #   init coneection 
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITHOST'), port=os.getenv('RABBITPORT')))
    channel = connection.channel()

    logging.getLogger().setLevel(logging.INFO)

    channel.basic_consume(queue='monitor.locating-server', auto_ack=True, on_message_callback=callback)
    logging.info('--------Location Server Start Consume Message--------')

    #   start consuming 
    channel.start_consuming()