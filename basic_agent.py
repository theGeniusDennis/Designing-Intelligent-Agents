import spade
import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour


class HelloAgent(Agent):
    class HelloBehaviour(OneShotBehaviour):
        async def run(self):
            print("Hello! Agent is running and connected to XMPP.")

    async def setup(self):
        print("Agent starting...")
        self.add_behaviour(self.HelloBehaviour())


async def main():
    jid = "santand@xmpp.jp"
    password = "santan1212"

    agent = HelloAgent(jid, password)
    await agent.start()

    print("Agent started successfully.")
    await asyncio.sleep(10)   # keep agent alive for 10 seconds

    await agent.stop()
    print("Agent stopped.")


if __name__ == "__main__":
    asyncio.run(main())
