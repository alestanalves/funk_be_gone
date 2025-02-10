import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev
import time

# Configuração
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Definição dos pinos
CE_PIN = 22    # GPIO 22 - Chip Enable
CSN_PIN = 5    # GPIO 5 - Chip Select
SCK_PIN = 11   # GPIO 11 - SCK
MOSI_PIN = 10  # GPIO 10 - MOSI
MISO_PIN = 9   # GPIO 9 - MISO

# Inicialização SPI e rádio NRF24
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 8000000
radio = NRF24(GPIO, spi)
radio.begin(CE_PIN, CSN_PIN)

# Função para testar sinais de SPI
def testar_gpio_spi():
    print("--- Testando sinais GPIO e SPI ---")

    # 1. Teste básico do SCK (enviar pulsos)
    GPIO.setup(SCK_PIN, GPIO.OUT)
    GPIO.output(SCK_PIN, GPIO.HIGH)
    time.sleep(0.01)
    GPIO.output(SCK_PIN, GPIO.LOW)
    time.sleep(0.01)
    print("Pulsos no pino SCK enviados.")

    # 2. Testar resposta no SPI enviando comando 0xFF
    response = spi.xfer2([0xFF])
    print(f"Resposta SPI ao comando 0xFF: {response}")

    # 3. Verificar se o MISO está recebendo sinais
    GPIO.setup(MISO_PIN, GPIO.IN)
    miso_value = GPIO.input(MISO_PIN)
    print(f"Valor atual no pino MISO: {'ALTO' if miso_value else 'BAIXO'}")

    # 4. Teste final: leitura do registro STATUS
    status = radio.get_status()
    print(f"Registro STATUS lido: 0x{status:02X}")

    if status == 0x00:
        print("Erro: O chip NRF24 não está respondendo corretamente.")
    else:
        print("O chip NRF24 está respondendo corretamente.")

    print("--- Teste de sinais concluído ---\n")

# Executar os testes
try:
    testar_gpio_spi()
except KeyboardInterrupt:
    print("\nTeste interrompido pelo usuário.")
finally:
    GPIO.cleanup()
