from opcua import Client, ua
from opcua.ua import ExtensionObject
from opcua.common.node import Node
from typing import Dict, Tuple, Any
from concurrent.futures import TimeoutError as FuturesTimeoutError
from threading import Lock
import logging

from .config import PLC_ENDPOINT, NODE_IDS

logger = logging.getLogger(__name__)


class _KeepAliveHandler:
    """
    Subscription handler – we don't actually care about the value,
    but this keeps the session active and lets us log status changes.
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def datachange_notification(self, node, val, data):
        # No-op: we don't need to do anything with this
        pass

    def event_notification(self, event):
        pass

    def status_change_notification(self, status):
        # This gets called if the subscription / session status changes
        self.logger.warning("OPC: Subscription status change: %s", status)


class OpcUaWrapper:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self._lock = Lock()
        self.client: Client | None = None
        self.node_cache: Dict[str, Tuple[Node, ua.VariantType]] = {}

        # Keepalive subscription state
        self._sub = None
        self._keepalive_handle = None

        self._connect()

    def _unwrap_extension_object(value):
        """
        If value is an ExtensionObject or Variant wrapping one,
        return the underlying struct (its Body). Otherwise, return as is.
        """
        # Variant case (node.get_value() can already return plain Python, but just in case)
        if hasattr(value, "Value"):
            value = value.Value

        # Raw ExtensionObject → try to unwrap Body
        if isinstance(value, ExtensionObject):
            if hasattr(value, "Body") and value.Body is not None:
                return value.Body

        return value


    # ------------------------
    # Connection management
    # ------------------------
    def _connect(self) -> None:
        """
        Create a new client, connect, and rebuild the node cache.
        Also set up a keepalive subscription so the session never goes idle.
        """
        logger.info("OPC: Connecting client to %s", self.endpoint)
        self.client = Client(self.endpoint)
        self.client.connect()

        # 🔑 Teach the client about custom structs / ExtensionObjects
        try:
            self.client.load_data_type_definitions()
            logger.info("OPC: Loaded data type definitions")
        except Exception:
            logger.exception("OPC: Failed to load data type definitions")

        # Rebuild node cache
        self.node_cache.clear()
        for key, nodeid in NODE_IDS.items():
            node = self.client.get_node(nodeid)
            vtype = node.get_data_type_as_variant_type()
            self.node_cache[key] = (node, vtype)

        logger.info("OPC: Connected and cached %d nodes", len(self.node_cache))

        # Create or recreate keepalive subscription
        self._setup_keepalive_subscription()

    def _setup_keepalive_subscription(self) -> None:
        """
        Create a subscription on a 'stable' node (e.g. ServerStatus.CurrentTime)
        so the session stays active and doesn't hit idle timeout.
        """
        if self.client is None:
            return

        try:
            # Clean up any previous subscription
            if self._sub is not None and self._keepalive_handle is not None:
                try:
                    self._sub.unsubscribe(self._keepalive_handle)
                    self._sub.delete()
                except Exception:
                    logger.exception("OPC: Failed to clean up existing subscription")

            handler = _KeepAliveHandler(logger)
            # Sampling / publishing every 5 seconds is plenty to keep session alive
            self._sub = self.client.create_subscription(5000, handler)

            # Use the standard ServerStatus CurrentTime node as the keepalive source
            keepalive_node = self.client.get_node(ua.ObjectIds.Server_ServerStatus_CurrentTime)
            self._keepalive_handle = self._sub.subscribe_data_change(keepalive_node)

            logger.info("OPC: Keepalive subscription created")
        except Exception:
            logger.exception("OPC: Failed to create keepalive subscription")

    # Optional: if you still want a reconnect helper for other code paths
    def _reconnect(self) -> None:
        """
        Force a reconnect – you may still want this for explicit manual calls,
        but it will no longer be triggered automatically for BrokenPipe in read().
        """
        logger.warning("OPC: Reconnecting client")
        if self.client is not None:
            try:
                self.client.disconnect()
            except Exception:
                logger.exception("OPC: Error while disconnecting stale client")

        self.client = None
        self._sub = None
        self._keepalive_handle = None
        self._connect()

    # ------------------------
    # Helpers
    # ------------------------
    def _coerce_value(self, vtype: ua.VariantType, value: Any) -> Any:
        """
        Coerce Python value into something compatible with the target VariantType.
        """
        if vtype in (
            ua.VariantType.Int16, ua.VariantType.Int32, ua.VariantType.Int64,
            ua.VariantType.UInt16, ua.VariantType.UInt32, ua.VariantType.UInt64,
            ua.VariantType.SByte, ua.VariantType.Byte,
        ):
            try:
                return int(value)
            except Exception:
                return 0

        if vtype in (ua.VariantType.Float, ua.VariantType.Double):
            try:
                return float(value)
            except Exception:
                return 0.0

        if vtype == ua.VariantType.Boolean:
            return bool(value)

        # Strings / others – just pass through
        return value

    def _get_node_entry(self, key: str) -> Tuple[Node, ua.VariantType]:
        if key not in self.node_cache:
            raise KeyError(f"Unknown OPC key: {key}")
        return self.node_cache[key]

    # ------------------------
    # Public API
    # ------------------------
    def read(self, key: str):
        """
        Read a value by logical key.
        We only auto-retry on FuturesTimeoutError here.
        BrokenPipeError etc. will bubble out so you can see them.
        """
        with self._lock:
            node, _ = self._get_node_entry(key)

            try:
                return node.get_value()
            except FuturesTimeoutError:
                logger.warning("OPC: Timeout on read '%s', reconnecting and retrying", key)
                self._reconnect()
                node, _ = self._get_node_entry(key)
                return node.get_value()

    def read_direct(self, nodeid: str):
        """
        Read a value directly by node ID (not using NODE_IDS mapping).
        """
        with self._lock:
            try:
                node = self.client.get_node(nodeid)
                return node.get_value()
            except FuturesTimeoutError:
                logger.warning("OPC: Timeout on read_direct '%s', reconnecting and retrying", nodeid)
                self._reconnect()
                node = self.client.get_node(nodeid)
                return node.get_value()

    def write(self, key: str, value: Any) -> None:
        """
        Write a value by logical key.
        - Coerces value based on the node's data type.
        - Supports both scalars and arrays (Python list/tuple).
        - On TimeoutError, reconnect and retry once.
        """
        with self._lock:
            node, vtype = self._get_node_entry(key)

            def _coerce_for_type(vtype: ua.VariantType, val: Any) -> Any:
                # Reuse existing logic, but apply it per-element if needed
                if isinstance(val, (list, tuple)):
                    return [self._coerce_value(vtype, x) for x in val]
                return self._coerce_value(vtype, val)

            coerced = _coerce_for_type(vtype, value)

            try:
                node.set_value(ua.Variant(coerced, vtype))
            except FuturesTimeoutError:
                logger.warning("OPC: Timeout on write '%s', reconnecting and retrying", key)
                self._reconnect()
                node, vtype = self._get_node_entry(key)
                coerced = _coerce_for_type(vtype, value)
                node.set_value(ua.Variant(coerced, vtype))

# Single shared instance
opc = OpcUaWrapper(PLC_ENDPOINT)