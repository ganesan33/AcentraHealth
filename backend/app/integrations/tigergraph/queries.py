"""
Graph Query Abstraction Layer for TigerGraph GSQL queries.
Contains named query definitions and execution helpers for fraud graph pattern detection.
"""

from typing import Dict, Any, List
from app.integrations.tigergraph.client import TigerGraphClient, tigergraph_client
from app.integrations.tigergraph.exceptions import TigerGraphQueryError
from app.core.logging import logger


class TigerGraphQueryRegistry:
    """Registry and executor for GSQL graph queries used by the Fraud Engine."""

    # Pre-defined query names expected to be installed on TigerGraph graph
    QUERY_SHARED_DEVICE_USERS = "find_shared_device_users"
    QUERY_SHARED_IP_USERS = "find_shared_ip_users"
    QUERY_USER_TRANSACTION_NETWORK = "find_user_transaction_network"
    QUERY_SUSPICIOUS_MERCHANT_CONNECTIONS = "find_suspicious_merchant_connections"
    QUERY_RELATED_TRANSACTIONS = "find_related_transactions"

    def __init__(self, client: TigerGraphClient = tigergraph_client) -> None:
        self.client = client

    def run_query(self, query_name: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute an installed GSQL query on TigerGraph with provided parameters.
        Returns graph query response payloads.
        """
        try:
            logger.info(f"Executing TigerGraph query '{query_name}' with parameters: {params}")
            conn = self.client.get_connection()
            result = conn.runInstalledQuery(query_name, params=params)
            return result
        except Exception as e:
            logger.error(f"Error executing TigerGraph query '{query_name}': {e}")
            raise TigerGraphQueryError(f"Query execution failed for '{query_name}'", details=str(e))

    # Abstract helper methods for named graph query invocations

    def find_shared_device_users(self, device_id: str) -> List[Dict[str, Any]]:
        """Placeholder query executor to find all users sharing the specified device."""
        return self.run_query(self.QUERY_SHARED_DEVICE_USERS, {"device_id": device_id})

    def find_shared_ip_users(self, ip_address: str) -> List[Dict[str, Any]]:
        """Placeholder query executor to find all users sharing the specified IP address."""
        return self.run_query(self.QUERY_SHARED_IP_USERS, {"ip_address": ip_address})

    def find_user_transaction_network(self, user_id: str, depth: int = 2) -> List[Dict[str, Any]]:
        """Placeholder query executor to traverse user transaction network up to specified hop depth."""
        return self.run_query(self.QUERY_USER_TRANSACTION_NETWORK, {"user_id": user_id, "depth": depth})

    def find_suspicious_merchant_connections(self, merchant_id: str) -> List[Dict[str, Any]]:
        """Placeholder query executor to find connected fraudulent accounts for a merchant."""
        return self.run_query(self.QUERY_SUSPICIOUS_MERCHANT_CONNECTIONS, {"merchant_id": merchant_id})

    def find_related_transactions(self, transaction_id: str) -> List[Dict[str, Any]]:
        """Placeholder query executor to find transactions linked by common devices/locations/IPs."""
        return self.run_query(self.QUERY_RELATED_TRANSACTIONS, {"transaction_id": transaction_id})


query_registry = TigerGraphQueryRegistry()
