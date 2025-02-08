"""NRF24L01 driver for MicroPython"""
import time
from machine import Pin, SPI

class NRF24L01:
    CONFIG      = const(0x00)
    EN_AA       = const(0x01)
    EN_RXADDR   = const(0x02)
    SETUP_AW    = const(0x03)
    SETUP_RETR  = const(0x04)
    RF_CH       = const(0x05)
    RF_SETUP    = const(0x06)
    STATUS      = const(0x07)
    RX_ADDR_P0  = const(0x0a)
    TX_ADDR     = const(0x10)
    RX_PW_P0    = const(0x11)
    FIFO_STATUS = const(0x17)
    DYNPD       = const(0x1c)

    RX_MODE     = const(1)
    TX_MODE     = const(0)

    def __init__(self, spi, csn, ce, payload_size=32):
        self.spi = spi
        self.csn = csn
        self.ce = ce
        self.payload_size = payload_size
        self.pipe0_read_addr = None
        
        # Initialize CSN and CE pins
        self.csn.value(1)
        self.ce.value(0)
        
        # Reset registers
        self.reg_write(CONFIG, 0x0b)  # CRC enable, 2-byte CRC length
        self.reg_write(EN_AA, 0x01)   # Auto-ACK on pipe 0
        self.reg_write(EN_RXADDR, 1)  # Enable data pipe 0
        self.reg_write(SETUP_AW, 0x03)  # 5-byte address
        self.reg_write(SETUP_RETR, (0x04 << 4) | 0x0f)  # 1500us retry, 15 retries
        self.reg_write(RF_CH, 0x4c)   # Channel 76
        self.reg_write(RF_SETUP, 0x07)  # 1Mbps, 0dBm, Setup LNA
        self.reg_write(RX_PW_P0, payload_size)
        self.reg_write(DYNPD, 0)      # Disable dynamic payloads
        
        # Clear status flags
        self.reg_write(STATUS, 0x70)   
        self.reg_write(FIFO_STATUS, 0x11)  # Clear FIFO status

    def reg_read(self, reg):
        self.csn.value(0)
        self.spi.write(bytes([reg]))
        val = self.spi.read(1)[0]
        self.csn.value(1)
        return val

    def reg_write(self, reg, val):
        self.csn.value(0)
        self.spi.write(bytes([0x20 | reg, val]))
        self.csn.value(1)

    def flush_rx(self):
        self.csn.value(0)
        self.spi.write(b'\xe2')
        self.csn.value(1)

    def flush_tx(self):
        self.csn.value(0)
        self.spi.write(b'\xe1')
        self.csn.value(1)

    def set_power_speed(self, power='low', speed='1Mbps'):
        setup = self.reg_read(RF_SETUP) & 0b11111000
        if power == 'high':
            setup |= 0b110
        elif power == 'low':
            setup |= 0b000
        if speed == '2Mbps':
            setup |= 0b1000
        elif speed == '1Mbps':
            setup |= 0b0000
        elif speed == '250kbps':
            setup |= 0b0100
        self.reg_write(RF_SETUP, setup)

    def start_listening(self):
        self.reg_write(CONFIG, self.reg_read(CONFIG) | 0x03)
        self.ce.value(1)
        if self.pipe0_read_addr is not None:
            self.reg_write_bytes(RX_ADDR_P0, self.pipe0_read_addr)

    def stop_listening(self):
        self.ce.value(0)
        self.reg_write(CONFIG, self.reg_read(CONFIG) & ~0x01)

    def send(self, buf):
        self.stop_listening()
        self.ce.value(0)
        
        self.reg_write(STATUS, 0x70)  # Clear flags
        self.flush_tx()
        
        self.csn.value(0)
        self.spi.write(b'\xa0')  # Write TX payload
        self.spi.write(buf)
        self.csn.value(1)
        
        self.ce.value(1)
        time.sleep_us(15)  # Send pulse
        self.ce.value(0)
        
        while not (self.reg_read(STATUS) & 0x20):  # Wait for TX complete
            pass
        
        self.reg_write(STATUS, 0x20)  # Clear TX flag

    def recv(self):
        if not self.reg_read(FIFO_STATUS) & 1:  # Data in RX FIFO
            self.csn.value(0)
            self.spi.write(b'\x61')  # Read RX payload
            buf = self.spi.read(self.payload_size)
            self.csn.value(1)
            self.reg_write(STATUS, 0x40)  # Clear RX flag
            return buf
        return None

    def reg_write_bytes(self, reg, buf):
        self.csn.value(0)
        self.spi.write(bytes([0x20 | reg]) + buf)
        self.csn.value(1)

    def set_channel(self, ch):
        if not 0 <= ch <= 125:
            raise ValueError("Channel must be between 0-125")
        self.reg_write(RF_CH, ch)

    def set_address(self, address):
        # Set TX address and RX pipe 0 address
        self.reg_write_bytes(RX_ADDR_P0, address)
        self.reg_write_bytes(TX_ADDR, address)
        self.pipe0_read_addr = address

    def any(self):
        return not (self.reg_read(FIFO_STATUS) & 1)
