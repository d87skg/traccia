import sys
from pathlib import Path

sys.path.insert(0, 'D:/Traccia/src/traccia')
sys.path.insert(0, 'D:/Traccia/traccia/reference')

from recorder import DefaultRecorder
from emitter.claude_code import ClaudeCodeEmitter
from python.validator import verify

class MockClaudeCodeAgent:
    def run(self, task):
        return "Task completed"
    def execute_command(self, command):
        return f"Executed: {command}"
    def read_file(self, path):
        return "file content"
    def write_file(self, path, content):
        return "written"

agent = MockClaudeCodeAgent()
recorder = DefaultRecorder("Claude Code Session")
emitter = ClaudeCodeEmitter(recorder)

emitter.patch(agent)
print("Patch succeeded")

agent.execute_command("ls -la")
agent.read_file("/tmp/test.txt")
agent.write_file("/tmp/output.txt", "data")
agent.run("analyze logs")

path = recorder.export("tests/integration/claude_code_mock.evidence")
print("Evidence:", path)

v = verify(path)
print("Status:", v.status)
print("Valid:", v.is_valid)
