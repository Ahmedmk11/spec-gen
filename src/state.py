from typing import TypedDict

class AgentState(TypedDict):
    code: str # code to generate tests for
    file_path: str  # file path of the code
    tests: str # generated tests file for the current function

    status: str # status of last test file
    output: str # output of last test file

    decision: str # decision of the analysis agent on the last test file
    reason: str # reason of last decision

    previous_attempts: list[str] # previous attempts of creating the current test file, empty if first attempt

    retries: int
