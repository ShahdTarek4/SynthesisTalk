from duckduckgo_search import DDGS

def search_web(query: str):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            return [
                {"title": r["title"], "href": r["href"], "body": r["body"]}
                for r in results
            ]
    except Exception as e:
        print("⚠️ DuckDuckGo error or rate limit:", e)
        return [{
            "title": "Search Error",
            "href": "",
            "body": "DuckDuckGo request failed (possibly due to rate limiting). Please try again later."
        }]
