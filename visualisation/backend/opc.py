from opcua import Client, ua
from opcua.ua import ExtensionObject
from opcua.common.node import Node
from typing import Dict, Tuple, Any
from concurrent.futures import TimeoutError as FuturesTimeoutError
from threading import RLock
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
        self._lock = RLock()
        self.client: Client | None = None
        self.node_cache: Dict[str, Tuple[Node, ua.VariantType]] = {}

        # Keepalive subscription state
        self._sub = None
        self._keepalive_handle = None

        try:
            self._connect()
        except Exception:
            logger.error("OPC: Initial connection failed to %s. Will retry on first access.", endpoint)

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
        with self._lock:
            if self.client is not None:
                try:
                    self.client.disconnect()
                except Exception:
                    pass
                self.client = None

            logger.info("OPC: Connecting client to %s", self.endpoint)
            new_client = Client(self.endpoint)
            try:
                new_client.connect()

                # 🔑 Teach the client about custom structs / ExtensionObjects
                try:
                    new_client.load_type_definitions()
                    logger.info("OPC: Loaded data type definitions")
                except Exception:
                    logger.warning("OPC: Failed to load data type definitions (non-critical)")

                # Rebuild node cache
                new_node_cache = {}
                for key, nodeid in NODE_IDS.items():
                    node = new_client.get_node(nodeid)
                    vtype = node.get_data_type_as_variant_type()
                    new_node_cache[key] = (node, vtype)

                # Successfully connected and prepared
                self.client = new_client
                self.node_cache = new_node_cache
                logger.info("OPC: Connected and cached %d nodes", len(self.node_cache))

                # Create or recreate keepalive subscription
                self._setup_keepalive_subscription()

            except Exception:
                logger.exception("OPC: Failed to connect to %s", self.endpoint)
                try:
                    new_client.disconnect()
                except:
                    pass
                raise

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
        with self._lock:
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
    def _execute_with_retry(self, operation, *args, **kwargs):
        """
        Execute an OPC operation with retry logic for connection errors.
        """
        max_retries = 3
        for attempt in range(max_retries):
            current_client = None
            try:
                with self._lock:
                    if self.client is None:
                        self._connect()
                    current_client = self.client
                    return operation(*args, **kwargs)
            except (FuturesTimeoutError, BrokenPipeError, ConnectionError, OSError) as e:
                logger.warning("OPC: Operation failed (attempt %d/%d): %s", attempt + 1, max_retries, e)
                if attempt < max_retries - 1:
                    with self._lock:
                        # Only reconnect if the client hasn't been changed by another thread
                        if self.client is current_client:
                            try:
                                self._reconnect()
                            except Exception:
                                logger.exception("OPC: Reconnection attempt failed")
                        else:
                            logger.info("OPC: Skipping reconnect as another thread already reconnected")
                else:
                    logger.error("OPC: Operation failed after %d retries", max_retries)
                    raise
            except Exception as e:
                logger.exception("OPC: Unexpected error during operation")
                raise

    def read(self, key: str):
        """
        Read a value by logical key.
        Handles reconnection and retries automatically.
        """
        def _read_op():
            node, _ = self._get_node_entry(key)
            return node.get_value()

        return self._execute_with_retry(_read_op)

    def read_direct(self, nodeid: str):
        """
        Read a value directly by node ID (not using NODE_IDS mapping).
        """
        return self._execute_with_retry(lambda: self.client.get_node(nodeid).get_value())

    def write(self, key: str, value: Any) -> None:
        """
        Write a value by logical key.
        - Coerces value based on the node's data type.
        - Supports both scalars and arrays (Python list/tuple).
        - Handles reconnection and retries automatically.
        """
        def _write_op():
            node, vtype = self._get_node_entry(key)

            def _coerce_for_type(vt: ua.VariantType, val: Any) -> Any:
                if isinstance(val, (list, tuple)):
                    return [self._coerce_value(vt, x) for x in val]
                return self._coerce_value(vt, val)

            coerced = _coerce_for_type(vtype, value)
            variant = ua.Variant(coerced, vtype)
            node.set_value(variant)

        return self._execute_with_retry(_write_op)

# Single shared instance
opc = OpcUaWrapper(PLC_ENDPOINT)