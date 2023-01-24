"""

Stratavac COMS driver
"""

from __future__ import annotations

import logging
import typing
import time

import serial
# from PyQt5 import QtSerialPort
__all__ = ['DVCUPDriver']

from PyQt5.QtSerialPort import QSerialPort

logger = logging.getLogger(__name__)


class DVCUPDriver:
   """Driver for DVCUP vacuum gauge."""

   _CMD_MANUAL_MODE: typing.ClassVar[str] = 'M=M'
   _CMD_AUTO_MODE: typing.ClassVar[str] = 'M=A'
   _CMD_DIAGNOSTIC_MODE: typing.ClassVar[str] = 'M=D'
   _CMD_VERSION: typing.ClassVar[str] = 'V?'
   _CMD_PRESSURE_FMT: typing.ClassVar[str] = 'VAC{slot}?'
   _CMD_PRESSURE_FMT_3CM: typing.ClassVar[str] = 'VAC?'
   _CMD_SETPOINT_FMT_3CM: typing.ClassVar[str] = 'SPS?'
   _CMD_SETPOINTSET_FMT_3CM: typing.ClassVar[str] = 'SPS={SPS}'
   _RSP_ERROR: typing.ClassVar[str] = 'ERR'

   DEFAULT_TIMEOUT: typing.ClassVar[typing.Optional[float]] = 5.0
   """Default serial timeout in seconds."""
   DEFAULT_AUTO_TIMEOUT: typing.ClassVar[typing.Optional[float]] = 10.0
   """Default serial timeout in seconds for auto mode (by default, the device reports every 5 seconds)."""

   _BAUD_RATE: typing.ClassVar[int] = 9600
   _ENCODING: typing.ClassVar[str] = 'ascii'
   _WRITE_TERMINATION: typing.ClassVar[str] = '\r\n'
   _READ_TERMINATION: typing.ClassVar[str] = '\r\n'

   def __init__(self, device: str, *, timeout: typing.Optional[float] = DEFAULT_TIMEOUT, **kwargs: typing.Any):
       """Initialize a KJL SPARC driver.

       :param device: The serial device
       :param timeout: The read timeout in seconds
       :param kwargs: Keyword arguments passed to the serial device
       """
       assert isinstance(device, str)
       assert isinstance(timeout, float) or timeout is None

       # device setup
       logger.debug(f'connecting to {device} (timeout: {timeout})')
       self._serial = serial.Serial(
           device, timeout=timeout, baudrate=self._BAUD_RATE,
           bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
           **kwargs
       )


   def __enter__(self) -> DVCUPDriver:
       return self

   def __exit__(self, exc_type: typing.Any, exc_val: typing.Any, exc_tb: typing.Any) -> typing.Any:
       self.close()

   def close(self) -> None:
       """Close the connection."""
       logger.debug('closing connection')
       self._serial.close()

   def _write(self, msg: str, *, flush: bool = True) -> None:
       assert isinstance(msg, str), 'Message must be a string'
       assert isinstance(flush, bool), 'Flush must be a bool'

       # Write message
       logger.debug(f'write: {msg}')
       self._serial.write(f'{msg}{self._WRITE_TERMINATION}'.encode(self._ENCODING))
       if flush:
           # Flush immediately
           self._serial.flush()

       # Insert a 100 ms delay to give the device time to process the message (recommended by KJL)
       time.sleep(0.1)

   def _read(self) -> str:
       # Read response

       #response = self._serial.read_until(self._READ_TERMINATION.encode(self._ENCODING)).decode(self._ENCODING)
       response = self._serial.readline()

       # if not response:
       #     raise serial.SerialException('Device did not respond (device probably not connected)')
       # if not response.endswith(self._READ_TERMINATION):
       #     raise serial.SerialException('Device response not terminated correctly (connection probably timed out)')

       # Trim message
       response = response[:-len(self._READ_TERMINATION)].decode(self._ENCODING)

       logger.debug(f'response: {response}')
       # Check for error messages
       # if response.startswith(self._RSP_ERROR):
       #     raise RuntimeError(f'Device returned error "{response}"')

       # Return response
       return response

   def _query(self, msg: str) -> str:
       # Write message and return response
       self._write(msg, flush=True)

       return self._read()

   def flush(self) -> None:
       """Clear serial output buffer and flush serial input buffer."""

       logger.debug('clearing serial output buffer and flushing serial input buffer')
       self._serial.reset_output_buffer()
       self._serial.flush()
       while self._serial.in_waiting:
           self._serial.reset_input_buffer()

   def _set_mode(self, cmd: str) -> None:
       assert cmd in {self._CMD_MANUAL_MODE, self._CMD_AUTO_MODE, self._CMD_DIAGNOSTIC_MODE}
       logger.debug(f'setting device mode: {cmd}')
       response = self._query(cmd)
       if response != cmd:
           # An unexpected message can happen when the device is still reporting in automatic mode
           # Hence, an unexpected response is ignored
           logger.warning(f'unexpected response for manual mode: {response}')

   def set_manual_mode(self) -> str:
       """Set the device to manual mode (so it does not report readings continuously)."""
       mode = self._query(self._CMD_MANUAL_MODE)
       return mode

   def set_auto_mode(self) -> None:
       """Set the device to auto mode (so it reports readings continuously)."""
       self._set_mode(self._CMD_AUTO_MODE)

   def get_version(self) -> str:
       """Return the version string of the device."""
       version = self._query(self._CMD_VERSION)
       if not version.startswith('V='):
           raise ValueError('Unexpected version string returned')
       return version[2:]

   def get_pressure_3CM(self) -> float:
       """Query a single pressure reading from a combined 3CM driver output

       :return: pressure reading from device in Torr
       :raise serial.SerialException: Raised in case of serial communication errors
       :raise ValueError: Raised when response can not be converted to a float
       """

       response = self._query(self._CMD_PRESSURE_FMT_3CM)
       logger.info(f'pressure query response: {response}')

       # query returns a string like "VAC1=2.23e-05"
       if response.startswith("VAC=R"):
           response = "VAC=808"
       if response.startswith("VAC=E"):
           response = "VAC=808"

       return float(response[4:])

   def get_setpoint_Dinamo(self) -> float:
       """Query a single pressure reading from a combined 3CM driver output

       :return: pressure reading from device in Torr
       :raise serial.SerialException: Raised in case of serial communication errors
       :raise ValueError: Raised when response can not be converted to a float
       """

       response = self._query(self._CMD_SETPOINT_FMT_3CM)

       logger.info(f'pressure query response: {response}')

       # query returns a string like "VAC1=2.23e-05"
       # if not response.startswith(f"VAC{slot}="):
       #     raise ValueError('Unexpected response to pressure query')

       return (response[4:])

   def set_setpoint_Dinamo(self, SPS: float = 0.0) -> float:
       """Query a single pressure reading from a combined 3CM driver output

       :param SPS: setpoint that you want to achieve
       :return: setpoint from device in Torr
       :raise serial.SerialException: Raised in case of serial communication errors
       :raise ValueError: Raised when response can not be converted to a float
       """

       response = self._query(self._CMD_SETPOINTSET_FMT_3CM.format(SPS=SPS))
       logger.info(f'pressure query response: {response}')

       # query returns a string like "VAC1=2.23e-05"
       # if not response.startswith(f"VAC{slot}="):
       #     raise ValueError('Unexpected response to pressure query')

       return (response[4:])

   def get_pressure(self, slot: int = 1) -> float:
       """Query a single pressure reading from one of the vacuum sensors by querying the device.

       To read pressure without a query (i.e. using auto mode), see :func:`read_pressure`.

       :param slot: The sensor slot ``{1, 2, 3}``
       :return: pressure reading from device in Torr
       :raise serial.SerialException: Raised in case of serial communication errors
       :raise ValueError: Raised when response can not be converted to a float
       """

       response = self._query(self._CMD_PRESSURE_FMT.format(slot=slot))
       logger.info(f'pressure query response: {response}')

       # query returns a string like "VAC1=2.23e-05"
       # if not response.startswith(f"VAC{slot}="):
       #     raise ValueError('Unexpected response to pressure query')

       return (response[5:])

   def read_pressure(self) -> float:
       """Read a single pressure message from a vacuum sensor in auto mode.

       This function assumes the device is in auto mode and waits for a message from the device.
       Buffers should be flushed before using this function and the timeout should be set correctly.
       This function returns when a message is received or when the serial connection times out.
       Make sure the timeout is set appropriately and that buffers are flushed before using this function.

       In auto mode, we can not choose the sensor slot to read (the default slot is ``1``).
       To read pressure of a specific slot using a query, see :func:`get_pressure`.

       :return: pressure reading from device (sensor slot ``1``) in Torr
       :raise serial.SerialException: Raised in case of serial communication errors
       :raise ValueError: Raised when response can not be converted to a float
       """
       response = self._read()
       logger.info(f'pressure read response: {response}')

       # device writes a string like "VAC=2.23e-05"
       if not response.startswith("VAC="):
           raise ValueError('Unexpected response to pressure reading')

       return float(response[4:])

