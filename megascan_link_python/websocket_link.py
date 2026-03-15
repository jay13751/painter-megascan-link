"""Module containing classes used to send data over the JS shim plugin."""

from __future__ import annotations

import json
import logging

from . import log


class WebsocketLink(object):
    """Single-use websocket client used to reach the Painter JS shim."""

    def __init__(self):
        from . import websocket

        self._create_connection = websocket.create_connection

    def send_payload(self, payload, settings: object, decision: object):
        try:
            ws = self._create_connection("ws://localhost:1212/")
            message = {
                "payload": payload.to_dict(),
                "settings": settings,
                "decision": decision,
            }
            log.LoggerLink.Log("Sending normalized payload to JS shim", logging.INFO)
            ws.send(json.dumps(message))
            ws.close()
        except Exception as exc:
            log.LoggerLink.Log("WEBSOCKET ERROR: {}".format(exc), logging.ERROR)
            log.LoggerLink.Log("Cannot send data to JS shim", logging.ERROR)
