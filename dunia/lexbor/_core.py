# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

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
