import asyncio

from langchain_core.documents import Document
from retrievers.tavily.tavily_search import TavilySearch

class ResearchConductor:
    """Manages and coordinates the research process."""
    async def conduct_research(self, query):
        """
        Runs the GPT Researcher to conduct research
        """
		
        web_context = await self.__get_context_by_search(query)
        # self.researcher.context = f"Context from local documents: {docs_context}\n\nContext from web sources: {web_context}"
        # self.researcher.context = await self.__get_context_by_search(self.researcher.query, document_data)
        # self.researcher.context = await self.__get_context_by_vectorstore(self.researcher.query)

        #print("web_context", web_context)
        return web_context

    async def __get_context_by_search(self, query, scraped_data: list = []):
        """
        Generates the context for the research task by searching the query and scraping the results
        Returns:
            context: List of context
        """
        context = []
        # Generate Sub-Queries including original query
        # Using asyncio.gather to process the sub_queries asynchronously
        context = await self.__process_sub_query(query, scraped_data)

        return context

    async def __process_sub_query(self, sub_query: str, scraped_data: list = []):
        """Takes in a sub query and scrapes urls based on it and gathers context.

        Args:
            sub_query (str): The sub-query generated from the original query
            scraped_data (list): Scraped data passed in

        Returns:
            str: The context gathered from search
        """

        if not scraped_data:
            scraped_data = await self.__scrape_data_by_query(sub_query)
            # await self.__scrape_data_by_query(sub_query)

        #content = await self.context_manager.get_similar_content_by_query(sub_query, scraped_data)

        return [
            Document(page_content=item.get("raw_content"),
                                                       metadata={"source": item.get("href")}) for item in scraped_data if item.get("raw_content")
        ]

    async def __scrape_data_by_query(self, sub_query):
        """
        Runs a sub-query across multiple retrievers and scrapes the resulting URLs.

        Args:
            sub_query (str): The sub-query to search for.

        Returns:
            list: A list of scraped content results.
        """
        #print("__scrape_data_by_query")

        scraped_content = []

        retriever = TavilySearch(sub_query)

        # Perform the search using the current retriever
        search_results = await asyncio.to_thread(
            retriever.search,
            include_raw_content=True
        )

        scraped_content.extend(search_results)

        #print("search_results", len(search_results))

        return scraped_content

    def add_costs(self, cost: float) -> None:
        return
