from mocobot.application.runtime import Runtime
import sys
import asyncio


if __name__ == '__main__':
    asyncio.run(Runtime().start(sys.argv))

