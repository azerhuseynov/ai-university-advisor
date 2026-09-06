import os
import json
import requests
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()  # reads .env and loads its contents as environment variables

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
COLLEGE_SCORECARD_API_KEY = os.environ["COLLEGE_SCORECARD_API_KEY"]

client = Anthropic(api_key=ANTHROPIC_API_KEY)


def search_schools(name=None, state=None, fields=None, per_page=5):
    """Search College Scorecard for schools matching filters."""
    if fields is None:
        fields = "school.name,school.city,school.state,latest.cost.tuition.in_state,latest.admissions.admission_rate.overall"

    params = {"api_key": COLLEGE_SCORECARD_API_KEY, "fields": fields, "per_page": per_page}
    if name:
        params["school.name"] = name
    if state:
        params["school.state"] = state

    response = requests.get("https://api.data.gov/ed/collegescorecard/v1/schools", params=params)
    if response.status_code != 200:
        return {"error": f"API returned status {response.status_code}"}
    return response.json().get("results", [])


def compare_schools(names, fields=None):
    """Look up several schools by name and return one result each, for side-by-side comparison."""
    results = []
    for n in names:
        matches = search_schools(name=n, per_page=1, fields=fields)
        results.append(matches[0] if matches else {"error": f"No match found for '{n}'"})
    return results


tools = [
    {
        "name": "search_schools",
        "description": "Search U.S. colleges and universities by name or state. Returns cost, admission rate, and location data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Full or partial school name, e.g. 'Berkeley'"},
                "state": {"type": "string", "description": "Two-letter U.S. state code, e.g. 'CA'"},
            },
        },
    },
    {
        "name": "compare_schools",
        "description": "Compare two or more specific, named schools side by side on cost, admissions, and earnings.",
        "input_schema": {
            "type": "object",
            "properties": {
                "names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "School names to compare, e.g. ['Berkeley', 'UCLA']",
                },
            },
            "required": ["names"],
        },
    },
]


def call_tool(call):
    if call.name == "search_schools":
        return search_schools(**call.input)
    elif call.name == "compare_schools":
        return compare_schools(**call.input)
    else:
        return {"error": f"Unknown tool: {call.name}"}


SYSTEM_PROMPT = """You are a college advisor helping prospective students research U.S. universities.

Rules:
- Only state facts about tuition, admission rates, or earnings if they came from a search_schools or compare_schools result. Never rely on your own training data for these numbers — it may be outdated or wrong.
- If a tool doesn't return the information being asked about, say so plainly rather than guessing.
- You may use general knowledge for non-factual context (e.g. what a major typically involves), but never present it as if it were official data.
- If a school name is ambiguous or the API returns nothing, ask a clarifying question instead of assuming.
"""


class Advisor:
    def __init__(self, model="claude-haiku-4-5-20251001"):
        self.model = model
        self.messages = []

    def ask(self, question):
        self.messages.append({"role": "user", "content": question})

        while True:
            response = client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=tools,
                messages=self.messages,
            )
            self.messages.append({"role": "assistant", "content": response.content})
            tool_calls = [block for block in response.content if block.type == "tool_use"]

            if not tool_calls:
                return response.content[0].text

            tool_results = []
            for call in tool_calls:
                result = call_tool(call)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": json.dumps(result),
                })
            self.messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    advisor = Advisor()
    print(advisor.ask("What's tuition like at Berkeley?"))