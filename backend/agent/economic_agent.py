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
        # Retrieve user profile to get explanation depth preference
        user_profile = await self.memory_service.get_user_profile(user_id)
        explanation_depth = user_profile.get("preferences", {}).get("explanation_depth", "moderate") if user_profile else "moderate"
        max_tokens = self._get_max_tokens_for_depth(explanation_depth)
        
        # Build system prompt with explanation depth guidance
        system_prompt = self._build_base_system_prompt(explanation_depth)
        
        # Build conversation messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Retrieve conversation history from memory
        conversation_history = await self.memory_service.get_conversation_history(user_id, limit=5)
        
        # Add user profile context as the first message after system prompt
        if user_profile:
            profile_context = self._build_user_context(user_profile)
            messages.append({
                "role": "user",
                "content": profile_context
            })
            messages.append({
                "role": "assistant",
                "content": "I've noted your profile. Ready to help with your economic decisions."
            })
        
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
                max_tokens=max_tokens
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
    
    def _build_base_system_prompt(self, explanation_depth: str = "moderate") -> str:
        """Build base system prompt without user-specific context"""
        base_prompt = """You are Pulse - an intelligent assistant that helps users make informed everyday economic and financial decisions by reading between the rates using real-time macroeconomic data.

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
- IMPORTANT: Always tailor recommendations to the user's profile - their risk tolerance, debt level, and financial goals
"""
        
        # Add explanation depth guidelines
        if explanation_depth.lower() == "brief":
            base_prompt += "\nRESPONSE STYLE: Provide concise, focused responses. Keep explanations brief and to the point. Use bullet points when helpful. Aim for clarity over detail."
        elif explanation_depth.lower() == "detailed":
            base_prompt += "\nRESPONSE STYLE: Provide comprehensive, in-depth responses. Include detailed explanations, examples, and context. Cover multiple perspectives and nuances."
        else:  # moderate
            base_prompt += "\nRESPONSE STYLE: Provide balanced responses with adequate detail. Include key explanations and examples without being overly verbose."
        
        return base_prompt

    def _get_max_tokens_for_depth(self, explanation_depth: str) -> int:
        """Return max tokens based on explanation depth preference"""
        depth_tokens = {
            "brief": 500,
            "moderate": 1000,
            "detailed": 2000
        }
        return depth_tokens.get(explanation_depth.lower(), 1000)

    def _build_user_context(self, user_profile: Dict[str, Any]) -> str:
        """Build user context message that includes current profile info"""
        context = "Here's my current financial profile:\n"
        
        if user_profile.get("income_range"):
            context += f"- Income range: {user_profile['income_range']}\n"
        
        if user_profile.get("debt_level"):
            context += f"- Current debt: ${user_profile['debt_level']:,.2f}\n"
        
        if user_profile.get("dependents"):
            context += f"- Dependents: {user_profile['dependents']}\n"
        
        if user_profile.get("risk_tolerance"):
            context += f"- Risk tolerance: {user_profile['risk_tolerance']}\n"
        
        if user_profile.get("financial_goals"):
            goals = user_profile['financial_goals']
            if goals and any(goals.values()):
                goals_list = [str(v) for v in goals.values() if v]
                context += f"- Financial goals: {', '.join(goals_list)}\n"
        
        return context

    def _build_system_prompt(
        self,
        user_profile: Optional[Dict[str, Any]],
        recent_decisions: List[Dict[str, Any]]
    ) -> str:
        """Build system prompt with user context - DEPRECATED: Use _build_base_system_prompt and _build_user_context instead"""
        base_prompt = """You are Pulse - an intelligent assistant that helps users make informed everyday economic and financial decisions by reading between the rates using real-time macroeconomic data.

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
