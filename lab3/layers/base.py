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
        """Stack layers like Scapy: append `other` to the tail payload of `self`.
        Prevent cycles, and do it iteratively to avoid recursion issues.
        """
        if other is self:
            raise ValueError("Cannot set a layer as its own payload")
        # Find tail
        node: BaseLayer = self
        visited = {id(node)}
        while node.payload is not None:
            if id(node.payload) in visited:
                raise ValueError("Cycle detected in layer chain")
            visited.add(id(node.payload))
            node = node.payload
        node.payload = other
        return self

    def get_layer(self, name: str) -> Optional["BaseLayer"]:
        """Return the first layer in the stack matching class name `name`."""
        if self.__class__.__name__ == name:
            return self
        if self.payload:
            return self.payload.get_layer(name)
        return None