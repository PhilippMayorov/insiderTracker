"""
Insider Trading Detection Module
Identifies markets with potential for insider trading based on headlines
"""
import os
import re
from typing import List, Dict, Optional

# Defer importing OpenAI and loading secrets until needed to avoid raising
# at import time when the environment isn't configured (e.g. in tests).
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()


def get_openai_client() -> Optional[object]:
    """Return an OpenAI client if OPENAI_API_KEY is available, otherwise None.

    This avoids raising an exception on import when the key is not set and
    allows the module to fall back to a keyword-based heuristic.
    """
    try:
        from openai import OpenAI
    except Exception:
        # openai package not installed or not importable
        return None

    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY')
    if not api_key:
        return None

    return OpenAI(api_key=api_key)


# Keywords that suggest insider-sensitive events
INSIDER_KEYWORDS = {
    'release': ['release', 'launch', 'unveil', 'debut', 'rollout'],
    'announcement': ['announce', 'announcement', 'reveal', 'disclose'],
    'regulatory': ['approve', 'approval', 'sec', 'fda', 'regulator', 'legislation', 
                   'regulate', 'authorize', 'authorization'],
    'political': ['election', 'elect', 'vote', 'ballot', 'referendum', 'senate', 
                  'congress', 'parliament'],
    'monetary': ['interest rate', 'fed', 'federal reserve', 'central bank', 
                 'monetary policy', 'rate hike', 'rate cut'],
    'corporate': ['merger', 'acquisition', 'buyout', 'takeover', 'ipo', 
                  'earnings', 'quarterly report'],
    'meeting': ['meeting', 'summit', 'conference', 'decision'],
}

# Keywords to exclude (markets based on public information or speculation)
EXCLUDE_KEYWORDS = [
    'price', 'reach', 'hit', 'above', 'below', 'bitcoin', 'eth', 'crypto',
    'stock price', 'market cap', 'weather', 'temperature', 'sports', 'game',
    'win', 'championship', 'score', 'team'
]


def is_insider_market(markets: List[Dict]) -> List[Dict]:
    """
    Iterate through a list of markets and return those with high potential 
    for insider trading based on their headlines.
    
    Args:
        markets: List of market dictionaries, each containing at least a 'headline' key
        
    Returns:
        List of market dictionaries flagged as potentially insider-sensitive
    """
    flagged_markets = []
    
    for market in markets:
        headline = market.get('headline') or market.get('question') or market.get('title', '')
        
        if headline and is_potentially_insider_headline(headline):
            flagged_markets.append(market)
    
    return flagged_markets


def is_potentially_insider_headline(headline: str) -> bool:
    """
    Determine whether a market headline could be influenced by insider knowledge
    using rule-based and OpenAI-based logic.
    
    Criteria for Insider-Potential:
    ✅ Release or announcement events
    ✅ Political or regulatory decisions
    ✅ Privileged information events
    
    ❌ Excluded:
    - Asset price predictions
    - Sports, weather, or publicly observable events
    
    Args:
        headline: Market headline/question to evaluate
        
    Returns:
        True if headline meets insider criteria, False otherwise
    """
    if not headline:
        return False
    
    headline_lower = headline.lower()
    
    # Step 1: Quick exclusion check
    if _should_exclude_headline(headline_lower):
        return False
    
    # Step 2: Keyword-based heuristic check
    keyword_match = _check_insider_keywords(headline_lower)
    
    # Step 3: If keywords are ambiguous or no match, use OpenAI
    if keyword_match is None:  # Ambiguous case
        return _check_with_openai(headline)
    
    return keyword_match


def _should_exclude_headline(headline_lower: str) -> bool:
    """
    Check if headline should be excluded based on exclude keywords.
    
    Args:
        headline_lower: Lowercase headline text
        
    Returns:
        True if headline should be excluded
    """
    for exclude_keyword in EXCLUDE_KEYWORDS:
        if exclude_keyword in headline_lower:
            return True
    return False


def _check_insider_keywords(headline_lower: str) -> bool | None:
    """
    Check headline against insider keywords using heuristics.
    
    Args:
        headline_lower: Lowercase headline text
        
    Returns:
        True if insider keywords found, False if clearly not insider-related,
        None if ambiguous (needs OpenAI check)
    """
    matches = 0
    
    for category, keywords in INSIDER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in headline_lower:
                matches += 1
                # Strong indicators
                if category in ['regulatory', 'monetary', 'corporate', 'announcement']:
                    return True
    
    # If we found some matches but not strong ones, it's ambiguous
    if matches > 0:
        return None
    
    # No matches found
    return False


def _check_with_openai(headline: str) -> bool:
    """
    Use OpenAI API to classify headline as insider-sensitive or not.
    
    Args:
        headline: Market headline to classify
        
    Returns:
        True if classified as insider-sensitive, False otherwise
    """
    try:
        # Get an OpenAI client (may be None if no API key is configured)
        client = get_openai_client()
        if client is None:
            # No API key/config — fall back to conservative non-flagging
            print("OpenAI API key not found; skipping AI-based classification.")
            return False

        prompt = f"""You are an expert at identifying markets where insider trading could occur.

Analyze this prediction market headline and determine if it could be influenced by insider knowledge.

Headlines with INSIDER POTENTIAL include:
✅ Product releases, launches, or announcements (e.g., new iPhone, software release)
✅ Government/regulatory decisions (e.g., SEC approval, FDA authorization, interest rate decisions)
✅ Political events with advance information (e.g., election timing, policy decisions)
✅ Corporate events (mergers, acquisitions, earnings that insiders know in advance)
✅ Events where executives or officials have privileged information

Headlines WITHOUT insider potential include:
❌ Asset price predictions (crypto, stocks reaching certain values)
❌ Sports outcomes
❌ Weather predictions
❌ Publicly observable events with no privileged information

Headline: "{headline}"

Respond with ONLY "YES" if this has insider potential, or "NO" if it does not.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4o mini for cost efficiency
            messages=[
                {"role": "system", "content": "You are an expert analyst identifying insider trading potential in prediction markets."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=10
        )

        # Normalize the model output and check for affirmative answer
        answer = ""
        try:
            # Newer SDKs return choices with messages
            answer = response.choices[0].message.content.strip().upper()
        except Exception:
            # Fallback for different response shapes
            try:
                answer = str(response.choices[0].text).strip().upper()
            except Exception:
                answer = ""

        return answer == "YES"
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        # Fallback to conservative approach - if unsure, don't flag
        return False


# Example usage and testing
if __name__ == "__main__":
    # Test cases
    test_markets = [
        {"headline": "Will the Federal Reserve raise interest rates in June 2025?"},
        {"headline": "Will Bitcoin reach $100k by December 2025?"},
        {"headline": "Will the next iPhone be announced before October 2025?"},
        {"headline": "Will the SEC approve the Bitcoin ETF by June 2025?"},
        {"headline": "Will it rain in New York tomorrow?"},
        {"headline": "Will the Lakers win the championship this year?"},
        {"headline": "Will Apple acquire Disney before 2026?"},
        {"headline": "Will the FDA approve Alzheimer's drug X in Q1 2025?"},
    ]
    
    print("Testing is_insider_market function:")
    print("=" * 80)
    
    flagged = is_insider_market(test_markets)
    
    print(f"\nFound {len(flagged)} markets with insider potential:\n")
    for market in flagged:
        print(f"✅ {market['headline']}")
    
    print(f"\n{len(test_markets) - len(flagged)} markets excluded:\n")
    for market in test_markets:
        if market not in flagged:
            print(f"❌ {market['headline']}")
