from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1
import json
import time
from tasks import process_uploaded_file
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuraciones
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
SUBSCRIPTION_ID = "document-processing-sub"

# Inicializar el cliente de suscripción de Pub/Sub
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)


def callback(message):
    print(f"Recibido mensaje: {message}")
    try:
        data = json.loads(message.data.decode("utf-8"))
        document_id = data.get("document_id")
        if document_id:
            print(f"Procesando documento: {document_id}")
            process_uploaded_file(document_id)
            # Confirmar que el mensaje se procesó correctamente
            message.ack()
        else:
            print("El mensaje no contiene document_id")
            message.ack()  # Confirmamos de todas formas para no reprocesar
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
        # No confirmamos para que se reintente más tarde
        message.nack()


def start_subscriber():
    streaming_pull_future = subscriber.subscribe(
        subscription_path, callback=callback
    )
    print(f"Escuchando mensajes en {subscription_path}")

    try:
        # Mantenemos viva la suscripción
        while True:
            time.sleep(60)
    except Exception as e:
        streaming_pull_future.cancel()
        print(f"Error en la suscripción: {e}")


if __name__ == "__main__":
    start_subscriber()
