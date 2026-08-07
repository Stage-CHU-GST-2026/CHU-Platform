import asyncio

from agents.data_analyst import create_data_analyst


async def main():
    agent = create_data_analyst()

    response = await agent.run(
        "Hello!"
    )

    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
