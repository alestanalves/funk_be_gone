import time
from PIL import Image, ImageDraw, ImageFont
import board
import adafruit_ssd1306

# Configurar a interface I2C manualmente
i2c = board.I2C()  # Usar GPIO 2 (SDA) e GPIO 3 (SCL)

# Inicializar a tela OLED
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)

# Criar uma imagem para desenhar
image = Image.new('1', (oled.width, oled.height))
draw = ImageDraw.Draw(image)

# Limpar a tela
draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

# Exibir texto
font = ImageFont.load_default()
draw.text((10, 10), "Teste OLED OK!", font=font, fill=255)

# Enviar imagem para a tela
oled.image(image)
oled.show()

# Aguardar antes de limpar a tela
time.sleep(10)
oled.fill(0)
oled.show()
