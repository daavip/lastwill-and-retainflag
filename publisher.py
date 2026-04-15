import time
import sys
import paho.mqtt.client as mqtt

BROKER = "test.mosquitto.org"
PORT = 1883

TOPIC_STATUS = "iot/device/status"
TOPIC_DATA_RETAIN = "iot/device/temperature"

# Callback executado quando o cliente recebe confirmação de conexão do broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[Publisher] Conectado ao broker MQTT com sucesso.")
    else:
        print(f"[Publisher] Falha ao conectar. Código de erro: {rc}")

def run_demonstration():
    # Inicializa o cliente simulando um dispositivo de IoT (ex: Raspberry, ESP32)
    client = mqtt.Client(client_id="Device_IoT_Sensors_01")
    client.on_connect = on_connect

    # -----------------------------------------------------
    # 1. Configurando o Last Will and Testament (LWT)
    # -----------------------------------------------------
    # Aqui, ANTES DE CONECTAR, dizemos ao Broker:
    # "Se eu perder a conexão abruptamente (sem enviar disconnect), publique 
    # a mensagem abaixo." Note o retain=True para quem assinar o tópico mais tarde
    # saber que o dispositivo terminou de uma forma anormal (está offline).
    mensagem_lwt = "OFFLINE (Abrupt Disconnect)"
    print(f"\n[Publisher] Configurando LWT para o tópico: {TOPIC_STATUS}")
    client.will_set(TOPIC_STATUS, payload=mensagem_lwt, qos=1, retain=True)

    print("[Publisher] Solicitando conexão com Keep Alive de 5 segundos...")
    # Conecta-se. O keepalive baixo ajuda a simulação a ser rápida (o broker 
    # perceberá que o cliente caiu porque ele vai parar de enviar 'pings').
    client.connect(BROKER, PORT, keepalive=5)

    client.loop_start() # Começa thread de monitoramento da conexão e mensagens recebidas
    time.sleep(2) # Aguardando que a conexão seja finalizada adequadamente...

    # -----------------------------------------------------
    # 2. Publicando Estado Inicial (Retain)
    # -----------------------------------------------------
    # Como entramos na rede com sucesso, avisamos que estamos ONLINE. Se configurarmos
    # com o Retain Flag igual a True, outros softwares do backend não precisam estar
    # online agora. Eles podem olhar depois qual é o Status mais "atual" do sensor.
    print(f"[Publisher] Publicando estado normal (ONLINE) em '{TOPIC_STATUS}'...")
    client.publish(TOPIC_STATUS, "ONLINE", qos=1, retain=True)

    time.sleep(1)

    # -----------------------------------------------------
    # 3. Publicando Exemplo de Dado (Retain Flag)
    # -----------------------------------------------------
    # Queremos que um painel leia a última temperatura válida do dispositivo
    # instantaneamente, mesmo que o dispositivo só poste temperatura a cada 10 min.
    temp_val = "25.4"
    print(f"[Publisher] Publicando temperatura = {temp_val} em '{TOPIC_DATA_RETAIN}' (Retain=True)")
    client.publish(TOPIC_DATA_RETAIN, f"Temperature: {temp_val} C", qos=0, retain=True)

    time.sleep(2)

    # -----------------------------------------------------
    # 4. Simulando Desconexão Anormal (Trigger LWT)
    # -----------------------------------------------------
    print("\n-----------------------------------------------------")
    print("[Publisher] ATENÇÃO: Simulando que o sensor caiu da rede / morreu.")
    print("O script será encerrado forçadamente em 3 segundos, simulando um corte de energia.")
    print("O broker Mosquito vai parar de receber ping-backs (KeepAlive) e acionará o LWT.")
    print("Aguarde e observe o terminal do subscriber!")
    print("-----------------------------------------------------\n")
    time.sleep(3)
    
    # Ao fechar pelo sys.exit(1) passamos direto por sem chamar client.disconnect(). 
    # O broker aciona a inteligência de queda do LWT de acordo.
    sys.exit(1)

if __name__ == "__main__":
    run_demonstration()
