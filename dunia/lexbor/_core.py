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

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from selectolax.lexbor import LexborHTMLParser, LexborNode


async def css_first(document_or_node: LexborHTMLParser | LexborNode, selector: str):
    if (splitter := ",") in selector or (splitter := ", ") in selector:
        for selector in selector.split(splitter):
            if html_element := await asyncio.to_thread(
                document_or_node.css_first, selector, default=None
            ):
                return html_element
    elif html_element := await asyncio.to_thread(
        document_or_node.css_first, selector, default=None
    ):
        return html_element


async def css(document_or_node: LexborHTMLParser | LexborNode, selector: str):
    if (splitter := ",") in selector or (splitter := ", ") in selector:
        tasks = (
            asyncio.to_thread(document_or_node.css, selector)
            for selector in selector.split(splitter)
        )
        all_css = await asyncio.gather(*tasks)
        return [
            html_element for html_elements in all_css for html_element in html_elements
        ]

    return await asyncio.to_thread(document_or_node.css, selector)
