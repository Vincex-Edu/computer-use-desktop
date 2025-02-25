import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from anthropic.types import TextBlockParam
from streamlit.testing.v1 import AppTest

from computer_use_demo.streamlit import Sender


@pytest.fixture(autouse=True)
def temp_bridge_dir():
    """Create a temporary directory for the bridge files during tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_bridge_dir = Path(temp_dir) / ".anthropic"
        os.makedirs(temp_bridge_dir, exist_ok=True)
        # Patch the BRIDGE_DIR
        with mock.patch("computer_use_demo.api.utils.BRIDGE_DIR", temp_bridge_dir):
            yield temp_bridge_dir


@pytest.fixture
def streamlit_app():
    return AppTest.from_file("computer_use_demo/streamlit.py")


def test_streamlit(streamlit_app: AppTest):
    streamlit_app.run()
    streamlit_app.text_input[1].set_value("sk-ant-0000000000000").run()
    with mock.patch("computer_use_demo.loop.sampling_loop") as patch:
        streamlit_app.chat_input[0].set_value("Hello").run()
        assert patch.called
        assert patch.call_args.kwargs["messages"] == [
            {
                "role": Sender.USER,
                "content": [TextBlockParam(text="Hello", type="text")],
            }
        ]
        assert not streamlit_app.exception
