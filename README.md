# Economic Decision Advisor — An LLM-Based Agentic System

## Project Overview

The **Economic Decision Advisor** is an agentic AI application that empowers users to make better everyday economic and financial decisions by interpreting live macroeconomic data. Unlike traditional rule-based systems that follow fixed workflows, this agent uses a large language model (LLM) to *reason* about which tools to deploy and how to synthesize their outputs into coherent, actionable insights.

The core innovation lies in the agent's reasoning autonomy: rather than executing a predetermined decision tree, the LLM dynamically evaluates the user's query, determines which data sources are most relevant, orchestrates calls to multiple real-world APIs, and then reflects on the results to provide evidence-based guidance. This mirrors how human financial advisors reason—by gathering information, weighing trade-offs, and adapting their approach based on context.

## Core Agent Architecture

The Economic Decision Advisor follows a classic **agentic loop** consisting of four key phases:

### 1. **Reason**
The agent receives a user query and uses the LLM to determine the most appropriate course of action. The LLM evaluates:
- What the user is asking (problem decomposition)
- Which external data sources would provide relevant insights
- Whether additional information is needed before offering guidance
- How past decisions or preferences (from long-term memory) might inform the current response

### 2. **Act**
Based on its reasoning, the agent *decides* which MCP (Model Context Protocol) tools to invoke and in what sequence. The agent may call:
- One tool for a straightforward query
- Multiple tools in parallel or sequence for complex scenarios
- Zero tools if sufficient context already exists in long-term memory

### 3. **Observe**
The agent receives structured data responses from each tool call. These observations are then integrated into the agent's working context. The LLM interprets the data, identifies patterns, and checks for consistency or conflicts between different data sources.

### 4. **Reflect**
The agent synthesizes all observations into a coherent response, considering:
- How the data answers the user's original question
- Confidence levels and data limitations
- Relevant caveats or alternative interpretations
- How this interaction should inform future reasoning (memory update)

This loop continues iteratively until the agent is confident it can provide a high-quality response. The loop is transparent to the user—they see the final synthesis, but the reasoning and tool orchestration occur beneath the surface.

## MCP Tools (Real External APIs)

The agent integrates with three primary data sources, each serving a distinct purpose in economic reasoning:

### 1. Federal Reserve Economic Data (FRED) API

**What it provides:**  
Direct access to thousands of macroeconomic time series maintained by the U.S. Federal Reserve, including inflation rates (CPI), unemployment figures, interest rates, GDP growth, and sectoral economic indicators.

**Why it's valuable:**  
FRED data is authoritative, regularly updated, and widely used by economists and policymakers. It provides the ground truth for macroeconomic conditions that directly affect personal financial decisions.

**How the agent uses it:**  
When a user asks, "Is now a good time to save or pay down debt?", the agent queries FRED to retrieve current inflation and real interest rates. High inflation may justify paying down debt faster, while high real interest rates favor saving. The agent can also compare historical data to assess whether current conditions are unusual, adding context to its recommendations.

### 2. Financial News API (NewsAPI)

**What it provides:**  
Real-time aggregation of economic and financial news headlines from hundreds of reputable sources, tagged by topic and sentiment.

**Why it's valuable:**  
News captures market sentiment, emerging risks, and policy announcements that are not yet fully reflected in historical time series. It provides narrative context and alerts the agent to sudden shifts in economic conditions.

**How the agent uses it:**  
When a user asks, "What recent economic news should influence my spending decisions?", the agent retrieves recent headlines on inflation, employment, interest rates, or sectoral trends. The agent weighs the sentiment and credibility of sources to highlight the most consequential developments. This ensures users are aware of emerging factors that may alter their financial outlook.

### 3. Currency & Exchange Rate API

**What it provides:**  
Real-time currency exchange rates, purchasing power parity indices, and cross-border cost-of-living comparisons.

**Why it's valuable:**  
Exchange rates and purchasing power directly affect the real value of savings, the cost of imports, and the returns on international investments. This API contextualizes personal finances within a global economic frame.

