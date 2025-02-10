import pigpio
from nrf24 import NRF24, RF24_PA, RF24_DATA_RATE, RF24_PAYLOAD, SPI_CHANNEL
import time

# Inicializar o cliente pigpio
pi = pigpio.pi()
if not pi.connected:
    print("Erro: Não foi possível conectar ao pigpio.")
    exit()

# Definição dos pinos
CE_PIN = 22  # GPIO 22 - Chip Enable
CSN_PIN = 5  # GPIO 5 (CSN é configurado via SPI)

# Inicialização do rádio NRF24
radio = NRF24(
    pi,
    ce=CE_PIN,
    payload_size=RF24_PAYLOAD.DYNAMIC,
    channel=45,
    data_rate=RF24_DATA_RATE.RATE_2MBPS,
    pa_level=RF24_PA.MAX
)

# Configurações adicionais
radio.set_address_bytes(5)
radio.open_writing_pipe("1NODE")

def testar_comunicacao_nrf24():
    print("--- Testando comunicação com o chip NRF24 ---")
    radio.show_registers()
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
        radio.power_down()
        pi.stop()  # Desconectar do pigpio
