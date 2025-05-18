from duckduckgo_search import DDGS

def search_web(query: str):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)
        return [{"title": r["title"], "href": r["href"], "body": r["body"]} for r in results]
