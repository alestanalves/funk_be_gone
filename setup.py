import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev
import time

# Definição dos pinos no Raspberry Pi
CE_PIN = 22      # GPIO22 (pino físico 15)
CSN_PIN = 25     # GPIO25 (pino físico 22)
SCK_PIN = 11     # SPI SCK padrão (pino físico 23)
MOSI_PIN = 10    # SPI MOSI padrão (pino físico 19)
MISO_PIN = 9     # SPI MISO padrão (pino físico 21)

# Inicialização do rádio NRF24
radio = NRF24(GPIO, spidev.SpiDev())
radio.begin(CE_PIN, CSN_PIN)

# Lista de canais para hopping
hopping_channels = [32, 34, 46, 48, 50, 52, 0, 1, 2, 4, 6, 8, 22, 24, 26, 28, 30, 74, 76, 78, 80, 82, 84, 86]
ptr_hop = 0

# Configuração inicial do GPIO
GPIO.setmode(GPIO.BCM)

def testar_pinos_nrf24():
    print("--- Testando pinos do NRF24 ---")

    # Testar pino CE
    GPIO.setup(CE_PIN, GPIO.OUT)
    GPIO.output(CE_PIN, GPIO.HIGH)
    time.sleep(0.01)
    if GPIO.input(CE_PIN) == GPIO.HIGH:
        print("Pino CE está funcionando corretamente.")
    else:
        print("Erro: Pino CE não está respondendo.")

    # Testar pino CSN
    GPIO.setup(CSN_PIN, GPIO.OUT)
    GPIO.output(CSN_PIN, GPIO.HIGH)
    time.sleep(0.01)
    if GPIO.input(CSN_PIN) == GPIO.HIGH:
        print("Pino CSN está funcionando corretamente.")
    else:
        print("Erro: Pino CSN não está respondendo.")

    print("--- Teste de pinos concluído ---\n")

def testar_comunicacao_spi():
    print("--- Testando comunicação SPI ---")

    # Configurar SPI
    spi = spidev.SpiDev()
    spi.open(0, 0)  # Bus 0, device 0 (pinos padrão)
    spi.max_speed_hz = 8000000

    # Enviar um valor de teste e verificar a resposta
    test_value = [0xAA]
    response = spi.xfer2(test_value)

    if response[0] != 0:
        print("Comunicação SPI verificada com sucesso.")
        print(f"Valor retornado: 0x{response[0]:02X}")
    else:
        print("Erro na comunicação SPI. Verifique os pinos MOSI, MISO e SCK.")

    spi.close()
    print("--- Teste de comunicação SPI concluído ---\n")

def testar_comunicacao_rf24():
    print("--- Testando comunicação com o NRF24 ---")
    if radio.is_chip_connected():
        print("O chip NRF24 está conectado e respondendo corretamente.")
    else:
        print("Erro: O chip NRF24 não está respondendo corretamente.")
    print("--- Teste de comunicação 
