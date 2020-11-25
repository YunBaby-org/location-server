import pika, requests, json, threading, os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

GEO_URL = 'https://www.googleapis.com/geolocation/v1/geolocate?key={}'.format(os.getenv('YOUR_API_KEY'))

connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITHOST'), port=os.getenv('RABBITPORT')))
channel = connection.channel()



def callback(ch, method, properties, body):
    threading.Thread(target=getGEO, args=(method, body)).start()

def toNext(routing_key, exchange_info):
    print('--- Next ---')
    connection1 = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITHOST'), port=os.getenv('RABBITPORT')))
    channel1 = connection1.channel()

    routing_key_P = 'tracker.' + routing_key + '.event.respond.' + exchange_info['Response']
    channel1.basic_publish(exchange='tracker-event', routing_key=routing_key_P, body=str(exchange_info))
    connection1.close()

def getGEO(method, body):
    print('--- get GEO ---')
    
    exchange_info = json.loads(body)
    
    wifi_info = dict()
    wifi_info['wifiAccessPoints'] = exchange_info['Result']['Wifis']

    response = requests.post(GEO_URL, json=wifi_info)
    result = json.loads(response.text) # str -> dict

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

    toNext(method.routing_key, exchange_info)

channel.basic_consume(queue='monitor.locating-server', auto_ack=True, on_message_callback=callback)

channel.start_consuming()