import RPi.GPIO as GPIO
import time

# Lista dos pinos GPIO a serem testados (modo BCM)
gpio_pins = [2, 3, 4, 17, 27, 22, 10, 9, 11, 5, 6, 13, 19, 26, 14, 15, 18, 23, 24, 25, 8, 7, 12, 16, 20, 21]

# Configuração inicial
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def testar_gpio():
    print("--- Testando GPIOs ---")

    for pin in gpio_pins:
        try:
            # Configurar pino como saída e escrever HIGH
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.1)

            # Configurar pino como entrada e ler valor
            GPIO.setup(pin, GPIO.IN)
            value = GPIO.input(pin)

            # Exibir resultado do teste
            if value == GPIO.HIGH:
                print(f"Pino GPIO {pin}: Funcionando corretamente (valor HIGH lido).")
            else:
                print(f"Pino GPIO {pin}: Erro - valor HIGH não detectado.")
        
        except Exception as e:
            print(f"Pino GPIO {pin}: Erro durante o teste ({e}).")

    print("--- Teste de GPIOs concluído ---")

if __name__ == "__main__":
    try:
        testar_gpio()
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
    finally:
        GPIO.cleanup()
