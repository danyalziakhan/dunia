# MIT License

# Copyright (c) 2022 Danyal Zia Khan

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from typing_extensions import Self


class StateSaver(Protocol):
    async def save(self) -> None:
        """Save the state class object to pickle file (for tracking which pages have been crawled)."""
        ...


class StateLoader(Protocol):
    async def load(self) -> Self:
        """Load the state class object from pickle file."""
        ...


class StateFile(Protocol):
    @property
    def directory(self) -> str:
        """Full directory for saved pickle file."""
        ...

    @property
    def file(self) -> str:
        """Full path for saved pickle file."""
        ...

    async def exists(self) -> bool:
        """Whether the pickle file exists."""
        ...


class State(StateSaver, StateLoader, StateFile, Protocol):
    pass
