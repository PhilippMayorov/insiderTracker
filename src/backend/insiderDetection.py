"""
Insider Trading Detection Module
Identifies markets with potential for insider trading based on headlines
"""
import os
import re
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_openai_client() -> Optional[OpenAI]:
    """Return an OpenAI client if OPENAI_API_KEY is available and the openai
    package is installed, otherwise None.
=
    This avoids raising an exception on import when the key is not set and
    allows the module to fall back to a keyword-based heuristic.
    """

    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_KEY')
    
    if not api_key:
        # Debug: Check if .env was loaded
        if os.getenv('DEBUG'):
            print("DEBUG: No OpenAI API key found in environment variables")
            print(f"DEBUG: Checked OPENAI_API_KEY and OPENAI_KEY")
            print(f"DEBUG: Current working directory: {os.getcwd()}")
        return None

    try:
        return OpenAI(api_key=api_key)
    except Exception as e:
        if os.getenv('DEBUG'):
            print(f"DEBUG: Failed to instantiate OpenAI client: {e}")
        return None


# Keywords that suggest insider-sensitive events
# These are organized by category with priority weighting
INSIDER_KEYWORDS = {
    # HIGHEST PRIORITY: Personal/Relationship (often known only to inner circle)
    'personal_relationship': {
        'keywords': ['divorce', 'pregnant', 'pregnancy', 'married', 'marry', 'engaged', 
                    'engagement', 'baby', 'relationship', 'dating', 'breakup', 'break up',
                    'split', 'expecting', 'cheating', 'affair'],
        'priority': 'high'
    },
    
    # HIGH PRIORITY: Release or announcement events (known in advance by insiders)
    'release_announcement': {
        'keywords': ['release', 'announce', 'announcement', 'launch', 'reveal', 
                    'premiere', 'unveil', 'debut', 'tour', 'album', 'drop', 
                    'event', 'concert', 'show', 'perform'],
        'priority': 'high'
    },
    
    # HIGH PRIORITY: Political/Government decisions (known to officials first)
    'political_government': {
        'keywords': ['election', 'resign', 'resignation', 'out as', 'step down',
                    'appoint', 'appointment', 'vacancy', 'policy', 'law', 'act',
                    'treaty', 'withdraw', 'sanction', 'pardon'],
        'priority': 'high'
    },
    
    # MEDIUM PRIORITY: Corporate events (insiders have early knowledge)
    'corporate': {
        'keywords': ['merger', 'acquisition', 'buyout', 'takeover', 'ipo', 
                    'earnings', 'ceo', 'executive'],
        'priority': 'medium'
    },
    
    # MEDIUM PRIORITY: Regulatory decisions
    'regulatory': {
        'keywords': ['approve', 'approval', 'sec', 'fda', 'regulator', 'legislation', 
                    'regulate', 'authorize', 'authorization'],
        'priority': 'medium'
    },
}

# Keywords to EXCLUDE (markets based on public information or pure speculation)
# These should be checked FIRST before checking insider keywords
EXCLUDE_KEYWORDS = [
    # Monetary policy (public Fed announcements)
    'rate cut', 'rate hike', 'interest rate', 'fed rate', 'federal reserve',
    'central bank', 'monetary policy',
    
    # Asset prices (pure speculation)
    'price', 'reach', 'hit', 'above', 'below', '$', 
    'bitcoin', 'btc', 'eth', 'ethereum', 'crypto', 'cryptocurrency',
    'stock price', 'market cap', 'gold', 'silver', 'value',
    
    # Sports (outcomes not insider-knowable)
    'sports', 'game', 'match', 'win', 'lose', 'championship', 
    'score', 'team', 'player', 'nfl', 'nba', 'mlb', 'fifa',
    
    # Weather/Natural events
    'weather', 'temperature', 'rain', 'snow', 'storm', 'hurricane',
    
    # Public box office / verifiable metrics
    'box office', 'gross', 'opening weekend',
]


def is_insider_market(markets: List[Dict]) -> List[Dict]:
    """
    Iterate through a list of markets and return those with high potential 
    for insider trading based on their headlines.
    
    Args:
        markets: List of market dictionaries, each containing at least a 'headline' key
        
    Returns:
        List of market dictionaries flagged as potentially insider-sensitive,
        with an added 'insider_score' field (0.0-1.0)
    """
    flagged_markets = []
    
    for market in markets:
        headline = market.get('headline') or market.get('question') or market.get('title', '')
        
        if headline and is_potentially_insider_headline(headline):
            # Create a copy of the market dict and add the insider score
            flagged_market = market.copy()
            flagged_market['insider_score'] = insider_score(headline)
            flagged_markets.append(flagged_market)
    
    return flagged_markets


