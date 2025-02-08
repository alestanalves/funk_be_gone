import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

# Mapeamento dos pinos
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
radio.begin(CE_PIN, CSN_PIN)

# Configurações básicas - com nomes corrigidos
radio.set_payload_size(32)  # Corrigido de setPayloadSize
radio.set_channel(0x76)     # Corrigido de setChannel
radio.set_data_rate(NRF24.BR_1MBPS)  # Corrigido de setDataRate
radio.set_pa_level(NRF24.PA_MIN)     # Corrigido de setPALevel

# Configurar endereços para escrita e leitura
radio.write_register(radio.RX_ADDR_P0, pipes[0])
radio.write_register(radio.TX_ADDR, pipes[0])

# Configurar tamanho do payload para pipe 0
radio.write_register(radio.RX_PW_P0, 32)

def enviar_mensagem():
    message = list("Teste!")
    while len(message) < 32:
        message.append(0)
    
    radio.write(message)
    print("Mensagem enviada:", "".join(message))

def receber_mensagem():
    if radio.available():
        recebido = radio.read(radio.get_payload_size())  # Corrigido de getDynamicPayloadSize
        print("Recebido:", "".join(map(chr, filter(None, recebido))))

# Script de teste
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
    
    radio.print_details()
    
    print("\nIniciando envio de mensagens de teste...")
    while True:
        enviar_mensagem()
        time.sleep(1)
        receber_mensagem()

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário")
finally:
    GPIO.cleanup()
    spi.close()
