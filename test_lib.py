import spidev
import RPi.GPIO as GPIO
import time

# NRF24L01 comandos e registros
CONFIG = 0x00
RF_CH = 0x05
STATUS = 0x07
TX_ADDR = 0x10
W_TX_PAYLOAD = 0xA0
FLUSH_TX = 0xE1
PWR_UP = 0x02

# Configuração de pinos
CE_PIN = 22   # GPIO 22 para CE
CSN_PIN = 8   # GPIO 8 para CSN

# Inicializar SPI e GPIO
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 4000000

GPIO.setmode(GPIO.BCM)
GPIO.setup(CE_PIN, GPIO.OUT)
GPIO.setup(CSN_PIN, GPIO.OUT)

def ce_high():
    GPIO.output(CE_PIN, GPIO.HIGH)

def ce_low():
    GPIO.output(CE_PIN, GPIO.LOW)

def csn_high():
    GPIO.output(CSN_PIN, GPIO.HIGH)

def csn_low():
    GPIO.output(CSN_PIN, GPIO.LOW)

def reg_write(reg, value):
    csn_low()
    spi.xfer2([0x20 | reg, value])
    csn_high()

def reg_read(reg):
    csn_low()
    resp = spi.xfer2([reg, 0xFF])
    csn_high()
    return resp[1]

def flush_tx():
    csn_low()
    spi.xfer2([FLUSH_TX])
    csn_high()

def enviar_mensagem(mensagem):
    ce_low()
    flush_tx()

    # Escrever payload
    csn_low()
    spi.xfer2([W_TX_PAYLOAD] + list(mensagem))
    csn_high()

    # Ativar envio
    ce_high()
    time.sleep(0.01)
    ce_low()

def testar_comunicacao():
    print("--- Testando comunicação com o NRF24L01 ---")
    status = reg_read(STATUS)
    print(f"Registro STATUS: 0x{status:02X}")

    if status == 0x00:
        print("Erro: O chip NRF24 não está respondendo corretamente.")
    else:
        print("O chip NRF24 está conectado e respondendo corretamente.")

def setup_nrf():
    # Configurar o rádio
    reg_write(CONFIG, PWR_UP)
    reg_write(RF_CH, 76)  # Configurar canal
    reg_write(TX_ADDR, 0xE7)  # Definir endereço de envio

    time.sleep(0.1)

def main():
    setup_nrf()
    testar_comunicacao()

    while True:
        mensagem = b"Hello NRF24!"
        print("Enviando mensagem:", mensagem)
        enviar_mensagem(mensagem)
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    finally:
        GPIO.cleanup()
        spi.close()
