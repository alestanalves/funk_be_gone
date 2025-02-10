import RPi.GPIO as GPIO
from nrf24 import NRF24
import time

# Configuração do modo de numeração dos pinos (BCM)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Definição dos pinos para o NRF24L01
CE_PIN = 22    # GPIO 22 - Chip Enable
CSN_PIN = 5    # GPIO 5 - Chip Select

# Inicialização do rádio NRF24
radio = NRF24(CE_PIN, CSN_PIN)

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

    # Enviar e receber um valor de teste usando o SPI direto
    response = radio.spi_transfer([0xFF])
    if response[0] != 0:
        print("Comunicação SPI verificada com sucesso. Valor retornado:", hex(response[0]))
    else:
        print("Erro na comunicação SPI. Verifique as conexões do SPI.")

    print("--- Teste de comunicação SPI concluído ---\n")

def testar_comunicacao_nrf24():
    print("--- Testando comunicação com o chip NRF24 ---")

    # Ler o registro STATUS do NRF24 para verificar se está respondendo
    status = radio.get_status()
    if status != 0x00:
        print("O chip NRF24 está conectado e respondendo corretamente.")
        print(f"Registro STATUS: 0x{status:02X}")
    else:
        print("Erro: O chip NRF24 não está respondendo corretamente.")

    print("--- Teste de comunicação concluído ---\n")

def testar_resposta_registros():
    print("--- Testando resposta de registros do NRF24 ---")
    # Ler o registro CONFIG do NRF24
    config_reg = radio.read_register(NRF24.CONFIG)
    print(f"Registro CONFIG: 0x{config_reg:02X}")

    if config_reg == 0x00:
        print("Erro: Registro CONFIG não retornou uma resposta válida. Verifique as conexões.")
    else:
        print("Resposta válida do registro CONFIG detectada.")

    print("--- Teste de resposta de registros concluído ---\n")

def setup():
    # Testar pinos, comunicação e registros
    testar_pinos_nrf24()
    testar_comunicacao_spi()
    testar_comunicacao_nrf24()
    testar_resposta_registros()

    # Apenas continuar se o NRF24 estiver funcionando corretamente
    if radio.get_status() == 0x00:
        print("Erro crítico: O chip NRF24 não está funcionando. Interrompendo...")
        return

    # Iniciar o jammer
    nrf_jammer()

def nrf_start():
    radio.set_payload_size(32)
    radio.set_channel(45)
    radio.set_pa_level(NRF24.PA_MAX)
    radio.set_data_rate(NRF24.BR_2MBPS)
    radio.set_retries(15, 15)

    # Definir o endereço de escrita
    radio.write_register(NRF24.TX_ADDR, [0xE8, 0xE8, 0xF0, 0xF0, 0xE1])

    return True

def nrf_jammer():
    if nrf_start():
        print("NRF24 inicializado. Iniciando jammer...")

        # Ativar transmissão contínua
        global ptr_hop
        hopping_channels = [32, 34, 46, 48, 50, 52, 0, 1, 2, 4, 6, 8, 22, 24, 26, 28, 30, 74, 76, 78, 80, 82, 84, 86]
        ptr_hop = 0

        while True:
            ptr_hop += 1
            if ptr_hop >= len(hopping_channels):
                ptr_hop = 0  # Reiniciar o índice se atingir o final da lista

            # Alterar o canal do rádio
            radio.set_channel(hopping_channels[ptr_hop])
            print("Canal atual:", hopping_channels[ptr_hop])

            # Pequeno delay para hopping
            time.sleep(0.2)
    else:
        print("Erro ao iniciar o jammer. Verifique as conexões.")

if __name__ == "__main__":
    try:
        setup()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    finally:
        GPIO.cleanup()  # Limpar configuração dos pinos
