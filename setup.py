import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

# Mapeamento dos pinos BCM para os pinos GP que você está usando
CE_PIN = 2    # GP2
CSN_PIN = 5   # GP5
SCK_PIN = 6   # GP6
MOSI_PIN = 7  # GP7
MISO_PIN = 4  # GP4

# Configuração dos pinos
GPIO.setmode(GPIO.BCM)
pipes = [[0xE8, 0xE8, 0xF0, 0xF0, 0xE1], [0xF0, 0xF0, 0xF0, 0xF0, 0xE1]]

# Configuração do SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Configuração do rádio
radio = NRF24(GPIO, spi)
radio.begin(CE_PIN, CSN_PIN)  # Usando os novos pinos CE e CSN

# Configurações básicas
radio.setPayloadSize(32)
radio.setChannel(0x76)
radio.setDataRate(NRF24.BR_1MBPS)
radio.setPALevel(NRF24.PA_MIN)
radio.setAutoAck(True)
radio.enableDynamicPayloads()
radio.enableAckPayload()

radio.openWritingPipe(pipes[0])
radio.openReadingPipe(1, pipes[1])
radio.printDetails()

def enviar_mensagem():
    message = list("Teste!")
    while len(message) < 32:
        message.append(0)
    
    radio.write(message)
    print("Mensagem enviada:", "".join(message))

def receber_mensagem():
    radio.startListening()
    
    while True:
        if radio.available():
            recebido = []
            radio.read(recebido, radio.getDynamicPayloadSize())
            print("Recebido:", "".join(map(chr, recebido)))
        time.sleep(1)

# Script de teste
def test_connection():
    try:
        print("Iniciando teste do módulo NRF24L01...")
        print("\nConexões utilizadas:")
        print("VCC  -> 3.3V")
        print("GND  -> GND")
        print(f"CE   -> GP{CE_PIN}")
        print(f"CSN  -> GP{CSN_PIN}")
        print(f"SCK  -> GP{SCK_PIN}")
        print(f"MOSI -> GP{MOSI_PIN}")
        print(f"MISO -> GP{MISO_PIN}")
        
        radio.printDetails()
        return True
    except Exception as e:
        print("Erro na conexão:", e)
        return False

if __name__ == "__main__":
    try:
        test_connection()
        print("\nIniciando envio de mensagens de teste...")
        while True:
            enviar_mensagem()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário")
    finally:
        GPIO.cleanup()
        spi.close()
