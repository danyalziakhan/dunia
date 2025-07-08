# MIT License

# Copyright (c) 2022-2025 Danyal Zia Khan

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

from typing import Protocol, runtime_checkable

from dunia.element import Element


class QuerySelector(
    Protocol,
):
    async def text_content(
        self, selector: str, *, timeout: int | None = None
    ) -> str | None: ...

    async def inner_text(
        self, selector: str, *, timeout: int | None = None
    ) -> str | None: ...

    async def get_attribute(
        self, selector: str, name: str, *, timeout: int | None = None
    ) -> str | None: ...

    async def query_selector(self, selector: str) -> Element | None: ...

    async def query_selector_all(self, selector: str) -> list[Element]: ...


@runtime_checkable
class Document(QuerySelector, Protocol):
    pass
