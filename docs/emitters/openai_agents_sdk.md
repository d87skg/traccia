
OpenAI Agents SDK Emitter
Status
Active — verified with mock, ready for real API testing.

Installation
bash
pip install traccia-sdk openai-agents
Usage
python
from agents import Agent, Runner
from traccia.recorder import DefaultRecorder
from traccia.emitter.openai import OpenAIEmitter

agent = Agent(name="Assistant", instructions="You are a helpful assistant.")

recorder = DefaultRecorder("OpenAI Agent Session")
emitter = OpenAIEmitter(recorder)
emitter.patch(agent)

result = Runner.run_sync(agent, "Hello, how are you?")
print(result.final_output)

recorder.export("openai_agent.evidence")
Supported Events
function.call → OpenBase tool.invoke

llm.response → OpenBase llm.response

agent.run → Session lifecycle
