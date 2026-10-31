"""User data needed by authentication and authorization workflows."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AuthenticatedUser:
    id: int
    username: str
    role: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row["id"],
            username=row["username"],
            role=row["role"],
        )
