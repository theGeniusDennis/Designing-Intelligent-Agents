import asyncio
import random
from datetime import datetime

from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour


class SensorAgent(Agent):

    class SenseEnvironmentBehaviour(PeriodicBehaviour):
        async def run(self):
            disaster_types = ["Flood", "Fire", "Earthquake"]
            severity_levels = ["LOW", "MEDIUM", "HIGH"]

            disaster = random.choice(disaster_types)
            severity = random.choice(severity_levels)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            event = {
                "disaster_type": disaster,
                "severity": severity,
                "time": timestamp
            }

            print(f"[EVENT DETECTED] {event}")

            # Log event to file
            with open("event_log.txt", "a") as log:
                log.write(f"{event}\n")

    async def setup(self):
        print("SensorAgent started and monitoring environment...")
        behaviour = self.SenseEnvironmentBehaviour(period=5)
        self.add_behaviour(behaviour)


async def main():
    jid = "santand2@xmpp.jp"
    password = "santan1212"

    agent = SensorAgent(jid, password)
    await agent.start(auto_register=True)

    print("SensorAgent running...")
    await asyncio.sleep(30)  # run for 30 seconds
    await agent.stop()
    print("SensorAgent stopped.")


if __name__ == "__main__":
    asyncio.run(main())