**How the agent uses it:**  
When a user asks, "How does current inflation affect my purchasing power?", the agent may compare purchasing power across different currencies or time periods. If a user is considering international spending or has investments abroad, the agent uses exchange data to model real purchasing power, not just nominal amounts. This tool also helps the agent explain inflation's real-world impact on everyday purchases.

## Long-Term Memory

The agent is designed to *learn* from interactions and maintain a persistent understanding of each user's context, preferences, and goals.

### What Gets Stored

Long-term memory captures:

- **User Profile**: Basic financial situation (income range, debt level, dependents)
- **Risk Tolerance**: Inferred from past responses and explicit preferences (conservative, moderate, aggressive)
- **Financial Goals**: Short-term (next 3 months) and long-term (retirement, major purchase)
- **Past Decisions**: A log of previous queries, agent recommendations, and whether the user acted on them
- **Preferences**: Which data sources the user trusts most, preferred explanation depth, any domains to avoid (e.g., stock picking)

### Memory Architecture

Memory is stored in a structured format (e.g., JSON or lightweight SQLite database) that allows the agent to:
1. **Retrieve** relevant context quickly when processing new queries
2. **Update** memory as new information emerges (e.g., user shares they got a raise, or inflation news shifts their concerns)
3. **Reflect** on past patterns to identify inconsistencies or evolving preferences

### How It Influences Reasoning

Each time the agent receives a query, it retrieves the user's profile and recent decision history. This context informs:
- **Tone & Detail**: If the user previously opted for simple explanations, the agent adjusts verbosity
- **Relevance**: The agent prioritizes tools and data relevant to known goals (e.g., retirement saving)
- **Consistency**: The agent can flag if a new query conflicts with stated goals or past decisions, prompting reflection
- **Personalization**: The agent avoids repeating advice it previously gave unless circumstances have changed

This creates a *relationship* between user and agent, where each interaction builds a richer model of the user's economic context and values.

## User Interface

The Economic Decision Advisor communicates through a **simple, conversational chat interface** available on web or desktop platforms. The UI serves as a communication layer, not the locus of intelligence.

### Interface Design Principles

- **Accessibility**: Users can ask questions in natural language, just as they would with a financial advisor
- **Transparency**: When the agent calls tools, it briefly indicates which data it's fetching (e.g., "Checking current inflation data from FRED...")
- **Traceability**: The response includes citations to data sources (e.g., "Based on FRED inflation data as of [date]...") and hyperlinks to relevant news articles
- **Context Preservation**: Conversation history remains visible, allowing users to revisit reasoning and refine follow-up questions
- **Memory Acknowledgment**: Occasionally, the agent reminds users of remembered context (e.g., "Given your focus on debt reduction, here's what the latest interest rates mean for you")

The UI does *not* make decisions, run models, or orchestrate tools; it is purely a conduit for user input and agent output. All reasoning, tool selection, and memory management occur in the backend agent system.

## Example Agent Interactions

Below are realistic scenarios illustrating how the agent reasons and acts:

### Scenario 1: Debt vs. Savings Decision

**User**: "Is now a good time to prioritize saving or paying down debt?"

**Agent Reasoning**:
- Retrieves user profile (moderate risk tolerance, $50k in student loans, $15k emergency fund)
- Decides to fetch real interest rates and inflation data from FRED
- Calls the Currency/Exchange Rate API to check purchasing power trends
- Reviews recent financial news for policy signals

**Agent Response**:
"Given current conditions, paying down debt makes sense for you. Here's why: Real interest rates are positive (3.2% nominal minus 2.8% inflation), meaning the 'true cost' of your debt is substantial. Your emergency fund is adequate, so after-tax savings could meaningfully reduce interest paid on your loans. However, watch for [recent Fed news]. If inflation cools further, savings might become more attractive. I'd suggest redirecting [X]% of monthly surplus to debt for the next six months, then revisiting as conditions evolve."

### Scenario 2: Inflation's Personal Impact

**User**: "How does current inflation affect my purchasing power?"

