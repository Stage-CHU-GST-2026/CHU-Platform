import asyncio

from ai.services import create_agent


async def main():
    agent = create_agent()

    response = await agent.run(
        "Hello!"
    )

    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
