# Código do receptor
import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import time
import spidev

# Mesma configuração de pinos
CE_PIN = 2
CSN_PIN = 5
SCK_PIN = 6
MOSI_PIN = 7
MISO_PIN = 4

GPIO.setmode(GPIO.BCM)
pipes = [[0xF0, 0xF0, 0xF0, 0xF0, 0xE1], [0xE8, 0xE8, 0xF0, 0xF0, 0xE1]]

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

radio = NRF24(GPIO, spi)
radio.begin(CE_PIN, CSN_PIN)

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
radio.startListening()

try:
    print("Receptor iniciado. Aguardando mensagens...")
    while True:
        if radio.available():
            recebido = []
            radio.read(recebido, radio.getDynamicPayloadSize())
            print("Recebido:", "".join(map(chr, filter(None, recebido))))
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nPrograma interrompido pelo usuário")
finally:
    GPIO.cleanup()
    spi.close()
