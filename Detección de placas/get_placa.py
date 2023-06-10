import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'tesseract'
import LPR
from paho.mqtt import client as mqtt_client
import random
import time
import argparse

# Bibliotecas
import argparse

# Parser
parser = argparse.ArgumentParser()
parser.add_argument("file_name", help="Imagen a buscar del carro")
#parser.add_argument("db_path", help="Ruta de la base de datos de las placas")
args = parser.parse_args()

ruta = args.file_name #args.db_path + args.img_src

# Variables y constantes
broker = 'localhost'
port = 1883
topic = "codigoIoT/mqtt/civ/placas/"
topic2 = "codigoIoT/mqtt/civ/pluma/"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'

print ("Las rutas recibidas son: " + ruta)
def getPlaca(rutaImg):
    lpr = LPR.LPR()
    img = cv2.imread(rutaImg)
    gray = lpr.grayscale(img)
    thresh = lpr.apply_threshold(gray)
    contours = lpr.find_contours(thresh)
    canvas = np.zeros_like(img)
    candidates = lpr.filter_candidates(contours)
    canvas = np.zeros_like(img)
    #cv2.drawContours(canvas , candidates, -1, (0, 255, 0), 2)
    #plt.axis('off')
    license = lpr.get_lowest_candidate(candidates)
    canvas = np.zeros_like(img)
    #cv2.drawContours(canvas , [license], -1, (0, 255, 0), 2)
    #plt.axis('off')
    cropped = lpr.crop_license_plate(gray, license)
    #cropped2 = lpr.crop_license_plate(img, license)
    #thresh_cropped = lpr.apply_adaptive_threshold(cropped)
    clear_border = lpr.clear_border(cropped)
    final = lpr.invert_image(clear_border)
    psm = 9
    alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    options = "-c tessedit_char_whitelist={}".format(alphanumeric)
    options += " --psm {}".format(psm)  
    txt = pytesseract.image_to_string(final, config=options)
    data=txt[:2]+txt[2:5]+ txt[5:]
    return str(data)
# Conexion al broker
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, mensaje):
    #while True:
    time.sleep(1)
    msg = mensaje
    result = client.publish(topic, msg)
    time.sleep(1)
    print (result)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")

### Inicio del programa
# Buscar Rostro
print ("Buscando placa")

# df = DeepFace.find(img_path = "img1.jpg", db_path = "C:/workspace/my_db")
data_placa = getPlaca(ruta)
print ("Resultado ")
print (data_placa)
#json_view = df.to_json(orient="index")
#print ("La expresion en JSON de los resultados es: ")
#print (json_view)


# Envio
client = connect_mqtt()
client.loop_start()
publish(client, str(data_placa))