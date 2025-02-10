import argparse
import struct
import sys
import time
import traceback

import pigpio
from nrf24 import *

def transmission_result(nrf: NRF24):
    if nrf.get_packages_lost() == 0:
        print(f"Success: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")
    else:
        print(f"Error: lost={nrf.get_packages_lost()}, retries={nrf.get_retries()}")

if __name__ == "__main__":
    print("Python NRF24 Test Sender Example.")

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="NRF24 Test Sender.")
    parser.add_argument('-n', '--hostname', type=str, default='localhost', help="Hostname for the pigpio daemon.")
    parser.add_argument('-p', '--port', type=int, default=8888, help="Port number of the pigpio daemon.")
    parser.add_argument('address', type=str, nargs='?', default='1NODE', help="Address to send to (3 to 5 ASCII characters).")

    args = parser.parse_args()
    hostname = args.hostname
    port = args.port
    address = args.address

    if not (2 < len(address) < 6):
        print(f'Invalid address {address}. Addresses must be 3 to 5 ASCII characters.')
        sys.exit(1)

    # Connect to pigpiod
    print(f'Connecting to GPIO daemon on {hostname}:{port} ...')
    pi = pigpio.pi(hostname, port)
    if not pi.connected:
        print("Not connected to Raspberry Pi ... goodbye.")
        sys.exit()

    # Create NRF24 object
    print(f"Initializing NRF24 module to send to address: {address}")
    nrf = NRF24(pi, ce=22, payload_size=RF24_PAYLOAD.DYNAMIC, channel=45, data_rate=RF24_DATA_RATE.RATE_2MBPS, pa_level=RF24_PA.MAX)
    nrf.set_address_bytes(len(address))
    nrf.open_writing_pipe(address)

    # Display the content of NRF24L01 registers
    nrf.show_registers()

    try:
        print(f'Starting to send data to {address}')
        while True:
            # Send a sample payload with dummy sensor data
            temperature = 23.0  # Simulated temperature reading
            humidity = 60.0     # Simulated humidity reading
            payload = struct.pack("<Bff", 0x01, temperature, humidity)
            print(f"Sending sensor values: temperature={temperature}, humidity={humidity}")

            # Reset package loss counter and send the payload
            nrf.reset_packages_lost()
            nrf.send(payload)

            # Wait for acknowledgment
            timeout = False
            try:
                nrf.wait_until_sent()
            except TimeoutError:
                timeout = True

            # Display the result of the send operation
            if not timeout:
                transmission_result(nrf)
            else:
                print("Timed out while waiting for acknowledgment.")

            # Wait 5 seconds before sending the next reading
            time.sleep(5)
    except:
        traceback.print_exc()
    finally:
        nrf.power_down()
        pi.stop()
