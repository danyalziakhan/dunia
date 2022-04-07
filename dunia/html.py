# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

from __future__ import annotations

from typing import Protocol


class HTMLSaver(Protocol):
    async def save(self, content: str) -> None:
        """Save HTML source content for fast reloading/caching (for LXML parsing or some custom HTML parsing)."""
        ...


class HTMLLoader(Protocol):
    async def load(self) -> str:
        """Load the HTML source content from HTML file."""
        ...


class HTMLFile(Protocol):
    @property
    def directory(self) -> str:
        """Full directory for saved HTML file."""
        ...

    @property
    def file(self) -> str:
        """Full path for saved HTML file."""
        ...

    async def exists(self) -> bool:
        """Whether the saved HTML file exists."""
        ...


class HTML(HTMLSaver, HTMLLoader, HTMLFile, Protocol):
    pass
