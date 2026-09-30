from typing import Optional, Dict, Any, List
from app.integrations.tigergraph.client import TigerGraphClient, tigergraph_client
from app.integrations.tigergraph.exceptions import TigerGraphUpsertError
from app.core.logging import logger


class TigerGraphService:
    """
    High-level application service for TigerGraph domain operations.
    Encapsulates schema vertex/edge creation and query invocation, hiding pyTigerGraph details.
    """

    def __init__(self, client: TigerGraphClient = tigergraph_client) -> None:
        self.client = client

    def _upsert_vertex(self, vertex_type: str, vertex_id: str, attributes: Dict[str, Any]) -> bool:
        """Internal helper to upsert a single vertex into TigerGraph."""
        try:
            conn = self.client.get_connection()
            # Clean empty attributes
            clean_attrs = {k: v for k, v in attributes.items() if v is not None}
            res = conn.upsertVertex(vertex_type, vertex_id, attributes=clean_attrs)
            logger.info(f"Upserted vertex {vertex_type}:{vertex_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert vertex {vertex_type}:{vertex_id} - {e}")
            raise TigerGraphUpsertError(f"Vertex upsert failed for {vertex_type}:{vertex_id}", details=str(e))

    def _upsert_edge(
        self,
        source_type: str,
        source_id: str,
        edge_type: str,
        target_type: str,
        target_id: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Internal helper to upsert a directed edge relationship between two vertices."""
        try:
            conn = self.client.get_connection()
            clean_attrs = {k: v for k, v in (attributes or {}).items() if v is not None}
            conn.upsertEdge(source_type, source_id, edge_type, target_type, target_id, attributes=clean_attrs)
            logger.info(f"Upserted edge {source_type}:{source_id} -[{edge_type}]-> {target_type}:{target_id}")
            return True
        except Exception as e:
            logger.error(
                f"Failed to upsert edge {source_type}:{source_id} -[{edge_type}]-> {target_type}:{target_id} - {e}"
            )
            raise TigerGraphUpsertError(f"Edge upsert failed for relationship {edge_type}", details=str(e))

    # --- Vertex Upsert Operations ---

    def upsert_user(self, user_id: str, name: str = "", created_at: Optional[str] = None) -> bool:
        """Upsert a User vertex."""
        return self._upsert_vertex("User", user_id, {"name": name, "created_at": created_at})

    def upsert_account(
        self,
        account_id: str,
        user_id: str = "",
        account_type: str = "",
        created_at: Optional[str] = None,
    ) -> bool:
        """Upsert an Account vertex."""
        return self._upsert_vertex(
            "Account",
            account_id,
            {"user_id": user_id, "account_type": account_type, "created_at": created_at},
        )

    def upsert_transaction(
        self,
        transaction_id: str,
        user_id: str = "",
        account_id: str = "",
        amount: float = 0.0,
        currency: str = "USD",
        merchant_id: str = "",
        device_id: str = "",
        location_id: str = "",
        ip_address: str = "",
        timestamp: Optional[str] = None,
    ) -> bool:
        """Upsert a Transaction vertex."""
        return self._upsert_vertex(
            "Transaction",
            transaction_id,
            {
                "user_id": user_id,
                "account_id": account_id,
                "amount": amount,
                "currency": currency,
                "merchant_id": merchant_id,
                "device_id": device_id,
                "location_id": location_id,
                "ip_address": ip_address,
                "timestamp": timestamp,
            },
        )

    def upsert_merchant(
        self, merchant_id: str, name: str = "", category: str = "", location: str = ""
    ) -> bool:
        """Upsert a Merchant vertex."""
        return self._upsert_vertex(
            "Merchant", merchant_id, {"name": name, "category": category, "location": location}
        )

    def upsert_device(self, device_id: str, device_type: str = "") -> bool:
        """Upsert a Device vertex."""
        return self._upsert_vertex("Device", device_id, {"device_type": device_type})

    def upsert_location(
        self,
        location_id: str,
        latitude: float = 0.0,
        longitude: float = 0.0,
        city: str = "",
        country: str = "",
    ) -> bool:
        """Upsert a Location vertex."""
        return self._upsert_vertex(
            "Location",
            location_id,
            {
                "latitude": latitude,
                "longitude": longitude,
                "city": city,
                "country": country,
            },
        )

    def upsert_ip(self, ip_address: str, country: str = "") -> bool:
        """Upsert an IP vertex."""
        return self._upsert_vertex("IP", ip_address, {"country": country})

    # --- Relationship / Edge Operations ---

    def create_user_account_relationship(self, user_id: str, account_id: str) -> bool:
        """Create OWNS relationship between User and Account."""
        return self._upsert_edge("User", user_id, "OWNS", "Account", account_id)

    def create_account_transaction_relationship(self, account_id: str, transaction_id: str) -> bool:
        """Create MADE relationship between Account and Transaction."""
        return self._upsert_edge("Account", account_id, "MADE", "Transaction", transaction_id)

    def create_transaction_merchant_relationship(self, transaction_id: str, merchant_id: str) -> bool:
        """Create AT_MERCHANT relationship between Transaction and Merchant."""
        return self._upsert_edge("Transaction", transaction_id, "AT_MERCHANT", "Merchant", merchant_id)

    def create_transaction_device_relationship(self, transaction_id: str, device_id: str) -> bool:
        """Create FROM_DEVICE relationship between Transaction and Device."""
        return self._upsert_edge("Transaction", transaction_id, "FROM_DEVICE", "Device", device_id)

    def create_transaction_location_relationship(self, transaction_id: str, location_id: str) -> bool:
        """Create FROM_LOCATION relationship between Transaction and Location."""
        return self._upsert_edge("Transaction", transaction_id, "FROM_LOCATION", "Location", location_id)

    def create_transaction_ip_relationship(self, transaction_id: str, ip_address: str) -> bool:
        """Create FROM_IP relationship between Transaction and IP."""
        return self._upsert_edge("Transaction", transaction_id, "FROM_IP", "IP", ip_address)

    def create_device_user_relationship(self, device_id: str, user_id: str) -> bool:
        """Create USED_BY relationship between Device and User."""
        return self._upsert_edge("Device", device_id, "USED_BY", "User", user_id)

    # --- Orchestration Helper ---

    def ingest_full_transaction(self, tx: Dict[str, Any]) -> bool:
        """
        Orchestrates full vertex and edge insertion for a complete transaction entity graph.
        Used by API endpoints and fraud processing pipelines.
        """
        tx_id = str(tx.get("transaction_id", tx.get("id", "")))
        user_id = str(tx.get("user_id", ""))
        account_id = str(tx.get("account_id", ""))
        merchant_id = str(tx.get("merchant_id", ""))
        device_id = str(tx.get("device_id", ""))
        location_id = str(tx.get("location_id", ""))
        ip_address = str(tx.get("ip_address", ""))

        # 1. Upsert Vertices
        if user_id:
            self.upsert_user(user_id, name=str(tx.get("user_name", "")))
        if account_id:
            self.upsert_account(account_id, user_id=user_id, account_type=str(tx.get("account_type", "")))
        if merchant_id:
            self.upsert_merchant(merchant_id, name=str(tx.get("merchant_name", "")))
        if device_id:
            self.upsert_device(device_id, device_type=str(tx.get("device_type", "")))
        if location_id:
            self.upsert_location(
                location_id,
                city=str(tx.get("city", "")),
                country=str(tx.get("country", "")),
            )
        if ip_address:
            self.upsert_ip(ip_address, country=str(tx.get("ip_country", "")))

        self.upsert_transaction(
            transaction_id=tx_id,
            user_id=user_id,
            account_id=account_id,
            amount=float(tx.get("amount", 0.0)),
            currency=str(tx.get("currency", "USD")),
            merchant_id=merchant_id,
            device_id=device_id,
            location_id=location_id,
            ip_address=ip_address,
            timestamp=tx.get("timestamp"),
        )

        # 2. Upsert Edges
        if user_id and account_id:
            self.create_user_account_relationship(user_id, account_id)
        if account_id and tx_id:
            self.create_account_transaction_relationship(account_id, tx_id)
        if tx_id and merchant_id:
            self.create_transaction_merchant_relationship(tx_id, merchant_id)
        if tx_id and device_id:
            self.create_transaction_device_relationship(tx_id, device_id)
        if tx_id and location_id:
            self.create_transaction_location_relationship(tx_id, location_id)
        if tx_id and ip_address:
            self.create_transaction_ip_relationship(tx_id, ip_address)
        if device_id and user_id:
            self.create_device_user_relationship(device_id, user_id)

        return True


tigergraph_service = TigerGraphService()


def get_tigergraph_service() -> TigerGraphService:
    """FastAPI Dependency injector for TigerGraphService."""
    return tigergraph_service
