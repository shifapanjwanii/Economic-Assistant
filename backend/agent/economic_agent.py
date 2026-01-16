from typing import Dict, List, Any, Optional
import json
from openai import AsyncOpenAI
import config
from services.api_services import FREDService, NewsAPIService, ExchangeRateService
from services.memory_service import MemoryService


class EconomicAgent:
    """
    The main agentic system implementing the Reason-Act-Observe-Reflect loop
    """
    
    def __init__(self):
        # Initialize OpenAI client (works with OpenRouter too)
        if config.LLM_PROVIDER == "openrouter":
            self.client = AsyncOpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENROUTER_BASE_URL
            )
        else:
            self.client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
        
        self.fred_service = FREDService()
        self.news_service = NewsAPIService()
        self.exchange_service = ExchangeRateService()
        self.memory_service = MemoryService()
        
        # Define available tools for the agent
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_inflation_data",
                    "description": "Retrieve current inflation rate (CPI) from FRED",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_unemployment_rate",
                    "description": "Retrieve current unemployment rate from FRED",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_interest_rates",
                    "description": "Retrieve current Federal Funds Rate from FRED",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_economic_news",
                    "description": "Retrieve recent economic news articles",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for news (e.g., 'inflation', 'federal reserve')"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_exchange_rates",
                    "description": "Get current exchange rates for currency comparisons",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "base_currency": {
                                "type": "string",
                                "description": "Base currency code (default: USD)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "compare_purchasing_power",
                    "description": "Compare purchasing power between two currencies",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "amount": {
                                "type": "number",
                                "description": "Amount to convert"
                            },
                            "from_currency": {
                                "type": "string",
                                "description": "Source currency code"
                            },
                            "to_currency": {
                                "type": "string",
                                "description": "Target currency code"
                            }
                        },
                        "required": ["amount"]
                    }
                }
            }
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return the observation"""
        try:
            if tool_name == "get_inflation_data":
                return await self.fred_service.get_inflation_rate()
            
            elif tool_name == "get_unemployment_rate":
                return await self.fred_service.get_unemployment_rate()
            
            elif tool_name == "get_interest_rates":
                return await self.fred_service.get_federal_funds_rate()
            
            elif tool_name == "get_economic_news":
                query = arguments.get("query", "economy OR inflation OR federal reserve")
                return await self.news_service.get_economic_news(query=query)
            
            elif tool_name == "get_exchange_rates":
                base = arguments.get("base_currency", "USD")
                return await self.exchange_service.get_exchange_rates(base_currency=base)
            
            elif tool_name == "compare_purchasing_power":
                amount = arguments.get("amount", 100.0)
                from_curr = arguments.get("from_currency", "USD")
                to_curr = arguments.get("to_currency", "EUR")
                return await self.exchange_service.compare_purchasing_power(
                    amount, from_curr, to_curr
                )
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def process_query(
        self, 
        user_id: str, 
        query: str
    ) -> Dict[str, Any]:
        """
        Main agentic loop: Reason -> Act -> Observe -> Reflect
        """
        # Retrieve user context from memory
        user_profile = await self.memory_service.get_user_profile(user_id)
        conversation_history = await self.memory_service.get_conversation_history(user_id, limit=5)
        recent_decisions = await self.memory_service.get_recent_decisions(user_id, limit=3)
        
        # Build system prompt with memory context
        system_prompt = self._build_system_prompt(user_profile, recent_decisions)
        
        # Build conversation messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add recent conversation history
        for conv in conversation_history:
            messages.append({
                "role": conv["role"],
                "content": conv["message"]
            })
        
        # Add current query
        messages.append({
            "role": "user",
            "content": query
        })
        
        # Save user query to memory
        await self.memory_service.add_conversation(user_id, "user", query)
        
        tools_used = []
        max_iterations = 5
        iteration = 0
        
        # Agentic loop
        while iteration < max_iterations:
            iteration += 1
            
            # REASON & ACT: Let LLM decide what tools to use
            response = await self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=config.LLM_TEMPERATURE,
                max_tokens=config.MAX_TOKENS
            )
            
            assistant_message = response.choices[0].message
            
            # Check if agent wants to use tools
            if assistant_message.tool_calls:
                # ACT & OBSERVE: Execute tool calls
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    tools_used.append(function_name)
                    
                    # OBSERVE: Get tool results
                    observation = await self.execute_tool(function_name, function_args)
                    
                    # Add observation to conversation
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(observation),
                        "tool_call_id": tool_call.id
                    })
                
                # Continue loop to let agent reflect on observations
                continue
            
            else:
                # REFLECT: Agent has final response
                final_response = assistant_message.content
                
                # Save assistant response to memory
                await self.memory_service.add_conversation(
                    user_id, 
                    "assistant", 
                    final_response,
                    tools_used
                )
                
                return {
                    "response": final_response,
                    "tools_used": list(set(tools_used)),
                    "iterations": iteration
                }
        
        # Max iterations reached
        return {
            "response": "I apologize, but I need more time to analyze this query. Could you rephrase or simplify your question?",
            "tools_used": tools_used,
            "iterations": iteration
        }
    
    def _build_system_prompt(
        self,
        user_profile: Optional[Dict[str, Any]],
        recent_decisions: List[Dict[str, Any]]
    ) -> str:
        """Build system prompt with user context"""
        base_prompt = """You are an Economic Decision Advisor - an intelligent assistant that helps users make informed everyday economic and financial decisions using real-time macroeconomic data.

Your role is to:
1. REASON about the user's question and determine which data sources would be most helpful
2. ACT by calling appropriate tools to gather economic data, news, or exchange rate information
3. OBSERVE the data returned from tools and identify patterns or insights
4. REFLECT by synthesizing all information into clear, actionable guidance

Guidelines:
- Use tools strategically to gather relevant economic data before making recommendations
- Cite your data sources and their dates in your responses
- Consider both current conditions and historical context
- Be transparent about uncertainties and limitations
- Avoid specific investment advice or stock picking
- Focus on helping with everyday economic decisions (saving, spending, debt management)
- Explain economic concepts in accessible language
- Consider the user's personal context when providing guidance
"""
        
        # Add user context if available
        if user_profile:
            base_prompt += f"\n\nUser Context:"
            if user_profile.get("risk_tolerance"):
                base_prompt += f"\n- Risk tolerance: {user_profile['risk_tolerance']}"
            if user_profile.get("debt_level"):
                base_prompt += f"\n- Debt level: ${user_profile['debt_level']:,.2f}"
            if user_profile.get("financial_goals"):
                goals = user_profile['financial_goals']
                if goals:
                    base_prompt += f"\n- Financial goals: {', '.join(str(v) for v in goals.values() if v)}"
        
        # Add recent decision context
        if recent_decisions:
            base_prompt += f"\n\nRecent interactions (for context):"
            for decision in recent_decisions[:2]:  # Only last 2
                base_prompt += f"\n- Previous query: {decision['query'][:100]}..."
        
        return base_prompt
