# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

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
