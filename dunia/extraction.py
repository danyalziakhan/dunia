# Copyright (c) 2021-present, GYU Co., Ltd. All rights reserved.

# Author: Danyal Zia Khan
# Email: danyal6870@gmail.com
# Copyright (c) 2020-2022 Danyal Zia Khan
# All rights reserved.

# USE OF THIS SOFTWARE AND DISTRIBUTION OUTSIDE THE GYU COMPANY IS STRICTLY PROHIBITED. PLEASE REPORT ANY SUCH USE TO THE COMPANY.

from __future__ import annotations

import asyncio

from typing import TYPE_CHECKING, cast, overload

import backoff
import lxml.html as lxml

from selectolax.lexbor import LexborHTMLParser
from selectolax.parser import HTMLParser
from throttler import throttle

from dunia.aio import with_timeout
from dunia.error import (
    PlaywrightError,
    PlaywrightTimeoutError,
    TimeoutException,
    backoff_hdlr,
)
from dunia.lexbor import LexborDocument
from dunia.log import warning
from dunia.lxml import LXMLDocument
from dunia.modest import ModestDocument


if TYPE_CHECKING:
    from typing import Callable, Literal

    from dunia.browser import Browser
    from dunia.html import HTML
    from dunia.page import Page


# ? Sometimes websites are throwing JavaScript exceptions in devtools console, which makes the page stuck on "networkidle", so let's make "load" by default for now
@backoff.on_exception(
    backoff.expo,
    TimeoutException,
    max_tries=5,
    on_backoff=backoff_hdlr,
)
async def visit_link(
    page: Page,
    product_href: str,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):
    """
    Visit the page (url) and retry for 5 times if the navigation has been failed within the configured timeout
    """
    try:
        await page.goto(product_href, wait_until=wait_until)
    except (PlaywrightTimeoutError, PlaywrightError) as err:
        raise TimeoutException(err) from err


async def change_page(
    page: Page,
    page_no: int,
    next_page_url: Callable[[str, int], str],
) -> str:
    """
    Navigate to the next page according to the navigation strategy
    """
    category_url = next_page_url(page.url, page_no)
    # ? We are starting from 1 because the first element (at index 0) is the current page that we don't want to navigate to again
    if page_no != 1:
        await visit_link(page, category_url)

    return category_url


async def load_html(
    html: HTML,
):

    return await html.load() if await html.exists() else None


async def load_from_html(
    page: Page,
    html: HTML,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):

    if not await html.exists():
        return False

    try:
        await page.set_content(
            await html.load(),
            wait_until=wait_until,
        )
    except PlaywrightTimeoutError:
        return False

    return True


async def load_content(
    *,
    browser: Browser,
    url: str,
    html: HTML,
    page_throttle_rate_limit: int,
    async_timeout: int,
    save_html: bool,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):

    if save_html:
        if await html.exists():
            content = await html.load()
        else:
            try:
                content = await fetch_content(browser, url, page_throttle_rate_limit)
            except UnicodeDecodeError:
                visit = with_timeout(async_timeout)(  # type: ignore
                    throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                        visit_link
                    )
                )
                page = await browser.new_page()
                await visit(page, url, wait_until=wait_until)
                content = await page.content()
                await page.close()
            await html.save(content)
    else:
        try:
            content = await fetch_content(browser, url, page_throttle_rate_limit)
        except UnicodeDecodeError:
            visit = with_timeout(async_timeout)(  # type: ignore
                throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                    visit_link
                )
            )
            page = await browser.new_page()
            await visit(page, url, wait_until=wait_until)
            content = await page.content()
            await page.close()

    return content


async def reload_content(
    *,
    browser: Browser,
    url: str,
    html: HTML,
    page_throttle_rate_limit: int,
    async_timeout: int,
    save_html: bool,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):

    try:
        content = await fetch_content(browser, url, page_throttle_rate_limit)
    except UnicodeDecodeError:
        visit = with_timeout(async_timeout)(  # type: ignore
            throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                visit_link
            )
        )
        page = await browser.new_page()
        await visit(page, url, wait_until=wait_until)
        content = await page.content()
        await page.close()

    if save_html:
        await html.save(content)

    return content


@backoff.on_exception(
    backoff.expo,
    TimeoutException,
    max_tries=5,
    on_backoff=backoff_hdlr,
)
async def fetch_content(browser: Browser, url: str, rate_limit: int):
    get = throttle(rate_limit=rate_limit, period=1.0)(  # type: ignore
        browser.request.get
    )
    try:
        return cast(str, await (await get(url)).text())
    except (PlaywrightTimeoutError, PlaywrightError) as err:
        raise TimeoutException(err) from err
    except UnicodeDecodeError as err:
        raise err from err


async def load_page(
    *,
    browser: Browser,
    url: str,
    html: HTML,
    page_throttle_rate_limit: int,
    async_timeout: int,
    save_html: bool,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):

    if save_html:
        if await html.exists():
            content = await html.load()
        else:
            visit = with_timeout(async_timeout)(  # type: ignore
                throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                    visit_link
                )
            )
            page = await browser.new_page()
            await visit(page, url, wait_until=wait_until)
            content = await page.content()
            await html.save(content)

            await page.close()
    else:
        visit = with_timeout(async_timeout)(  # type: ignore
            throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                visit_link
            )
        )
        page = await browser.new_page()
        await visit(page, url, wait_until=wait_until)
        content = await page.content()

        await page.close()

    return content


