from machine import SPI, Pin
import time
from nrf24l01 import NRF24L01

# Configuração do SPI
spi = SPI(0,
          baudrate=1000000,
          polarity=0,
          phase=0,
          sck=Pin(6),
          mosi=Pin(7),
          miso=Pin(4))

# Configuração dos pinos CE e CSN
csn = Pin(5, mode=Pin.OUT, value=1)
ce = Pin(2, mode=Pin.OUT, value=0)

# Inicialização do módulo NRF24L01
nrf = NRF24L01(spi, csn, ce, payload_size=8)

# Configuração do endereço
address = b"\x00\x00\x00\x00\x01"
nrf.open_tx_pipe(address)

# Função para enviar dados
def send_data(data):
    nrf.send(data)
    time.sleep_ms(50)

# Loop principal
while True:
    try:
        # Exemplo: enviando uma mensagem
        message = b"Ola!"
        send_data(message)
        print("Dados enviados:", message)
        time.sleep(1)
    except Exception as e:
        print("Erro:", e)
