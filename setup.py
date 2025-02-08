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

# Configurações básicas
radio.set_payload_size(32)
radio.set_channel(0x76)
radio.set_data_rate(NRF24.BR_1MBPS)
radio.set_pa_level(NRF24.PA_MIN)

# Configurar endereços para escrita e leitura
radio.write_register(radio.RX_ADDR_P0, pipes[0])
radio.write_register(radio.TX_ADDR, pipes[0])

# Configurar tamanho do payload para pipe 0
radio.write_register(radio.RX_PW_P0, 32)

def enviar_mensagem():
    try:
        # Criando a mensagem como lista de bytes
        message = [ord(c) for c in "Teste!"]
        
        # Verificação de tamanho
        if len(message) > 32:
            print("Aviso: Mensagem truncada para 32 bytes")
            message = message[:32]
        else:
            # Preenchendo o resto do payload com zeros
            message.extend([0] * (32 - len(message)))
        
        # Verificação de valores
        for i, val in enumerate(message):
            if not isinstance(val, int):
                message[i] = 0
                print(f"Aviso: Valor inválido na posição {i}")
        
        # Debug - mostra os valores antes do envio
        print("Valores hexadecimais:", [hex(x) for x in message])
        print("Valores decimais:", message)
        
        # Envio da mensagem
        radio.write(message)
        print("Mensagem enviada:", "".join(chr(x) for x in message if x != 0))
        
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def receber_mensagem():
    if radio.available():
        # Lendo a mensagem
        recebido = radio.read(radio.get_payload_size())
        # Convertendo bytes para string, removendo zeros
        mensagem = "".join(chr(x) for x in recebido if x != 0)
        print("Recebido:", mensagem)

# Script principal
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
except Exception as e:
    print(f"Erro: {e}")
finally:
    GPIO.cleanup()
    spi.close()
