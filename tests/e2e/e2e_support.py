"""Helpers of the end-to-end tests: raw reads and writes of the machine, and one wait."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp
from gaggiuino_api import GaggiuinoClient

# The one time limit of each wait for the machine, in seconds.
WAIT_LIMIT = 10.0

# The settings groups that the tests write. The tests never write another group.
WRITTEN_GROUPS = ("led", "display")

_TIMEOUT = aiohttp.ClientTimeout(total=WAIT_LIMIT)


async def wait_until(check: Callable[[], Awaitable[bool]]) -> bool:
    """Ask `check` again until it is true or `WAIT_LIMIT` ends; return whether it became true."""
    try:
        async with asyncio.timeout(WAIT_LIMIT):
            while not await check():
                await asyncio.sleep(0.2)
    except TimeoutError:
        return False
    return True


class RawMachine:
    """The raw JSON of the REST API, past the integration and the models of the library."""

    def __init__(self, session: aiohttp.ClientSession, base_url: str) -> None:
        self._session = session
        self._base_url = base_url.rstrip("/")

    async def get(self, path: str) -> Any:
        """GET `/api/<path>` and return the parsed JSON."""
        url = f"{self._base_url}/api/{path}"
        async with self._session.get(url, timeout=_TIMEOUT) as response:
            response.raise_for_status()
            return await response.json(content_type=None)

    async def write_group(self, group: str, body: dict[str, Any]) -> None:
        """POST a whole settings group. Only a group of `WRITTEN_GROUPS` is allowed."""
        if group not in WRITTEN_GROUPS:
            raise AssertionError(f"The tests never write the settings group {group!r}")
        url = f"{self._base_url}/api/settings/{group}"
        async with self._session.post(url, json=body, timeout=_TIMEOUT) as response:
            response.raise_for_status()
            answer = await response.json(content_type=None)
        if isinstance(answer, dict) and str(answer.get("success")).lower() == "false":
            raise AssertionError(f"The machine refused the write of {group!r}")

    async def group_equals(self, group: str, expected: dict[str, Any]) -> bool:
        """Return True when the raw settings group equals `expected`."""
        return await self.get(f"settings/{group}") == expected

    async def wait_for_group(self, group: str, expected: dict[str, Any]) -> bool:
        """Wait until the raw settings group equals `expected`; return whether it did."""
        return await wait_until(lambda: self.group_equals(group, expected))

    async def restore_group(self, group: str, original: dict[str, Any]) -> None:
        """Write the raw group back as it was read, and make sure that the machine has it."""
        await self.write_group(group, original)
        assert await self.wait_for_group(group, original), f"Restore of {group} failed"

    async def state(self) -> dict[str, Any]:
        """Return the state that the tests change: the profiles and the written settings groups."""
        profiles = sorted(await self.get("profiles/all"), key=lambda p: p["id"])
        state: dict[str, Any] = {"profiles": profiles}
        for group in WRITTEN_GROUPS:
            state[group] = await self.get(f"settings/{group}")
        return state


async def is_selected(client: GaggiuinoClient, profile_id: int) -> bool:
    """Return True when the list and the status both name `profile_id` as the active profile."""
    selected = [p.id for p in await client.profiles.list() if p.selected]
    return selected == [profile_id] and (await client.status()).profile_id == profile_id
