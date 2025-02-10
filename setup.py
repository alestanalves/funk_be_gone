import RPi.GPIO as GPIO
from lib_nrf24 import NRF24
import spidev
import time

# Configuração do modo de numeração dos pinos (BCM) e avisos
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Definição dos pinos para o NRF24L01
CE_PIN = 22    # GPIO 22 - Chip Enable
CSN_PIN = 5    # GPIO 5 - Chip Select

# Inicialização do rádio NRF24
radio = NRF24(GPIO, spidev.SpiDev())
radio.spi.open(0, 0)  # Bus 0, Device 0
radio.spi.max_speed_hz = 8000000
radio.begin(CE_PIN, CSN_PIN)

# Lista de canais para hopping
hopping_channels = [32, 34, 46, 48, 50, 52, 0, 1, 2, 4, 6, 8, 22, 24, 26, 28, 30, 74, 76, 78, 80, 82, 84, 86]
ptr_hop = 0

def testar_pinos_nrf24():
    print("--- Testando pinos do NRF24 ---")

    # Testar pino CE
    GPIO.setup(CE_PIN, GPIO.OUT)
    GPIO.output(CE_PIN, GPIO.HIGH)
    time.sleep(0.01)
    if GPIO.input(CE_PIN) == GPIO.HIGH:
        print("Pino CE está funcionando corretamente.")
    else:
        print("Erro: Pino CE não está respondendo.")

    # Testar pino CSN
    GPIO.setup(CSN_PIN, GPIO.OUT)
    GPIO.output(CSN_PIN, GPIO.HIGH)
    time.sleep(0.01)
    if GPIO.input(CSN_PIN) == GPIO.HIGH:
        print("Pino CSN está funcionando corretamente.")
    else:
        print("Erro: Pino CSN não está respondendo.")

    print("--- Teste de pinos concluído ---\n")

def testar_comunicacao_spi():
    print("--- Testando comunicação SPI ---")
    
    spi = spidev.SpiDev()
    spi.open(0, 0)  # Bus 0, Device 0
    spi.max_speed_hz = 8000000
    
    # Enviar e receber um valor de teste
    response = spi.xfer2([0xAA])
    if response[0] != 0:
        print("Comunicação SPI verificada com sucesso. Valor retornado:", hex(response[0]))
    else:
        print("Erro na comunicação SPI. Verifique as conexões do SPI.")
    
    spi.close()
    print("--- Teste de comunicação SPI concluído ---\n")

def testar_comunicacao_nrf24():
    print("--- Testando comunicação com o chip NRF24 ---")
    
    # Lendo o registro STATUS do chip NRF24
    status = radio.read_register(radio.STATUS)
    if status != 0x00:  # Espera-se que o registro STATUS não seja zero
        print("O chip NRF24 está conectado e respondendo corretamente.")
        print(f"Registro STATUS: 0x{status:02X}")
    else:
        print("Erro: O chip NRF24 não está respondendo corretamente.")
    
    print("--- Teste de comunicação concluído ---\n")

def nrf_start():
    radio.setPayloadSize(32)
    radio.setChannel(45)
    radio.setPALevel(NRF24.PA_MAX)
    radio.setDataRate(NRF24.BR_2MBPS)
    radio.setAutoAck(False)
    radio.openWritingPipe([0xE8, 0xE8, 0xF0, 0xF0, 0xE1])

    return True

def nrf_jammer():
    if nrf_start():
        print("NRF24 inicializado. Iniciando jammer...")

        # Ativar transmissão contínua
        global ptr_hop
        while True:
            ptr_hop += 1
            if ptr_hop >= len(hopping_channels):
                ptr_hop = 0  # Reiniciar o índice se atingir o final da lista

            # Alterar o canal do rádio
            radio.setChannel(hopping_channels[ptr_hop])
            print("Canal atual:", hopping_channels[ptr_hop])

            # Pequeno delay para hopping
            time.sleep(0.2)
    else:
        print("Erro ao iniciar o jammer. Verifique as conexões.")

def setup():
    # Testar pinos e comunicação
    testar_pinos_nrf24()
    testar_comunicacao_spi()
    testar_comunicacao_nrf24()

    # Iniciar o jammer
    nrf_jammer()

if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    finally:
        GPIO.cleanup()  # Limpar configuração dos pinos
