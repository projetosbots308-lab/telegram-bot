import httpx

ANILIST_API = "https://graphql.anilist.co"


async def search_anime_manga(query):

    graphql_query = """
    query ($search: String) {
      Media(search: $search) {
        title {
          romaji
          english
        }
        description
        genres
        averageScore
        seasonYear
        coverImage {
          extraLarge
        }
        format
      }
    }
    """

    variables = {"search": query}

    async with httpx.AsyncClient() as client:
        r = await client.post(
            ANILIST_API,
            json={"query": graphql_query, "variables": variables},
            timeout=30
        )

    data = r.json()["data"]["Media"]

    return {
        "title": data["title"]["english"] or data["title"]["romaji"],
        "description": data["description"],
        "genres": data["genres"],
        "score": data["averageScore"],
        "year": data["seasonYear"],
        "cover": data["coverImage"]["extraLarge"],
        "format": data["format"],
    }
