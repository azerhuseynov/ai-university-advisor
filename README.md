# University Advisor Agent

An AI agent that helps prospective students research U.S. universities — tuition, admission rates, and earnings outcomes — grounded in real government data rather than a language model's guesses.

**[Live demo](https://ai-university-advisor.onrender.com)**
Note: hosted on a free tier, so the first load may take 30–60 seconds if it's been idle.

## What it does

Ask it things like:
- "What's tuition like at Berkeley?"
- "Compare admission rates at Berkeley and UCLA"
- "What's the earnings outlook after graduating from a school?"

The agent decides on its own which data to pull, fetches it live from an official government API, and answers using only that data.

## How it works

- **Data source:** College Scorecard API (U.S. Department of Education)
- **Agent loop:** built with the Claude API's tool-use feature — the model decides which tool to call and with what arguments, based on the question
- **Grounding:** a system prompt restricts factual claims to what the tools actually returned
- **Memory:** each visitor gets their own session, so follow-up questions resolve against earlier context

## Tech stack

- Backend: Python, FastAPI
- LLM: Claude API (Anthropic), tool-use / function calling
- Data: College Scorecard API
- Frontend: Plain HTML/CSS/JS, no framework
- Deployment: Render

## Known limitations

- U.S. institutions only
- Session memory resets if the server restarts
- Free-tier hosting means a cold start delay after inactivity

## Possible extensions

- Add a third tool for filtering by major or field of study
- Persist sessions in a real database
- Add a qualitative "why this school" layer on top of the structured data