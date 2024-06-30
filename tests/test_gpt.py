import pytest
from app.gpt.chat_summary import gpt_summary


@pytest.mark.asyncio
async def test_gpt():
    assert isinstance(await gpt_summary(-1002145854165), str), 'failed'
