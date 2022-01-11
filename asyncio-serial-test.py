# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import asyncio
import sys
import threading
from azure.iot.device.aio import IoTHubModuleClient
import json
from datetime import datetime
import os
from statistics import mean
import pytz
import serial_asyncio

OBSERVED_VALUES = ['concentration', 'temperature', 'relative_humidity', 'atmos_pressure']
CONCENTRATION, TEMPERATURE, RELATIVE_HUMIDITY, ATMOS_PRESSURE = OBSERVED_VALUES
OBSERVED_VALUE_INDEX = {OBSERVED_VALUES[i]: i for i in range(len(OBSERVED_VALUES))}
OBSERVED_TIME = 'observed_time'
VALID_RANGES = {
    CONCENTRATION: (0, 2500),
    TEMPERATURE: (-10, 75),
    RELATIVE_HUMIDITY: (0, 100),
    ATMOS_PRESSURE: (600, 850)
}
EST = pytz.timezone('America/New_York')
UTC = pytz.timezone('UTC')
HRLY_INTERVAL_FORMAT = '%Y%m%d%H'

# Event indicating client stop
stop_event = threading.Event()
messages = {}

class SerialReader(asyncio.Protocol):
    def connection_made(self, transport):
        """Store the serial transport and prepare to receive data.
        """
        self.transport = transport
        self.buf = ''
        self.msgs_recvd = 0
        print('Reader connection created')
        
    def data_received(self, ch):
        global messages

        d = ch.decode('utf-8', errors='ignore')
        if d == '\r':
            print (f'received line: {self.buf}')
            hrlyInterval = datetime.utcnow().strftime(HRLY_INTERVAL_FORMAT)
            messages.setdefault(hrlyInterval, []).append(self.buf)
        else:
            self.buf += d

    def connection_lost(self, exc):
        print('Reader closed')


def main():
    loop = asyncio.get_event_loop()
    reader = serial_asyncio.create_serial_connection(loop, SerialReader, 'SerialReader', baudrate=19200)
    asyncio.ensure_future(reader)
    print('Reader scheduled')
    loop.run_forever()
    print('Done')


