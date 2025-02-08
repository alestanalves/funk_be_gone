from machine import SPI, Pin
from nrf24l01 import NRF24L01

# Configuração do SPI
spi = SPI(0,
          baudrate=1000000,
          polarity=0,
          phase=0,
          sck=Pin(6),
          mosi=Pin(7),
          miso=Pin(4))

# Configuração dos pinos
csn = Pin(5, mode=Pin.OUT, value=1)
ce = Pin(2, mode=Pin.OUT, value=0)

try:
    # Tenta criar uma instância do NRF24L01
    nrf = NRF24L01(spi, csn, ce)
    print("Biblioteca instalada com sucesso!")
except Exception as e:
    print("Erro:", e)
