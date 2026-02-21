import asyncio
import random
from datetime import datetime
from enum import Enum
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour


class CoordinatorState(Enum):
    IDLE = "IDLE"
    EVALUATING = "EVALUATING"
    ASSIGNING = "ASSIGNING"
    MONITORING = "MONITORING"


class RescueState(Enum):
    IDLE = "IDLE"
    DISPATCHED = "DISPATCHED"
    RESCUING = "RESCUING"
    COMPLETED = "COMPLETED"


class SmokeSensor:
    def __init__(self, sensor_id):
        self.sensor_id = sensor_id
        self.smoke_percentage = random.uniform(0, 10)

    def read_smoke(self):
        change = random.uniform(-5, 8)
        self.smoke_percentage = max(0, min(100, self.smoke_percentage + change))
        return self.smoke_percentage


class VibrationSensor:
    def __init__(self):
        self.frequency = random.uniform(0, 1)

    def read_vibration(self):
        change = random.uniform(-0.5, 1)
        self.frequency = max(0, min(10, self.frequency + change))
        return self.frequency


class RescueAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.state = RescueState.IDLE
        self.current_task = None

    async def handle_task(self, disaster_type):
        self.state = RescueState.DISPATCHED
        print(f"[RESCUE-{self.agent_id}] Dispatched")

        self.state = RescueState.RESCUING
        print(f"[RESCUE-{self.agent_id}] Responding to {disaster_type}")

        await asyncio.sleep(5)

        self.state = RescueState.COMPLETED
        print(f"[RESCUE-{self.agent_id}] Rescue completed")

        self.state = RescueState.IDLE
        print(f"[RESCUE-{self.agent_id}] Back to IDLE")


class CoordinatorAgent:
    def __init__(self, rescue_agents):
        self.state = CoordinatorState.IDLE
        self.rescue_agents = rescue_agents

    async def handle_disaster(self, disaster_type):
        self.state = CoordinatorState.EVALUATING
        print("[COORDINATOR] Evaluating disaster")

        self.state = CoordinatorState.ASSIGNING
        print("[COORDINATOR] Coordinating rescue response")

        agent = random.choice(self.rescue_agents)
        await agent.handle_task(disaster_type)

        self.state = CoordinatorState.MONITORING
        print("[COORDINATOR] Monitoring rescue operation")

        self.state = CoordinatorState.IDLE
        print("[COORDINATOR] Back to IDLE")


class SensorAgent(Agent):
    def __init__(self, jid, password, log_file, coordinator):
        super().__init__(jid, password, verify_security=False)
        self.log_file = log_file
        self.coordinator = coordinator
        self.smoke_sensors = [SmokeSensor(i) for i in range(1, 5)]
        self.vibration_sensor = VibrationSensor()

        with open(self.log_file, "w") as f:
            f.write(f"Disaster Monitoring Log - Started at {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")

    class MonitorBehaviour(CyclicBehaviour):
        async def run(self):
            smoke_readings = {
                s.sensor_id: s.read_smoke() for s in self.agent.smoke_sensors
            }
            vibration = self.agent.vibration_sensor.read_vibration()

            severity, disaster_type = self.agent.evaluate_environment(
                smoke_readings, vibration
            )

            if severity == "CRITICAL":
                print("[SYSTEM] Critical disaster detected")
                await self.agent.coordinator.handle_disaster(disaster_type)

            await asyncio.sleep(5)

    async def setup(self):
        print("[SYSTEM] Agents are sensing the environment")
        self.add_behaviour(self.MonitorBehaviour())

    def evaluate_environment(self, smoke_readings, vibration):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        avg_smoke = sum(smoke_readings.values()) / len(smoke_readings)

        severity = "STABLE"
        disaster_type = None

        if avg_smoke > 70 or vibration > 7:
            severity = "CRITICAL"
            disaster_type = "FIRE" if avg_smoke > 70 else "EARTHQUAKE"

        smoke_str = ", ".join(
            f"{sensor_id}: {value:.2f}"
            for sensor_id, value in sorted(smoke_readings.items())
        )

        log_entry = (
            f"[{timestamp}] "
            f"Smoke Sensors: {{{smoke_str}}} "
            f"(Avg: {avg_smoke:.2f}%) | "
            f"Vibration: {vibration:.2f} Hz | "
        )

        if severity == "STABLE":
            log_entry += "Status: ENVIRONMENT STABLE"
        else:
            log_entry += f"Status: DISASTER - {disaster_type} | Severity: {severity}"

        print(log_entry)

        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

        return severity, disaster_type


async def main():
    rescue_agents = [RescueAgent(1), RescueAgent(2)]
    coordinator = CoordinatorAgent(rescue_agents)

    agent = SensorAgent(
        "dci_rescue@xmpp.jp",
        "password",
        "disaster_event_log.txt",
        coordinator
    )

    await agent.start(auto_register=False)

    await asyncio.get_running_loop().run_in_executor(
        None, input, "Press ENTER to stop...\n"
    )

    await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
