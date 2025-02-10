import machine
import utime
from nrf24l01 import NRF24L01

# Configuração dos pinos do Raspberry Pi Pico ou MicroPython board
spi = machine.SPI(0, baudrate=4000000, polarity=0, phase=0, sck=machine.Pin(2), mosi=machine.Pin(3), miso=machine.Pin(4))
csn = machine.Pin(5, machine.Pin.OUT)
ce = machine.Pin(0, machine.Pin.OUT)

# Inicialização do módulo NRF24L01
nrf = NRF24L01(spi, csn, ce, channel=76, payload_size=32)

# Endereço de comunicação (5 bytes)
address = b'1NODE'

# Configuração do transmissor
nrf.open_tx_pipe(address)
nrf.open_rx_pipe(1, address)

def enviar_mensagem():
    try:
        # Dados a serem enviados
        mensagem = b"Hello NRF!"
        print("Enviando mensagem:", mensagem)

        # Iniciar o envio
        nrf.send(mensagem)
        print("Mensagem enviada com sucesso.")

    except OSError as e:
        print("Erro ao enviar mensagem:", e)

def testar_comunicacao():
    # Exibir registros do NRF24
    print("--- Configuração e registros do NRF24 ---")
    try:
        nrf.start_listening()
        registros = {
            "CONFIG": nrf.reg_read(CONFIG),
            "STATUS": nrf.reg_read(STATUS),
            "RF_CH": nrf.reg_read(RF_CH),
            "TX_ADDR": nrf.reg_read(TX_ADDR)
        }
        for reg, valor in registros.items():
            print(f"{reg}: 0x{valor:02X}")

        nrf.stop_listening()
    except Exception as e:
        print("Erro ao acessar registros do NRF24:", e)

# Função principal
def main():
    testar_comunicacao()
    while True:
        enviar_mensagem()
        utime.sleep(2)

if __name__ == "__main__":
    main()
