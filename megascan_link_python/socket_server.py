"""Socket server that receives Megascans payloads and normalizes them."""

from __future__ import annotations

import json
import logging
import select
import socket
import time

from . import config, log
from .payloads import normalize_payload
from .qt_compat import QtCore


class SocketServerThread(QtCore.QThread):
    onPayloadNormalized = QtCore.Signal(object)

    shouldClose = False
    shouldRestart = False
    started = False

    def run(self):
        logger = log.LoggerLink()
        conf = config.ConfigSettings()
        port = int(conf.getConfigSetting("Connection", "port"))
        timeout = int(conf.getConfigSetting("Connection", "timeout"))
        listeners = []

        for family, address in self._listener_specs(port):
            try:
                sock = socket.socket(family, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if family == socket.AF_INET6:
                    try:
                        sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
                    except OSError:
                        pass
                sock.bind(address)
                sock.listen(5)
                sock.setblocking(False)
                listeners.append(sock)
                logger.Log("Listening on {}".format(address), logging.INFO)
            except Exception as exc:
                logger.Log("Failed to bind {}: {}".format(address, exc), logging.DEBUG)

        if not listeners:
            logger.Log("Could not create any listening sockets", logging.ERROR)
            return

        self.started = True
        logger.Log("Socket server ready on port {} with timeout {}".format(port, timeout), logging.INFO)

        while True:
            if self._try_close_sockets(listeners):
                break
            try:
                readable, _, _ = select.select(listeners, [], [], timeout)
                if not readable:
                    logger.Log("Socket timeout", logging.DEBUG)
                    continue
                for listener in readable:
                    connection, client_address = listener.accept()
                    logger.Log("Connection from {}".format(client_address), logging.DEBUG)
                    self._read_connection(connection)
            except Exception as exc:
                logger.Log("Socket server loop error: {}".format(exc), logging.ERROR)

        self.shouldClose = False
        if self.shouldRestart:
            logger.Log("Restarting socket", logging.INFO)
            self.shouldRestart = False
            self.started = False
            self.run()
        self.started = False

    def _listener_specs(self, port: int):
        specs = [(socket.AF_INET, ("127.0.0.1", port))]
        if socket.has_ipv6:
            specs.append((socket.AF_INET6, ("::1", port, 0, 0)))
        return specs

    def _read_connection(self, connection):
        chunks = []
        try:
            connection.settimeout(2)
            while True:
                data = connection.recv(8192)
                if not data:
                    break
                chunks.append(data.decode("utf-8", "replace"))
        finally:
            connection.close()
        payload_data = "".join(chunks)
        if payload_data:
            self._handle_payload_data(payload_data)

    def _handle_payload_data(self, payload_data: str):
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

    def _try_close_sockets(self, listeners) -> bool:
        if self.shouldClose:
            log.LoggerLink.Log("Closing socket", logging.INFO)
            for sock in listeners:
                try:
                    sock.close()
                except OSError:
                    pass
            return True
        return False

    def restart(self):
        self.shouldClose = True
        self.shouldRestart = True

    def close(self):
        self.shouldClose = True
