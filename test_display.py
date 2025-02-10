import time
from PIL import Image, ImageDraw, ImageFont
import Adafruit_SSD1306

# Configuração da tela OLED (I2C address padrão: 0x3C)
oled = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_address=0x3C)

# Inicializar a tela
oled.begin()
oled.clear()
oled.display()

# Criar uma imagem para desenhar
width = oled.width
height = oled.height
image = Image.new('1', (width, height))

# Obter o objeto de desenho
draw = ImageDraw.Draw(image)

# Limpar a tela com fundo preto
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Carregar uma fonte padrão do PIL
font = ImageFont.load_default()

# Exibir texto na tela
draw.text((10, 10), "Teste OLED OK!", font=font, fill=255)

# Atualizar a tela com a imagem desenhada
oled.image(image)
oled.display()

# Manter o texto na tela por 10 segundos
time.sleep(10)

# Limpar a tela
oled.clear()
oled.display()
