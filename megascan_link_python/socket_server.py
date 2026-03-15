"""Socket server that receives Megascans payloads and normalizes them."""

from __future__ import annotations

import io
import json
import logging
import socket
import time

from . import config, log
from .payloads import normalize_payload
from .qt_compat import QtCore


class SocketServerThread(QtCore.QThread):
    onRawPayloadReceived = QtCore.Signal(object)
    onPayloadNormalized = QtCore.Signal(object)

    shouldClose = False
    shouldRestart = False
    started = False

    def run(self):
        logger = log.LoggerLink()
        conf = config.ConfigSettings()
        port = int(conf.getConfigSetting("Connection", "port"))
        timeout = int(conf.getConfigSetting("Connection", "timeout"))

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        server_address = ("localhost", port)
        logger.Log(
            "Trying to start socket on {}:{} with timeout {}".format(
                server_address[0], server_address[1], timeout
            ),
            logging.INFO,
        )

        while not self.started:
            try:
                sock.bind(server_address)
                self.started = True
            except Exception as exc:
                logger.Log("Failed to start socket: {}. Retrying...".format(exc), logging.DEBUG)
                time.sleep(1)

        if not self.started:
            return

        sock.listen(1)
        while True:
            if self._try_close_socket(sock):
                break
            try:
                logger.Log("Waiting for a connection", logging.DEBUG)
                self._received_data = io.StringIO()
                self._connection, client_address = sock.accept()
                logger.Log("Connection from {}".format(client_address), logging.DEBUG)
                while True:
                    if self._try_close_socket(sock):
                        break
                    data = self._connection.recv(8192)
                    if data:
                        self._received_data.write(data.decode("utf-8", "replace"))
                    else:
                        break
            except socket.timeout:
                logger.Log("Socket timeout", logging.DEBUG)
            else:
                payload_data = self._received_data.getvalue()
                if payload_data:
                    self._handle_payload_data(payload_data)
            finally:
                if hasattr(self, "_connection"):
                    self._connection.close()
                    delattr(self, "_connection")
                if hasattr(self, "_received_data"):
                    self._received_data.close()

        self.shouldClose = False
        if self.shouldRestart:
            logger.Log("Restarting socket", logging.INFO)
            self.shouldRestart = False
            self.started = False
            self.run()
        self.started = False

    def _handle_payload_data(self, payload_data: str):
        self.onRawPayloadReceived.emit(payload_data)
        if config.ConfigSettings.checkIfOptionIsSet("General", "debug_payload_logging"):
            log.LoggerLink.Log("Raw payload: {}".format(payload_data), logging.DEBUG)
        try:
            raw_payload = json.loads(payload_data)
        except json.JSONDecodeError as exc:
            log.LoggerLink.Log("Failed to decode payload JSON: {}".format(exc), logging.ERROR)
            return

        try:
            normalized = normalize_payload(raw_payload)
        except Exception as exc:
            log.LoggerLink.Log("Failed to normalize payload: {}".format(exc), logging.ERROR)
            return

        self.onPayloadNormalized.emit(normalized)

    def _try_close_socket(self, sock) -> bool:
        if self.shouldClose:
            log.LoggerLink.Log("Closing socket", logging.INFO)
            sock.close()
            return True
        return False

    def restart(self):
        self.shouldClose = True
        self.shouldRestart = True

    def close(self):
        self.shouldClose = True
