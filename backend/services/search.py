# search.py - FIXED VERSION

from duckduckgo_search import DDGS
from services import reasoning  # make sure this is imported

def search_web(query: str, summarize: bool = True, context_summary: str = ""):
    """
    Enhanced search with context awareness
    """
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=5)
            if not results or all('title' not in r for r in results):
                return [{
                    "title": "Search Error",
                    "href": "",
                    "body": "DuckDuckGo returned no results. You may have hit a rate limit or provided too long of a query."
                }]

            cleaned_results = [
                {
                    "title": r.get("title", "No Title"),
                    "href": r.get("href", ""),
                    "body": r.get("body", "")
                }
                for r in results if "title" in r
            ]

            if summarize:
                combined_text = "\n".join(f"{r['title']}: {r['body']}" for r in cleaned_results)
                
                # Enhanced summary prompt with context awareness
                if context_summary:
                    summary_prompt = f"""Based on the following search results, provide an insightful overview that answers the query: "{query}". 
                    
Context from our conversation: {context_summary}

Connect the search results to our ongoing discussion when relevant. Be concise and clear.

Search results:
{combined_text}"""
                else:
                    summary_prompt = f"""Based on the following search results, provide an insightful overview or conclusion that answers the query: "{query}". Be concise and clear.

{combined_text}"""

                summary = reasoning.call_llm(summary_prompt)
                formatted_results = "\n".join(
                    f"• {r['title']}\n  {r['href']}" for r in cleaned_results
                )
                return f"🧠 Summary:\n{summary}\n\n🔗 Sources:\n{formatted_results}"

            return cleaned_results

    except Exception as e:
        print("⚠️ DuckDuckGo error:", e)
        return [{
            "title": "DuckDuckGo Search Error",
            "href": "",
            "body": "DuckDuckGo request failed. This may be due to rate limits or network error."
        }]