async def reload_page(
    *,
    browser: Browser,
    url: str,
    html: HTML,
    page_throttle_rate_limit: int,
    async_timeout: int,
    save_html: bool,
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
):

    visit = with_timeout(async_timeout)(  # type: ignore
        throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
            visit_link
        )
    )
    page = await browser.new_page()
    await visit(page, url, wait_until=wait_until)
    content = await page.content()

    if save_html:
        await html.save(content)

    await page.close()

    return content


@overload
async def parse_document(
    content: str,
    *,
    engine: Literal["lxml"],
) -> LXMLDocument | None:
    ...


@overload
async def parse_document(
    content: str,
    *,
    engine: Literal["modest"],
) -> ModestDocument | None:
    ...


@overload
async def parse_document(
    content: str,
    *,
    engine: Literal["lexbor"],
) -> LexborDocument | None:
    ...


async def parse_document(
    content: str,
    *,
    engine: Literal["lxml", "modest", "lexbor"] = "lxml",
) -> LXMLDocument | ModestDocument | LexborDocument | None:
    if engine == "lxml":
        try:
            tree = cast(lxml.HtmlElement, await asyncio.to_thread(lxml.fromstring, content))  # type: ignore
        except lxml.etree.ParserError:
            return None

        return LXMLDocument(tree)

    elif engine == "lexbor":
        try:
            tree = await asyncio.to_thread(LexborHTMLParser, content)
        except Exception:
            return None

        return LexborDocument(tree)

    elif engine == "modest":
        try:
            tree = await asyncio.to_thread(HTMLParser, content)
        except Exception:
            return None

        return ModestDocument(tree)

    raise TypeError(
        f'Wrong engine type: {engine}\nSupported engines: ["lxml", "modest", "lexbor"]'
    )


@overload
async def parse_page(
    browser: Browser,
    content: str,
    url: str,
    *,
    page_throttle_rate_limit: int,
    async_timeout: int,
    engine: Literal["lxml"],
) -> LXMLDocument:
    ...


@overload
async def parse_page(
    browser: Browser,
    content: str,
    url: str,
    *,
    page_throttle_rate_limit: int,
    async_timeout: int,
    engine: Literal["modest"],
) -> ModestDocument:
    ...


@overload
async def parse_page(
    browser: Browser,
    content: str,
    url: str,
    *,
    page_throttle_rate_limit: int,
    async_timeout: int,
    engine: Literal["lexbor"],
) -> LexborDocument:
    ...


async def parse_page(
    browser: Browser,
    content: str,
    url: str,
    *,
    page_throttle_rate_limit: int,
    async_timeout: int,
    engine: Literal["lxml", "modest", "lexbor"] = "lxml",
    wait_until: Literal["commit", "domcontentloaded", "load", "networkidle"] = "load",
) -> LXMLDocument | ModestDocument | LexborDocument:
    if engine == "lxml":
        try:
            tree = cast(lxml.HtmlElement, await asyncio.to_thread(lxml.fromstring, content))  # type: ignore
        except lxml.etree.ParserError as err:
            warning(
                f'LXML parsing error -> "{err}". We will crawl the HTML content again.'
            )

            page = await browser.new_page()
            visit = with_timeout(async_timeout)(  # type: ignore
                throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                    visit_link
                )
            )
            await visit(page, url, wait_until=wait_until)

            tree = cast(
                lxml.HtmlElement,
                await asyncio.to_thread(lxml.fromstring, await page.content()),  # type: ignore
            )
            await page.close()
        return LXMLDocument(tree)

    elif engine == "lexbor":
        try:
            tree = await asyncio.to_thread(LexborHTMLParser, content)
        except Exception as err:
            warning(
                f'Selectolax parsing error -> "{err}". We will crawl the HTML content again.'
            )

            page = await browser.new_page()
            visit = with_timeout(async_timeout)(  # type: ignore
                throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                    visit_link
                )
            )
            await visit(page, url, wait_until=wait_until)

            tree = await asyncio.to_thread(LexborHTMLParser, await page.content())
            await page.close()

        return LexborDocument(tree)

    elif engine == "modest":
        try:
            tree = await asyncio.to_thread(HTMLParser, content)
        except Exception as err:
            warning(
                f'Selectolax parsing error -> "{err}". We will crawl the HTML content again.'
            )

            page = await browser.new_page()
            visit = with_timeout(async_timeout)(  # type: ignore
                throttle(rate_limit=page_throttle_rate_limit, period=1.0)(  # type: ignore
                    visit_link
                )
            )
            await visit(page, url, wait_until=wait_until)

            tree = await asyncio.to_thread(HTMLParser, await page.content())
            await page.close()

        return ModestDocument(tree)

    raise TypeError(
        f'Wrong engine type: {engine}\nSupported engines: ["lxml", "modest", "lexbor"]'
    )
