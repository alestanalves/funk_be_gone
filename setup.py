import pigpio
from nrf24 import NRF24
import time

# Inicializar o cliente pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Erro: Não foi possível conectar ao pigpio.")
    exit()

# Definição dos pinos
CE_PIN = 22    # GPIO 22 - Chip Enable
CSN_PIN = 5    # GPIO 5 - Chip Select (é definido diretamente na SPI)

# Inicialização do rádio NRF24
radio = NRF24(pi, CE_PIN)  # Passa apenas o pino CE

# Configuração SPI
radio.spi = pi.spi_open(0, 8000000, 0)  # Abrir SPI no canal 0 com 8 MHz e modo 0

# Configurações do rádio
radio.set_channel(45)
radio.set_payload_size(32)
radio.set_pa_level(NRF24.PA_MAX)
radio.set_data_rate(NRF24.BR_2MBPS)
radio.set_retries(15, 15)

def testar_comunicacao_nrf24():
    print("--- Testando comunicação com o chip NRF24 ---")
    status = radio.get_status()
    if status != 0x00:
        print("O chip NRF24 está conectado e respondendo corretamente.")
        print(f"Registro STATUS: 0x{status:02X}")
    else:
        print("Erro: O chip NRF24 não está respondendo corretamente.")
    print("--- Teste de comunicação concluído ---\n")

def nrf_jammer():
    print("NRF24 inicializado. Iniciando jammer...")

    hopping_channels = [32, 34, 46, 48, 50, 52, 0, 1, 2, 4, 6, 8, 22, 24, 26, 28, 30, 74, 76, 78, 80, 82, 84, 86]
    ptr_hop = 0

    while True:
        # Alterar o canal do rádio
        ptr_hop = (ptr_hop + 1) % len(hopping_channels)
        radio.set_channel(hopping_channels[ptr_hop])
        print("Canal atual:", hopping_channels[ptr_hop])

        # Pequeno delay para hopping
        time.sleep(0.2)

def setup():
    testar_comunicacao_nrf24()
    nrf_jammer()

if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    finally:
        pi.spi_close(radio.spi)
        pi.stop()  # Desconectar do pigpio
