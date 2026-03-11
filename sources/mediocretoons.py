import httpx
import time
import os

BASE_URL = "https://mediocrescan.com"
API_URL = "https://api.mediocretoons.site"


class MediocreToons:

    name = "MediocreToons"

    def __init__(self):

        self.token = None
        self.token_expiry = 0

        self.email = os.getenv("MEDIOCRE_EMAIL")
        self.password = os.getenv("MEDIOCRE_PASSWORD")

    # ==========================================================
    # TOKEN
    # ==========================================================

    async def get_token(self):

        now = time.time()

        if self.token and now < self.token_expiry:
            return self.token

        return await self.login()

    async def login(self):

        if not self.email or not self.password:
            return None

        url = f"{API_URL}/auth/login"

        payload = {
            "email": self.email.strip(),
            "senha": self.password
        }

        headers = {
            "x-app-key": "toons-mediocre-app",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient() as client:

            r = await client.post(url, json=payload, headers=headers)

            if r.status_code != 200:
                return None

            data = r.json()

            token = data.get("token") or data.get("access_token")

            if not token:
                return None

            expires = data.get("expiresIn", 3600)

            self.token = token
            self.token_expiry = time.time() + expires

            return token

    # ==========================================================
    # REQUEST
    # ==========================================================

    async def request(self, url, params=None):

        token = await self.get_token()

        headers = {
            "x-app-key": "toons-mediocre-app",
            "Referer": BASE_URL,
            "Origin": BASE_URL
        }

        if token:
            headers["Authorization"] = f"Bearer {token}"

        async with httpx.AsyncClient() as client:

            r = await client.get(url, params=params, headers=headers)

            if r.status_code == 401:
                self.token = None
                token = await self.login()

                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    r = await client.get(url, params=params, headers=headers)

            r.raise_for_status()

            return r.json()

    # ==========================================================
    # SEARCH
    # ==========================================================

    async def search(self, query):

        url = f"{API_URL}/obras"

        params = {
            "string": query,
            "pagina": 1,
            "limite": 20
        }

        data = await self.request(url, params)

        mangas = []

        for m in data["data"]:

            mangas.append({
                "title": m["nome"],
                "url": m["id"]
            })

        return mangas

    # ==========================================================
    # CHAPTERS
    # ==========================================================

    async def chapters(self, manga_id):

        chapters = []

        page = 1

        while True:

            url = f"{API_URL}/capitulos"

            params = {
                "obr_id": manga_id,
                "page": page,
                "limite": 100,
                "order": "desc"
            }

            data = await self.request(url, params)

            for c in data["data"]:

                chapters.append({
                    "chapter_number": c.get("numero"),
                    "url": c.get("id")
                })

            pagination = data.get("pagination")

            if not pagination or not pagination.get("hasNextPage"):
                break

            page += 1

        return chapters

    # ==========================================================
    # PAGES
    # ==========================================================

    async def pages(self, chapter_id):

        url = f"{API_URL}/capitulos/{chapter_id}"

        data = await self.request(url)

        pages = []

        for p in data["paginas"]:

            pages.append(p["url"])

        return pages