def is_potentially_insider_headline(headline: str) -> bool:
    """
    Determine whether a market headline could be influenced by insider knowledge
    using rule-based and OpenAI-based logic.
    
    Criteria for Insider-Potential (HIGH PRIORITY):
    ✅ Personal/Relationship events (divorce, pregnancy, marriage, dating)
    ✅ Release or announcement events (product launches, tours, albums)
    ✅ Political or government decisions (resignations, appointments, policy)
    
    Criteria for Insider-Potential (MEDIUM PRIORITY):
    ✅ Corporate events (mergers, acquisitions, earnings)
    ✅ Regulatory decisions (SEC, FDA approvals)
    
    ❌ Excluded:
    - Monetary policy (Fed rate decisions - public announcements)
    - Asset price predictions (Bitcoin, stocks, gold)
    - Sports outcomes
    - Weather or natural events
    - Publicly verifiable metrics (box office numbers)
    
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
    Check headline against insider keywords using priority-based heuristics.
    
    Args:
        headline_lower: Lowercase headline text
        
    Returns:
        True if insider keywords found (especially high-priority ones),
        False if clearly not insider-related,
        None if ambiguous (needs OpenAI check)
    """
    high_priority_match = False
    medium_priority_match = False
    
    for category, data in INSIDER_KEYWORDS.items():
        keywords = data['keywords']
        priority = data['priority']
        
        for keyword in keywords:
            if keyword in headline_lower:
                if priority == 'high':
                    # Personal relationships, releases, political events are strong signals
                    return True
                elif priority == 'medium':
                    medium_priority_match = True
    
    # If we found medium-priority matches, consider it insider-sensitive
    if medium_priority_match:
        return True
    
    # No matches found
    return False


def insider_score(headline: str) -> float:
    """
    Return a score between 0.0 and 1.0 for insider risk intensity.
    
    Score ranges:
    - 0.9-1.0: HIGH priority insider-sensitive (personal/relationship, major announcements)
    - 0.6-0.8: MEDIUM priority insider-sensitive (corporate, regulatory)
    - 0.0-0.3: Public information or excluded categories
    
    Args:
        headline: Market headline/question to evaluate
        
    Returns:
        Float score between 0.0 (no insider risk) and 1.0 (high insider risk)
    """
    if not headline:
        return 0.0
    
    headline_lower = headline.lower()
    
    # Step 1: Check exclusions (score = 0.0)
    if _should_exclude_headline(headline_lower):
        return 0.0
    
    # Step 2: Check for high-priority keywords
    for category, data in INSIDER_KEYWORDS.items():
        keywords = data['keywords']
        priority = data['priority']
        
        for keyword in keywords:
            if keyword in headline_lower:
                if priority == 'high':
                    # Personal relationships, releases, political events
                    if category == 'personal_relationship':
                        return 1.0  # Highest confidence
                    elif category in ['release_announcement', 'political_government']:
                        return 0.95
                elif priority == 'medium':
                    # Corporate and regulatory events
                    return 0.7
    
    # No insider keywords found
    return 0.1  # Low default score (not definitively excluded, but no signals)


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
            # Only print warning once per run
            if not hasattr(_check_with_openai, '_warned'):
                print("⚠️  OpenAI API key not found; using keyword-based classification only.")
                print("   Set OPENAI_API_KEY in your .env file for improved accuracy.")
                _check_with_openai._warned = True
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
    # Test cases covering all priority levels
    test_markets = [
        # HIGH PRIORITY: Personal/Relationship (should be flagged)
        {"headline": "Hailey Bieber pregnant in 2025?"},
        {"headline": "Jay-Z & Beyoncé divorce in 2025?"},
        {"headline": "Nara & Lucky divorce in 2025?"},
        {"headline": "Lana Del Rey divorce in 2025?"},
        {"headline": "Taylor Swift engaged in 2025?"},
        
        # HIGH PRIORITY: Release/Announcement (should be flagged)
        {"headline": "Britney Spears tour in 2025?"},
        {"headline": "Will the next iPhone be announced before October 2025?"},
        {"headline": "Drake album release in 2025?"},
        
        # HIGH PRIORITY: Political/Government (should be flagged)
        {"headline": "Will Biden resign before 2026?"},
        {"headline": "Trump out as Republican nominee?"},
        
        # MEDIUM PRIORITY: Corporate/Regulatory (should be flagged)
        {"headline": "Will the SEC approve the Bitcoin ETF by June 2025?"},
        {"headline": "Will Apple acquire Disney before 2026?"},
        {"headline": "Will the FDA approve Alzheimer's drug X in Q1 2025?"},
        
        # EXCLUDED: Monetary policy (should NOT be flagged)
        {"headline": "Will the Federal Reserve raise interest rates in June 2025?"},
        {"headline": "Will 5 Fed rate cuts happen in 2025?"},
        
        # EXCLUDED: Asset prices (should NOT be flagged)
        {"headline": "Will Bitcoin reach $100k by December 2025?"},
        {"headline": "Will Bitcoin reach $150,000 by December 2025?"},
        {"headline": "Will Ethereum hit $10k in 2025?"},
        
        # EXCLUDED: Sports (should NOT be flagged)
        {"headline": "Will the Lakers win the championship this year?"},
        
        # EXCLUDED: Weather (should NOT be flagged)
        {"headline": "Will it rain in New York tomorrow?"},
    ]
    
    print("Testing is_insider_market function:")
    print("=" * 80)

    flagged = is_insider_market(test_markets)
    
    print(f"\nFound {len(flagged)} markets with insider potential:\n")
    for market in flagged:
        score = market.get('insider_score', 0.0)
        print(f"✅ [{score:.2f}] {market['headline']}")
    
    print(f"\n{len(test_markets) - len(flagged)} markets excluded:\n")
    for market in test_markets:
        if market not in flagged:
            score = insider_score(market['headline'])
            print(f"❌ [{score:.2f}] {market['headline']}")
