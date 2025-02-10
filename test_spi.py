import spidev

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 8000000

# Enviar e receber um byte
response = spi.xfer2([0xAA])
print("Resposta SPI:", response)

spi.close()
