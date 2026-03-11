import zipfile
import httpx
import asyncio
import img2pdf

from io import BytesIO


async def download_image(client, url):
    try:
        r = await client.get(url, timeout=60)
        r.raise_for_status()
        return r.content
    except Exception as e:
        print("Erro ao baixar imagem:", e)
        return None


async def download_all_images(image_urls):

    async with httpx.AsyncClient() as client:
        tasks = [download_image(client, url) for url in image_urls]
        images = await asyncio.gather(*tasks)

    images = [img for img in images if img]

    if not images:
        raise Exception("Nenhuma imagem foi baixada")

    return images


# ======================================================
# CBZ
# ======================================================

async def create_cbz(image_urls, manga_title, chapter_name):

    images = await download_all_images(image_urls)

    safe_title = manga_title.replace("/", "").replace(" ", "_")
    safe_chapter = str(chapter_name).replace("/", "").replace(" ", "_")

    filename = f"{safe_title}_{safe_chapter}.cbz"

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as cbz:
        for i, img in enumerate(images):
            cbz.writestr(f"{i+1}.jpg", img)

    buffer.seek(0)

    return buffer, filename


# ======================================================
# PDF
# ======================================================

async def create_pdf(image_urls, manga_title, chapter_name):

    images = await download_all_images(image_urls)

    safe_title = manga_title.replace("/", "").replace(" ", "_")
    safe_chapter = str(chapter_name).replace("/", "").replace(" ", "_")

    filename = f"{safe_title}_{safe_chapter}.pdf"

    pdf_bytes = img2pdf.convert(images)

    buffer = BytesIO(pdf_bytes)

    return buffer, filename


# ======================================================
# CBR (RAR SIMULADO)
# ======================================================

async def create_cbr(image_urls, manga_title, chapter_name):

    images = await download_all_images(image_urls)

    safe_title = manga_title.replace("/", "").replace(" ", "_")
    safe_chapter = str(chapter_name).replace("/", "").replace(" ", "_")

    filename = f"{safe_title}_{safe_chapter}.cbr"

    buffer = BytesIO()

    # CBR normalmente é RAR, mas leitores aceitam ZIP
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as cbr:
        for i, img in enumerate(images):
            cbr.writestr(f"{i+1}.jpg", img)

    buffer.seek(0)

    return buffer, filename
