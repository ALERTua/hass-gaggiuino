# hass-gaggiuino memory index

The index that follows comes from `.claude/memory/MEMORY.md`, and each link is relative to that folder. The repository is public, so this memory holds no personal data and no value of one computer.

- The exact version of `gaggiuino_api` in `custom_components/gaggiuino/manifest.json` sets the minimum firmware that the integration supports. A version of the library supports one iteration of the REST API of the firmware and names its minimum firmware in its README. The integration adds no support of its own for an older firmware.
- Each change goes into `main` through a pull request from its own branch. Only a commit of the type `chore` goes directly into `main`.
- The pin of `gaggiuino_api` is in `custom_components/gaggiuino/manifest.json` and in `pyproject.toml`. Change both lines together. The test `tests/test_requirements.py` compares them.
- The tests run only on Linux, in WSL and in CI. The test package `pytest-homeassistant-custom-component` needs `fcntl`, which Windows does not have.
- A test plays the machine with the `aioclient_mock` fixture of Home Assistant through `FakeMachine` in `tests/conftest.py`. Do not mock the client class: the test must see the parse of the answers.
- The end-to-end tests in `tests/e2e/` write to a real machine. Before you change or run them, read their safety rules in the "Testing" section of `AGENTS.md`, and keep each rule.
- The coordinator has one `asyncio.Lock`. The poll holds it for all of its requests. An action holds it for the write, the read of what changed and the update of the listeners. `PARALLEL_UPDATES` orders only the actions of one platform, and the LED light and the LED disco switch are on two platforms and write one settings group. The lock also stops a poll that read the settings before a write from storing the old copy after it.
- After a write, do not call `async_request_refresh()`. It has a cooldown of 10 seconds. Push the group that the action read back into `coordinator.data` instead.
