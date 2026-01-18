from duckduckgo_search import DDGS 

class SearchAgent:
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query, max_results = 3):
        '''
        Search the web for the given query and return the results.
        '''
        print(f"[Search] Googling: '{query}'...")
        try: 
            results = self.ddgs.text(query, max_results = max_results)
            if not results:
                return "No results found."

            context_text = '### search results ###\n'
            for i, res in enumerate(results):
                context_text += f"Source {i+1}: {res['title']}\n"
                context_text +=  f"URL: {res['href']}\n"
                context_text += f"Content: {res['body']}\n\n"
            return context_text

        except Exception as e:
            print(f"[ERROR] Search Failed: {e}")
            return None
            