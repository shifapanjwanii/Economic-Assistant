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
        """Get current CPI inflation rate (year-over-year percentage change)"""
        # Fetch 13+ months of data to calculate YoY change
        if not self.api_key:
            return {"error": "FRED API key not configured"}
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=400)).strftime("%Y-%m-%d")
        
        params = {
            "series_id": "CPIAUCSL",
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
                
                observations = data.get("observations", [])
                if len(observations) >= 13:
                    current_cpi = float(observations[-1].get("value", 0))
                    previous_year_cpi = float(observations[-13].get("value", 0))
                    
                    if previous_year_cpi > 0:
                        yoy_inflation = ((current_cpi - previous_year_cpi) / previous_year_cpi) * 100
                        return {
                            "series_id": "CPIAUCSL",
                            "latest_value": round(yoy_inflation, 2),
                            "latest_date": observations[-1].get("date"),
                            "observations": observations[-13:],
                            "success": True
                        }
                
                return {"error": "Insufficient data for YoY calculation", "success": False}
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def get_unemployment_rate(self) -> Dict[str, Any]:
        """Get current unemployment rate"""
        return await self.get_series_data("UNRATE")
    
    async def get_federal_funds_rate(self) -> Dict[str, Any]:
        """Get current Federal Funds Rate"""
        return await self.get_series_data("FEDFUNDS")
    
    async def get_gdp_growth(self) -> Dict[str, Any]:
        """Get Real GDP growth rate (year-over-year percentage change, adjusted for inflation)"""
        if not self.api_key:
            return {"error": "FRED API key not configured"}
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=500)).strftime("%Y-%m-%d")
        
        params = {
            "series_id": "GDPC1",  # Real GDP, Chained 2012 Dollars
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
                
                observations = data.get("observations", [])
                if len(observations) >= 5:  # GDP is quarterly, so 5 quarters ~ 1.25 years
                    current_gdp = float(observations[-1].get("value", 0))
                    previous_year_gdp = float(observations[-5].get("value", 0))
                    
                    if previous_year_gdp > 0:
                        yoy_growth = ((current_gdp - previous_year_gdp) / previous_year_gdp) * 100
                        return {
                            "series_id": "GDPC1",
                            "latest_value": round(yoy_growth, 2),
                            "latest_date": observations[-1].get("date"),
                            "observations": observations[-5:],
                            "success": True
                        }
                
                return {"error": "Insufficient data for YoY calculation", "success": False}
                
        except Exception as e:
            return {"error": str(e), "success": False}
    
    async def get_historical_exchange_rates(self, currency: str, days: int = 365) -> Dict[str, Any]:
        """Get historical exchange rates from FRED for a specific currency"""
        if not self.api_key:
            return {"error": "FRED API key not configured"}
        
        # Map currency codes to FRED series IDs
        currency_series_map = {
            "EUR": "DEXUSEU",  # U.S. / Euro Foreign Exchange Rate
            "GBP": "DEXUSUK",  # U.S. / U.K. Foreign Exchange Rate
            "JPY": "DEXJPUS",  # Japan / U.S. Foreign Exchange Rate
            "CAD": "DEXCAUS",  # Canada / U.S. Foreign Exchange Rate
            "AUD": "DEXUSAL",  # Australia / U.S. Foreign Exchange Rate
            "CHF": "DEXSZUS",  # Switzerland / U.S. Foreign Exchange Rate
        }
        
        series_id = currency_series_map.get(currency.upper())
        if not series_id:
            return {"error": f"Currency {currency} not supported", "success": False}
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
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
                
                observations = data.get("observations", [])
                
                # Filter out missing values and convert to proper format
                historical_data = []
                for obs in observations:
                    value = obs.get("value")
                    if value and value != ".":  # FRED uses "." for missing values
                        try:
                            historical_data.append({
                                "date": obs.get("date"),
                                "rate": float(value)
                            })
                        except (ValueError, TypeError):
                            continue
                
                if historical_data:
                    return {
                        "currency": currency,
                        "series_id": series_id,
                        "historical_data": historical_data,
                        "success": True
                    }
                
                return {"error": "No data available", "success": False}
                
        except Exception as e:
            return {"error": str(e), "success": False}


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
    
    async def get_historical_exchange_rates(
        self, 
        currency: str,
        base_currency: str = "USD",
        days: int = 365
    ) -> Dict[str, Any]:
        """Get historical exchange rates for a specific currency pair over time"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Sample dates across the year (monthly data points)
            dates_to_fetch = []
            current = start_date
            while current <= end_date:
                dates_to_fetch.append(current.strftime("%Y-%m-%d"))
                current += timedelta(days=30)  # Roughly monthly
            
            # Add the most recent date
            if dates_to_fetch[-1] != end_date.strftime("%Y-%m-%d"):
                dates_to_fetch.append(end_date.strftime("%Y-%m-%d"))
            
            historical_data = []
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch historical data for each date
                for date_str in dates_to_fetch:
                    try:
                        # Check if date is in the past or today
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                        if date_obj > datetime.now():
                            continue
                            
                        response = await client.get(
                            f"{self.base_url}/{date_str}",
                            params={"base": base_currency}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            rates = data.get("rates", {})
                            
                            if currency in rates:
                                historical_data.append({
                                    "date": date_str,
                                    "rate": rates[currency]
                                })
                    except Exception as e:
                        # Skip this date if there's an error
                        continue
            
            return {
                "base": base_currency,
                "currency": currency,
                "historical_data": historical_data,
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
