import time
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883

TOPIC_STATUS = "iot/device/status"
TOPIC_DATA_RETAIN = "iot/device/temperature"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("\n[Subscriber] Conectado ao broker! Aguardando tópicos...")
        # Inscreve-se nos tópicos quando realiza ou refaz a conexão.
        client.subscribe([(TOPIC_STATUS, 1), (TOPIC_DATA_RETAIN, 0)])
        print(f"[Subscriber] Inscrito em: '{TOPIC_STATUS}' e '{TOPIC_DATA_RETAIN}'\n")
    else:
        print(f"[Subscriber] Falha na conexão. Error {rc}")

def on_message(client, userdata, msg):
    try:
        # Pega a mensagem binária e encoda no formato string tradicional
        payload_str = msg.payload.decode('utf-8')
        
        # msg.retain é True quando essa mensagem já estava retida em memória no
        # broker MQTT antes mesmo do código (subscriber) subir/reconectar.
        # Caso chegue false, ela foi postada há meros milisegundos nesse instante.
        is_retained = bool(msg.retain)
        retain_tag = "[MENSAGEM RETIDA DO BROKER]" if is_retained else "[RECEBIMENTO EM TEMPO REAL]"
        
        print(f" > Novo Log '{msg.topic}' | {retain_tag}")
        print(f"     => Valor: {payload_str}")

        # Identificando o LWT
        if "OFFLINE (Abrupt Disconnect)" in payload_str:
            print("     [ !! LWT DISPARADO PELO BROKER !! ] - O dispositivo morreu sem aviso prévio/graceful shutdown.")
            
    except Exception as e:
        print(f"[Subscriber] Erro de processamento na msg: {e}")

def run_subscriber():
    # Cria o client (para simular backend server de consumo de IoT)
    client = mqtt.Client(client_id="Backend_Subscriber_App_01", clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message

    print("[Subscriber] Solicitando conexão...")
    client.connect(BROKER, PORT, keepalive=60)

    # Inicia e segura na thread processando as msgs MQTT
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n[Subscriber] Fechando o app (Ctrl+C). Desconectando normalmente...")
        client.disconnect()

if __name__ == "__main__":
    run_subscriber()
