import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 8000000
response = spi.xfer2([0xFF])
print("Resposta SPI:", response)
spi.close()
