import asyncio
import os

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


async def extract_paragraphs_subprocess():
    cmd = f'python3 {SCRIPT_PATH}/extract_paragraphs_async.py'
    await asyncio.create_subprocess_shell(cmd)


if __name__ == '__main__':
    asyncio.run(extract_paragraphs_subprocess())
