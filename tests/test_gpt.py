import asyncio
import pytest
from app.gpt.chat_summary import gpt_summary
from app.config import ADMIN_CHAT


@pytest.mark.asyncio
@pytest.mark.gpt
async def test_gpt():
    assert isinstance(await gpt_summary(ADMIN_CHAT), str), 'failed'
