"""Server package for JSON-RPC communication."""

from jojo_code.server.jsonrpc import JsonRpcServer, get_server
from jojo_code.server.handlers import register_handlers

__all__ = ["JsonRpcServer", "get_server", "register_handlers"]
