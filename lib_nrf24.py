#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import spidev
import time
import sys

class NRF24:
    MAX_CHANNEL = 127
    MAX_PAYLOAD_SIZE = 32

    # Pins
    CE_PIN   = 22
    IRQ_PIN  = 24
    CSN_PIN  = 0

    # Registers
    CONFIG      = 0x00
    EN_AA       = 0x01
    EN_RXADDR   = 0x02
    SETUP_AW    = 0x03
    SETUP_RETR  = 0x04
    RF_CH       = 0x05
    RF_SETUP    = 0x06
    STATUS      = 0x07
    OBSERVE_TX  = 0x08
    CD          = 0x09
    RX_ADDR_P0  = 0x0A
    RX_ADDR_P1  = 0x0B
    RX_ADDR_P2  = 0x0C
    RX_ADDR_P3  = 0x0D
    RX_ADDR_P4  = 0x0E
    RX_ADDR_P5  = 0x0F
    TX_ADDR     = 0x10
    RX_PW_P0    = 0x11
    RX_PW_P1    = 0x12
    RX_PW_P2    = 0x13
    RX_PW_P3    = 0x14
    RX_PW_P4    = 0x15
    RX_PW_P5    = 0x16
    FIFO_STATUS = 0x17
    DYNPD       = 0x1C
    FEATURE     = 0x1D

    # Bit Mnemonics
    MASK_RX_DR  = 6
    MASK_TX_DS  = 5
    MASK_MAX_RT = 4
    EN_CRC      = 3
    CRCO        = 2
    PWR_UP      = 1
    PRIM_RX     = 0

    # Power setup
    PA_MIN = 0
    PA_LOW = 1
    PA_HIGH = 2
    PA_MAX = 3
    PA_ERROR = 4

    # Speed setup
    BR_1MBPS = 0
    BR_2MBPS = 1
    BR_250KBPS = 2

    def __init__(self, gpio, spi):
        self.gpio = gpio
        self.spi = spi
        self.channel = 76
        self.data_rate = self.BR_1MBPS
        self.payload_size = self.MAX_PAYLOAD_SIZE
        self.ack_payload_available = False
        self.dynamic_payloads_enabled = False
        self.ack_payload_length = 5
        self.pipe0_reading_address = None

    def ce(self, level):
        if self.ce_pin is not None:
            self.gpio.output(self.ce_pin, level)

    def read_register(self, reg, length=1):
        buf = [reg & 0x1F]
        for i in range(length):
            buf.append(0)
        
        resp = self.spi.xfer2(buf)
        if length == 1:
            return resp[1]
        else:
            return resp[1:]

    def write_register(self, reg, value):
        buf = [0x20 | (reg & 0x1F)]
        
        if isinstance(value, (list, tuple)):
            buf.extend(value)
        else:
            buf.append(value)
            
        self.spi.xfer2(buf)

    def begin(self, ce_pin, csn_pin):
        self.ce_pin = ce_pin
        self.csn_pin = csn_pin
        
        if ce_pin is not None:
            self.gpio.setup(ce_pin, self.gpio.OUT)
        
        self.gpio.setup(csn_pin, self.gpio.OUT)
        
        self.ce(0)
        self.gpio.output(csn_pin, 1)
        
        time.sleep(0.005)
        
        self.write_register(self.CONFIG, 0x0C)
        self.set_retries(15, 15)
        self.set_pa_level(self.PA_MAX)
        self.set_data_rate(self.BR_1MBPS)
        self.write_register(self.CONFIG, 0x0E)
        
        self.flush_rx()
        self.flush_tx()

    def start_listening(self):
        self.write_register(self.CONFIG, self.read_register(self.CONFIG) | (1 << self.PRIM_RX))
        self.write_register(self.STATUS, self.RX_DR | self.TX_DS | self.MAX_RT)
        
        self.ce(1)
        
        if self.pipe0_reading_address:
            self.write_register(self.RX_ADDR_P0, self.pipe0_reading_address)

    def stop_listening(self):
        self.ce(0)
        self.flush_tx()
        self.flush_rx()

    def available(self):
        return self.get_status() & (1 << self.RX_DR)

    def get_status(self):
        return self.read_register(self.STATUS)

    def flush_rx(self):
        self.spi.xfer2([0xE2])

    def flush_tx(self):
        self.spi.xfer2([0xE1])

    def read(self, length):
        if length > self.MAX_PAYLOAD_SIZE:
            length = self.MAX_PAYLOAD_SIZE
            
        buf = [0x61]
        for i in range(length):
            buf.append(0)
            
        resp = self.spi.xfer2(buf)
        
        return resp[1:]

    def write(self, buf):
        length = min(len(buf), self.MAX_PAYLOAD_SIZE)
        
        self.ce(0)
        
        txbuf = [0xA0]
        txbuf.extend(buf[0:length])
        
        self.spi.xfer2(txbuf)
        
        self.ce(1)
        time.sleep(0.001)
        self.ce(0)

    def set_channel(self, channel):
        if channel > self.MAX_CHANNEL:
            channel = self.MAX_CHANNEL
        self.write_register(self.RF_CH, channel)

    def set_payload_size(self, size):
        if size > self.MAX_PAYLOAD_SIZE:
            size = self.MAX_PAYLOAD_SIZE
        self.payload_size = size
        self.write_register(self.RX_PW_P0, size)

    def set_pa_level(self, level):
        setup = self.read_register(self.RF_SETUP)
        setup &= ~((1 << 1) | (1 << 2))
        
        if level == self.PA_MAX:
            setup |= (1 << 1) | (1 << 2)
        elif level == self.PA_HIGH:
            setup |= (1 << 1)
        elif level == self.PA_LOW:
            setup |= (1 << 2)
        
        self.write_register(self.RF_SETUP, setup)

    def set_data_rate(self, speed):
        setup = self.read_register(self.RF_SETUP)
        setup &= ~((1 << 3) | (1 << 5))
        
        if speed == self.BR_250KBPS:
            setup |= (1 << 5)
        elif speed == self.BR_2MBPS:
            setup |= (1 << 3)
        
        self.write_register(self.RF_SETUP, setup)

    def set_retries(self, delay, count):
        self.write_register(self.SETUP_RETR, (delay & 0xf) << 4 | (count & 0xf))

    def get_payload_size(self):
        return self.payload_size

    def print_details(self):
        print("Detalhes do NRF24L01+")
        print("=====================")
        print(f"Canal: {self.channel}")
        print(f"Payload size: {self.payload_size}")
        print(f"Status: {bin(self.get_status())}")
