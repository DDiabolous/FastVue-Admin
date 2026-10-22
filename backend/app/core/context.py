from dataclasses import dataclass


@dataclass(frozen=True)
class AuditContext:
    operator: str
    ip: str
