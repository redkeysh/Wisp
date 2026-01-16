"""Policy engine for evaluating capability-based access control."""

import logging
from typing import Any

from sqlalchemy import select

from wisp_framework.context import WispContext
from wisp_framework.db.models import PolicyRule
from wisp_framework.services.db import DatabaseService

logger = logging.getLogger(__name__)


class PolicyResult:
    """Result of a policy check."""

    def __init__(
        self,
        allowed: bool,
        reason: str,
        explain_trace: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize policy result.

        Args:
            allowed: Whether access is allowed
            reason: Explanation of the decision
            explain_trace: List of rules that were evaluated
        """
        self.allowed = allowed
        self.reason = reason
        self.explain_trace = explain_trace or []


class PolicyEngine:
    """Engine for evaluating policy rules and capabilities."""

    def __init__(self, db_service: DatabaseService | None = None) -> None:
        """Initialize policy engine.

        Args:
            db_service: Optional database service for rule persistence
        """
        self._db_service = db_service

    async def check(
        self, capability: str, ctx: WispContext
    ) -> PolicyResult:
        """Check if a capability is allowed for the given context.

        Args:
            capability: Capability string (e.g., "moderation.kick")
            ctx: WispContext with user, guild, channel, etc.

        Returns:
            PolicyResult with allowed status and explanation
        """
        if not self._db_service or not self._db_service.session_factory:
            # No database - default to allow
            return PolicyResult(
                allowed=True,
                reason="No policy engine configured, defaulting to allow",
            )

        try:
            # Get all applicable rules
            rules = await self._get_applicable_rules(capability, ctx)

            if not rules:
                # No rules found - default to allow
                return PolicyResult(
                    allowed=True,
                    reason="No policy rules found, defaulting to allow",
                )

            # Evaluate rules in priority order (higher priority first)
            # More specific scopes override less specific ones
            # Explicit deny overrides allow
            explain_trace = []
            allow_rules = []
            deny_rules = []

            for rule in rules:
                explain_trace.append({
                    "rule_id": rule.id,
                    "scope_type": rule.scope_type,
                    "scope_id": rule.scope_id,
                    "action": rule.action,
                    "priority": rule.priority,
                })

                if rule.action == "deny":
                    deny_rules.append(rule)
                else:
                    allow_rules.append(rule)

            # Explicit deny takes precedence
            if deny_rules:
                highest_priority_deny = max(deny_rules, key=lambda r: r.priority)
                return PolicyResult(
                    allowed=False,
                    reason=f"Denied by rule {highest_priority_deny.id} at {highest_priority_deny.scope_type} scope",
                    explain_trace=explain_trace,
                )

            # Check for allow rules
            if allow_rules:
                highest_priority_allow = max(allow_rules, key=lambda r: r.priority)
                return PolicyResult(
                    allowed=True,
                    reason=f"Allowed by rule {highest_priority_allow.id} at {highest_priority_allow.scope_type} scope",
                    explain_trace=explain_trace,
                )

            # Should not reach here, but default to deny for safety
            return PolicyResult(
                allowed=False,
                reason="No applicable allow rules found",
                explain_trace=explain_trace,
            )

        except Exception as e:
            logger.error(f"Policy check failed: {e}", exc_info=True)
            # Fail closed - deny access on error
            return PolicyResult(
                allowed=False,
                reason=f"Policy check error: {str(e)}",
            )

    async def _get_applicable_rules(
        self, capability: str, ctx: WispContext
    ) -> list[PolicyRule]:
        """Get all applicable policy rules for a capability and context.

        Args:
            capability: Capability string
            ctx: WispContext

        Returns:
            List of applicable PolicyRule instances
        """
        async with self._db_service.session_factory() as session:
            # Build query for applicable rules
            # Scope hierarchy: global → guild → channel → role → user
            # We need to get rules at all applicable scopes

            conditions = [PolicyRule.capability == capability]

            # Get rules at different scopes
            scope_conditions = [
                PolicyRule.scope_type == "global",
            ]

            if ctx.guild_id:
                scope_conditions.append(
                    (PolicyRule.scope_type == "guild") & (PolicyRule.scope_id == ctx.guild_id)
                )

            if ctx.channel_id:
                scope_conditions.append(
                    (PolicyRule.scope_type == "channel") & (PolicyRule.scope_id == ctx.channel_id)
                )

            # Note: role and user scopes would require additional context
            # For now, we'll focus on guild and channel scopes

            stmt = select(PolicyRule).where(
                *conditions,
                # Match any of the scope conditions
                # This is simplified - full implementation would check roles/users
            )

            # For simplicity, get all rules and filter in Python
            # In production, this should be optimized with proper SQL
            result = await session.execute(stmt)
            all_rules = result.scalars().all()

            # Filter to applicable scopes
            applicable_rules = []
            for rule in all_rules:
                if rule.scope_type == "global":
                    applicable_rules.append(rule)
                elif rule.scope_type == "guild" and ctx.guild_id and rule.scope_id == ctx.guild_id:
                    applicable_rules.append(rule)
                elif rule.scope_type == "channel" and ctx.channel_id and rule.scope_id == ctx.channel_id:
                    applicable_rules.append(rule)
                # Role and user scopes would require additional checks

            # Sort by priority (higher first)
            applicable_rules.sort(key=lambda r: r.priority, reverse=True)

            return applicable_rules

    async def add_rule(
        self,
        scope_type: str,
        scope_id: int | None,
        capability: str,
        action: str,
        priority: int = 0,
    ) -> PolicyRule:
        """Add a policy rule.

        Args:
            scope_type: Scope type (global, guild, channel, role, user)
            scope_id: Scope ID (None for global)
            capability: Capability string
            action: Action ("allow" or "deny")
            priority: Priority (higher = more important)

        Returns:
            Created PolicyRule instance
        """
        if not self._db_service or not self._db_service.session_factory:
            raise RuntimeError("Database service not available")

        async with self._db_service.session_factory() as session:
            rule = PolicyRule(
                scope_type=scope_type,
                scope_id=scope_id,
                capability=capability,
                action=action,
                priority=priority,
            )
            session.add(rule)
            await session.commit()
            await session.refresh(rule)
            return rule

    async def list_rules(
        self, capability: str | None = None, scope_type: str | None = None
    ) -> list[PolicyRule]:
        """List policy rules.

        Args:
            capability: Optional capability filter
            scope_type: Optional scope type filter

        Returns:
            List of PolicyRule instances
        """
        if not self._db_service or not self._db_service.session_factory:
            return []

        async with self._db_service.session_factory() as session:
            conditions = []
            if capability:
                conditions.append(PolicyRule.capability == capability)
            if scope_type:
                conditions.append(PolicyRule.scope_type == scope_type)

            stmt = select(PolicyRule)
            if conditions:
                stmt = stmt.where(*conditions)

            result = await session.execute(stmt)
            return list(result.scalars().all())
