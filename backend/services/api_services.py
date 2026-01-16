import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import config


class FREDService:
    """Service for interacting with Federal Reserve Economic Data API"""
    
    def __init__(self):
        self.base_url = config.FRED_BASE_URL
        self.api_key = config.FRED_API_KEY
        
    async def get_series_data(
        self, 
        series_id: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fetch data for a specific FRED series"""
        if not self.api_key:
            return {"error": "FRED API key not configured"}
        
        # Default to last year of data if no dates provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/series/observations",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract observations
                observations = data.get("observations", [])
                if observations:
                    latest = observations[-1]
                    return {
                        "series_id": series_id,
                        "latest_value": latest.get("value"),
                        "latest_date": latest.get("date"),
                        "observations": observations[-12:],  # Last 12 data points
                        "success": True
                    }
                return {"error": "No data available", "success": False}
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def get_inflation_rate(self) -> Dict[str, Any]:
        """Get current CPI inflation rate"""
        return await self.get_series_data("CPIAUCSL")
    
    async def get_unemployment_rate(self) -> Dict[str, Any]:
        """Get current unemployment rate"""
        return await self.get_series_data("UNRATE")
    
    async def get_federal_funds_rate(self) -> Dict[str, Any]:
        """Get current Federal Funds Rate"""
        return await self.get_series_data("FEDFUNDS")
    
    async def get_gdp_growth(self) -> Dict[str, Any]:
        """Get GDP growth rate"""
        return await self.get_series_data("GDP")


class NewsAPIService:
    """Service for interacting with News API"""
    
    def __init__(self):
        self.base_url = config.NEWS_API_BASE_URL
        self.api_key = config.NEWS_API_KEY
    
    async def get_economic_news(
        self, 
        query: str = "economy OR inflation OR federal reserve",
        days_back: int = 7,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Fetch recent economic news articles"""
        if not self.api_key:
            return {"error": "News API key not configured"}
        
        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "relevancy",
            "language": "en",
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/everything",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                articles = data.get("articles", [])
                return {
                    "articles": [
                        {
                            "title": article.get("title"),
                            "description": article.get("description"),
                            "source": article.get("source", {}).get("name"),
                            "url": article.get("url"),
                            "published_at": article.get("publishedAt")
                        }
                        for article in articles[:page_size]
                    ],
                    "total_results": data.get("totalResults", 0),
                    "success": True
                }
                
        except Exception as e:
            return {"error": str(e), "success": False}


class ExchangeRateService:
    """Service for interacting with Exchange Rate API"""
    
    def __init__(self):
        self.base_url = config.EXCHANGE_RATE_BASE_URL
        self.api_key = config.EXCHANGE_RATE_API_KEY
    
    async def get_exchange_rates(
        self, 
        base_currency: str = "USD"
    ) -> Dict[str, Any]:
        """Get current exchange rates for a base currency"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/latest/{base_currency}"
                )
                response.raise_for_status()
                data = response.json()
                
                return {
                    "base": data.get("base"),
                    "date": data.get("date"),
                    "rates": data.get("rates", {}),
                    "success": True
                }
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def compare_purchasing_power(
        self,
        amount: float,
        from_currency: str = "USD",
        to_currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Compare purchasing power between currencies"""
        rates_data = await self.get_exchange_rates(from_currency)
        
        if not rates_data.get("success"):
            return rates_data
        
        rates = rates_data.get("rates", {})
        if to_currency not in rates:
            return {"error": f"Currency {to_currency} not found", "success": False}
        
        converted_amount = amount * rates[to_currency]
        
        return {
            "original_amount": amount,
            "original_currency": from_currency,
            "converted_amount": round(converted_amount, 2),
            "converted_currency": to_currency,
            "exchange_rate": rates[to_currency],
            "date": rates_data.get("date"),
            "success": True
        }
