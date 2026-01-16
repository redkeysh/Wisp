"""Policy engine for capability-based access control."""

from wisp_framework.policy.capabilities import CapabilityRegistry
from wisp_framework.policy.decorators import requires_capability
from wisp_framework.policy.engine import PolicyEngine

__all__ = ["PolicyEngine", "CapabilityRegistry", "requires_capability"]
