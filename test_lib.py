import spidev
import RPi.GPIO as GPIO
import time
from nrf24l01 import NRF24L01

# Configuração dos pinos do Raspberry Pi
CE_PIN = 22  # GPIO 22 para CE
CSN_PIN = 8  # GPIO 8 para CSN (SPI Chip Select)

# Configuração SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 4000000

# Configuração GPIO para CE
GPIO.setmode(GPIO.BCM)
GPIO.setup(CE_PIN, GPIO.OUT)

# Inicialização do NRF24L01
nrf = NRF24L01(spi, cs=GPIO.output, ce=lambda level: GPIO.output(CE_PIN, level), channel=76, payload_size=32)

# Configuração dos endereços de comunicação
address = b'1NODE'
nrf.open_tx_pipe(address)
nrf.open_rx_pipe(1, address)

def enviar_mensagem():
    try:
        # Mensagem a ser enviada
        mensagem = b"Hello from RPi"
        print("Enviando mensagem:", mensagem)

        # Iniciar o envio
        nrf.send(mensagem)
        print("Mensagem enviada com sucesso.")

    except OSError as e:
        print("Erro ao enviar mensagem:", e)

def testar_comunicacao():
    # Exibir registros do NRF24L01
    print("--- Configuração e registros do NRF24L01 ---")
    try:
        registros = {
            "CONFIG": nrf.reg_read(nrf.CONFIG),
            "STATUS": nrf.reg_read(nrf.STATUS),
            "RF_CH": nrf.reg_read(nrf.RF_CH),
            "TX_ADDR": nrf.reg_read(nrf.TX_ADDR)
        }
        for reg, valor in registros.items():
            print(f"{reg}: 0x{valor:02X}")
    except Exception as e:
        print("Erro ao acessar registros do NRF24L01:", e)

def main():
    testar_comunicacao()
    while True:
        enviar_mensagem()
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    finally:
        GPIO.cleanup()
        spi.close()
