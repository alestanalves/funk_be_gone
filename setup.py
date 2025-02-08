import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev
import random

# Mapeamento dos pinos
CE_PIN = 2    # GP2
CSN_PIN = 5   # GP5
SCK_PIN = 6   # GP6
MOSI_PIN = 7  # GP7
MISO_PIN = 4  # GP4

# Configuração dos pinos
GPIO.setmode(GPIO.BCM)

# Configuração do SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Configuração do rádio
radio = NRF24(GPIO, spi)
radio.begin(CE_PIN, CSN_PIN)

# Configurações básicas
radio.set_payload_size(32)
radio.set_channel(0x76)  # Canal inicial
radio.set_data_rate(NRF24.BR_1MBPS)
radio.set_pa_level(NRF24.PA_MAX)

# Canais disponíveis para jamming
bluetooth_channels = [32, 34, 46, 48, 50, 52, 0, 1, 2, 4, 6, 8, 22, 24, 26, 28, 30, 74, 76, 78, 80]
ble_channels = [2, 26, 80]

def configure_radio(channel):
    """Configura o rádio para um canal específico."""
    radio.set_channel(channel)

def jam_ble():
    """Jamming em canais BLE."""
    channel = random.choice(ble_channels)
    print(f"Jamming BLE no canal {channel}")
    configure_radio(channel)

def jam_bluetooth():
    """Jamming em canais Bluetooth."""
    channel = random.choice(bluetooth_channels)
    print(f"Jamming Bluetooth no canal {channel}")
    configure_radio(channel)

def jam_all():
    """Jamming em canais Bluetooth e BLE aleatoriamente."""
    if random.choice([True, False]):
        jam_bluetooth()
    else:
        jam_ble()

def verificar_radio():
    """Verifica se o módulo NRF24 está funcionando corretamente."""
    print("Verificando módulo NRF24...")

    # Leitura do registro STATUS
    status = radio.get_status()
    print(f"Registro STATUS: 0x{status:02X}")

    # Verifica se o valor é válido (o valor padrão deve estar entre 0x0E e 0x0F)
    if status & 0x0E == 0x0E:
        print("Módulo NRF24 conectado e respondendo corretamente.")
    else:
        print("Aviso: O registro STATUS não indica uma resposta correta. Verifique as conexões.")

    # Teste de leitura/escrita de registro
    try:
        radio.write_register(NRF24.CONFIG, 0x0A)
        config_value = radio.read_register(NRF24.CONFIG)
        if config_value == 0x0A:
            print("Teste de escrita/leitura no registro CONFIG bem-sucedido.")
        else:
            print("Erro: Falha na verificação de escrita/leitura no registro CONFIG.")
    except Exception as e:
        print(f"Erro durante a verificação do rádio: {e}")

# Script principal
try:
    print("Iniciando jamming com o módulo NRF24L01...")

    # Verificação inicial do rádio
    verificar_radio()

    while True:
        # Alterna entre diferentes modos de jamming
        mode = random.choice(["ble", "bluetooth", "all"])
        if mode == "ble":
            jam_ble()
        elif mode == "bluetooth":
            jam_bluetooth()
        elif mode == "all":
            jam_all()

        # Aguarda 1 segundo antes de repetir
        time.sleep(1)

except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário")
except Exception as e:
    print(f"Erro: {e}")
finally:
    GPIO.cleanup()
    spi.close()
