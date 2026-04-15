Integrantes:
Amanda Acosta de Andrade - 1956912

Davi Pelloso - 1976516
# MQTT: Last Will Testament (LWT) e Retain Flag

Este repositório contém explicações e exemplos práticos dos conceitos de **Last Will Testament (LWT)** e **Retain Flag** no protocolo MQTT.

## 1. Last Will e Testament (LWT)

O **Last Will Testament** (Testamento Final) é uma funcionalidade que permite a um cliente MQTT especificar, no momento da conexão, uma mensagem no broker. Se esse cliente for desconectado de forma inesperada (ex: queda de energia, cabo rompido, perda de conexão celular), o broker se encarregará de publicar automaticamente essa mensagem.

### Quando Usar
- **Monitoramento de estado (Presence):** Saber de forma eficaz quais dispositivos em uma rede estão online ou offline.
- **Sistemas de alerta crítico:** Ser notificado imediatamente caso um sensor crítico no campo pare de enviar dados e saia da rede subitamente.
- **Failover / Resiliência:** Permitir que o sistema maior saiba que um nó falhou e que outras rotinas (como enviar um comando de reinício, ou transferir carga para outro nó) devem ser ativadas.

### Impactos no Sistema IoT Real
- **Confiabilidade Reativa:** Permite que o backend aja no exato momento (após o timeout de *keep_alive*) que a comunicação cessa incorretamente, reduzindo o tempo que o sistema fica "cego" diante de um hardware travado.
- **Redução de Tráfego:** Uma alternativa pior seria o servidor enviar pacotes constantemente pingando o dispositivo ("você está aí?"). O LWT centraliza essa lógica no broker via *keep_alive* da conexão TCP, poupando bateria nos devices e banda na rede - algo em extrema falta em IoT.

---

## 2. Retain Flag

A **Retain Flag** (Sinalizador de Retenção) é uma configuração definida na publicação de uma mensagem. Quando habilitada (True), pede ao broker MQTT para armazenar aquela mensagem específica em memória, associada àquele tópico. Quando um novo assinante (subscriber) se conectar posteriormente ao tópico, o broker envia instantaneamente a "última mensagem conhecida" marcada com retain.

### Quando Usar
- **Último Estado Válido:** Leituras intermitentes, onde o valor continua valendo. Exemplo: um sensor de temperatura ambiente que envia dados só a cada 3 horas. Com retain, se você abre o Dashboard da sua casa após 1 hora da última medição, verá a última temperatura lida instantaneamente, sem ter que aguardar a próxima leitura dali a 2 horas.
- **Atributos estáticos e Configuração:** Onde a planta ou infraestrutura publica configurações que os sensores/endpoints leem assim que fazem *boot*.
- **Combinação com LWT:** É muito comum LWT ser enviado com retain. Se eu perdi conexão, a mensagem LWT "Estou OFFLINE" vai ser enviada aos assinantes agora, mas TAMBÉM ficará retida para alertar a qualquer novo assinante que entrar amanhã que o sensor está OFFLINE.

### Impactos no Sistema IoT Real
- **Experiência Imediata no Frontend:** Sistemas, aplicativos e dashboards montam os layouts instantaneamente assumindo em tempo real o último estado (a luz está verde, a bomba de água está desligada, a bateria está em 80%), mantendo fluidez.
- **Custos de Memória em Brokers:** Deixar todas as mensagens com retain em um sistema gigante força o broker MQTT a gastar muita RAM, pois as mensagens ficam cravadas dependendo da configuração. Em nuvens de hiper-escala com milhões de terminais enviando mensagens com retain, isso aumenta os custos substancialmente. Usa-se com sabedoria, focando em mensagens de "estado" e não em eventos de streaming rápidos (como "velocidade do carro variando").

---

## Estrutura deste Repositório e Prática

Neste projeto demonstramos, em linguagem Python:
* `publisher.py` (Dispositivo que configura o LWT e simula ficar OFFLINE caindo repentinamente, além de publicar tópicos de temperatura usando Retain).
* `subscriber.py` (O Backend que consome os tópicos, identificando quais mensagens já chegaram de forma retida e acompanhando a queda do publisher via LWT).

### Como Simular

**Trabalhando com o pacote paho-mqtt:**
Sugiro a versão `1.6.1` por possuir retrocompatibilidade com a vasta maioria das aplicações de tutorial.
```bash
pip install -r requirements.txt
```

**Passo a passo:**
1. Abra um terminal e rode o código do consumidor:
```bash
python subscriber.py
```
2. Abra um **segundo** terminal e inicie o dispositivo produtor:
```bash
python publisher.py
```

Observe que no terminal do *subscriber* haverá confirmações em tempo real e após a quebra abrupta do processo *publisher*, ele identificará o recebimento do Last Will & Testament (LWT) configurado na largada. Feche o subscriber e rode de novo em seguida, você notará a mensagem com retain flag aparecendo sem que o publicador precise ter enviado nada!
