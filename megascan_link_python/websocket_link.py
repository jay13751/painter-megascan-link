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
            action = decision.get("action", "process_payload") if isinstance(decision, dict) else "process_payload"
            transport_payload = payload.to_transport_dict(action)
            message = {
                "payload": transport_payload,
                "data": transport_payload.get("assets", []),
                "settings": settings,
                "decision": decision,
            }
            message_json = json.dumps(message)
            log.LoggerLink.Log(
                "Sending {} assets to JS shim for action {} ({} bytes)".format(
                    len(transport_payload.get("assets", [])),
                    action,
                    len(message_json.encode("utf-8")),
                ),
                logging.INFO,
            )
            ws.send(message_json)
            ws.close()
        except Exception as exc:
            log.LoggerLink.Log("WEBSOCKET ERROR: {}".format(exc), logging.ERROR)
            log.LoggerLink.Log("Cannot send data to JS shim", logging.ERROR)
