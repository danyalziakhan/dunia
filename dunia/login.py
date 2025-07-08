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

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from dunia.error import (
    LoginInputNotFound,
    PasswordInputNotFound,
    PlaywrightTimeoutError,
)
from dunia.log import success

if TYPE_CHECKING:
    from dunia.playwright._types import PlaywrightBrowser, PlaywrightPage


class LoginStrategy(Protocol):
    async def __call__(self, page: PlaywrightPage, login_button_query: str) -> None: ...


async def default_login_button_strategy(
    page: PlaywrightPage, login_button_query: str
) -> None:
    # ? Most websites redirect from login page when submitting the form, so we are putting it inside expect_navigation() block
    # ? If it doesn't work for some websites, copy this function to your code, remove expect_navigation() part and pass your function to LoginInfo object
    async with page.expect_navigation():
        await page.click(login_button_query)

    await page.wait_for_load_state(
        state="load"
    )  # ? "load" is fine for most websites, but some websites don't show full page details until all the network requests are resolved, so for that "networkidle" can be used


@dataclass(slots=True, frozen=True, kw_only=True)
class LoginInfo:
    """
    All the required information that will allow the browser to login to the website. This doesn't contain any information about the type of Browser.
    """

    login_url: str = field(
        metadata={"help": "The url of the login page where input forms are present"}
    )
    user_id: str = field(metadata={"help": "User id or email"})
    password: str = field(metadata={"help": "User password"})
    user_id_query: str = field(
        metadata={"help": "Query for selecting the input field for typing the user id"}
    )
    password_query: str = field(
        metadata={"help": "Query for selecting the input field for typing the password"}
    )
    login_button_query: str = field(
        metadata={
            "help": "Query for selecting the login button or whatever element that is required for submitting the login request"
        }
    )
    keep_logged_in_check_query: str | None = field(
        default=None,
        metadata={
            "help": "Query for the checkbox for keeping the user logged in."
            "Some websites have the checkbox, in such case, it's better to use it to perhaps help the browser store the cache of user credentials"
        },
    )
    login_button_strategy: LoginStrategy = field(
        default=default_login_button_strategy,
        metadata={
            "help": "Most websites provides the clickable submit button, but sometimes the button cannot be clicked."
            'In such case, a different strategy for submitting the credentials will be used (such as pressing "Enter", etc.)'
            'In that case, we can say that it doesn\'t necessarily needs to be login "button" strategy, but anything that can successfully submit the form'
        },
    )


@dataclass(slots=True, frozen=True)
class Login:
    login_info: LoginInfo

    async def __call__(self, browser: PlaywrightBrowser) -> None:
        page = await browser.new_page()
        # ? Sometimes if there are network requests happening in the background, the "input" fields keep reverting to the original/previous state while typing
        await page.goto(self.login_info.login_url, wait_until="networkidle")

        is_already_login = True
        try:
            await page.wait_for_selector(
                self.login_info.user_id_query,
                state="visible",
            )

            is_already_login = False
        except PlaywrightTimeoutError:
            is_already_login = True

        if not is_already_login:
            input_id = await page.query_selector(self.login_info.user_id_query)

            if input_id:
                await input_id.fill(self.login_info.user_id)
            else:
                raise LoginInputNotFound(
                    f"User ID ({self.login_info.user_id}) could not be entered"
                )

            if self.login_info.keep_logged_in_check_query:
                await page.check(self.login_info.keep_logged_in_check_query)

            input_password = await page.query_selector(
                self.login_info.password_query,
            )
            if input_password:
                await input_password.fill(self.login_info.password)
            else:
                raise PasswordInputNotFound(
                    f"Passowrd ({self.login_info.password}) could not be entered"
                )

            await self.login_info.login_button_strategy(
                page, self.login_info.login_button_query
            )

            success(
                f"Logged in <MAGENTA><w>(ID: {self.login_info.user_id}, PW: {self.login_info.password})</></>"
            )

        await page.close()