**Agent Reasoning**:
- Retrieves inflation rate from FRED
- Uses exchange rate data to compare purchasing power in different markets
- Checks user memory: has noted concerns about rising rent and groceries
- Queries financial news for sector-specific inflation trends

**Agent Response**:
"Overall inflation is 3.1% year-over-year, but *you're* likely experiencing faster inflation in the categories you care about. Groceries are up 4.2% and rental markets 5.8% in your region. This means your $100,000 salary effectively buys [X]% less than a year ago, specifically in housing and food. One option: shift discretionary spending to categories with lower inflation, or consider the timing of major purchases (e.g., buying durable goods now before further price rises). Want me to model specific scenarios?"

### Scenario 3: Economic News & Spending Decisions

**User**: "What recent economic news should influence my spending decisions?"

**Agent Reasoning**:
- Queries NewsAPI for recent headlines on employment, inflation, and consumer sectors
- Filters by relevance to user's stored goals and profile
- Cross-references with FRED data to validate sentiment

**Agent Response**:
"Three stories matter to you this week: (1) The Fed signaled rates may hold steady—good news for mortgage refinancing if you're considering it. (2) Job growth slowed to [X%], suggesting potential income risk; consider boosting your emergency fund. (3) Tech layoffs are accelerating; if your income depends on that sector, this is a caution signal. I'd recommend deferring non-essential purchases for the next month while clarity emerges. Does your employment feel stable?"

## Educational Purpose

This project is designed and built for **educational purposes** within a university course on agentic AI systems. It serves as a capstone demonstration of how LLM agents reason autonomously over real-world data to solve practical problems.

### Learning Objectives

1. **Agentic Reasoning**: Students understand how LLMs can be prompted to reason iteratively (Reason → Act → Observe → Reflect), rather than simply answering queries directly.

2. **Tool Orchestration**: Students learn to design systems where an AI agent *decides* which tools to use, rather than executing a fixed decision tree. This requires designing clean tool interfaces and grounding the agent's reasoning in concrete, external data.

3. **API Integration**: Students practice integrating multiple real-world APIs (FRED, NewsAPI, exchange rates) into a cohesive backend system, handling rate limiting, error states, and data heterogeneity.

4. **Long-Term Memory**: Students explore how persistent context enables more personalized, adaptive agent behavior. This touches on database design, privacy considerations, and the challenge of maintaining consistency over time.

5. **Prompt Engineering & LLM Control**: Students refine prompts to guide LLM behavior, define tool schemas that the LLM understands, and implement guardrails to prevent misuse (e.g., the agent avoiding specific investment advice).

6. **System Design**: Students grapple with the end-to-end architecture of an agentic system—from user interface design to backend reasoning to observability—and appreciate the gaps between research papers and production deployments.

## Tech Stack

The Economic Decision Advisor is built using modern, accessible technologies aligned with current industry practice:

- **LLM API**: OpenAI GPT-4 / GPT-4o (or compatible LLM API) for reasoning and response generation
- **REST APIs**: 
  - Federal Reserve Economic Data (FRED) API for macroeconomic data
  - NewsAPI (or similar) for financial news aggregation
  - Exchange rate API (e.g., Open Exchange Rates) for currency data
- **Backend Framework**: Python with FastAPI or Node.js with Express for API server
- **Storage**: SQLite or JSON-based persistence for long-term user memory
- **Frontend Framework**: React or Vue.js for web-based chat interface (or desktop app using Electron)
- **Orchestration**: Python-based agent loop with structured prompting and tool-calling libraries (e.g., LangChain, LlamaIndex, or custom implementation)

## Conclusion

The Economic Decision Advisor demonstrates that agentic AI is not science fiction—it is a practical, learnable approach to building intelligent systems that reason autonomously, integrate diverse information sources, and adapt to individual users over time. By combining an LLM's reasoning with real economic data, this project grounds abstract agentic concepts in a tangible, relatable domain. Through building and deploying this system, students gain hands-on experience with the core techniques reshaping AI development today.
