from __future__ import annotations

from typing import Optional, TypeVar

T = TypeVar("T", bound="BaseLayer")


class BaseLayer:
    def __init__(self, payload: Optional["BaseLayer"] = None):
        self.payload: Optional[BaseLayer] = payload

    def build(self) -> bytes:
        """Convert the layer (including its payload) to bytes."""
        raise NotImplementedError

    def show(self, indent: int = 0) -> None:
        """Pretty-print the layer and recursively its payload."""
        raise NotImplementedError

    def __truediv__(self: T, other: "BaseLayer") -> T:
        """Overload the division operator to stack layers, Scapy-style.
        Returns the lower layer with its payload set to the upper layer.
        """
        if self.payload is None:
            self.payload = other
        else:
            # Delegate to the next layer to preserve chain order
            self.payload = self.payload / other
        return self

    def get_layer(self, name: str) -> Optional["BaseLayer"]:
        """Return the first layer in the stack matching class name `name`."""
        if self.__class__.__name__ == name:
            return self
        if self.payload:
            return self.payload.get_layer(name)
        return None        return None