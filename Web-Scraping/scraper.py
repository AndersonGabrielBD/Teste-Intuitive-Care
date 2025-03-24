import os
import aiohttp
import asyncio
import zipfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from tqdm.asyncio import tqdm_asyncio

class ANSDownloader:
    
    def __init__(self):
        self.base_url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
        self.download_dir = "./Web-scraping/output/ans_pdfs"
        self.zip_name = "./Web-scraping/output/ans_pdfs.zip"
        self.timeout = aiohttp.ClientTimeout(total=120)  # 2 minutos timeout
        self.chunk_size = 65536  # 64KB chunks
        self.max_connections = 20  # Conexões simultâneas

    async def create_connector(self):
        return aiohttp.TCPConnector(limit=self.max_connections, force_close=True)

    async def fetch_links(self, session):
        try:
            async with session.get(self.base_url) as response:
                response.raise_for_status()
                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")
                return [
                    urljoin(self.base_url, a["href"])
                    for a in soup.find_all("a", href=True)
                    if "anexo" in a["href"].lower() and a["href"].endswith(".pdf")
                ]
        except Exception as e:
            print(f"Erro ao buscar links: {str(e)}")
            return []

    async def download_pdf(self, session, url, semaphore, pbar):
        async with semaphore:
            try:
                pdf_name = os.path.basename(url).split("?")[0]
                pdf_path = os.path.join(self.download_dir, pdf_name)
                
                if os.path.exists(pdf_path):
                    pbar.update(1)
                    return pdf_path
                
                async with session.get(url) as response:
                    response.raise_for_status()
                    with open(pdf_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(self.chunk_size):
                            f.write(chunk)
                
                pbar.update(1)
                return pdf_path
            except Exception as e:
                print(f"\nErro no download {url}: {str(e)}")
                pbar.update(1)
                return None

    async def download_all(self, session, links):
        os.makedirs(self.download_dir, exist_ok=True)
        semaphore = asyncio.Semaphore(self.max_connections)
        
        with tqdm_asyncio(total=len(links), desc="Download Turbo") as pbar:
            tasks = [self.download_pdf(session, url, semaphore, pbar) for url in links]
            return await asyncio.gather(*tasks)

    def create_zip(self, files):
        with zipfile.ZipFile(self.zip_name, "w", zipfile.ZIP_DEFLATED, compresslevel=3) as zipf:
            for file in filter(None, files):
                if file and os.path.exists(file): 
                    zipf.write(file, os.path.basename(file))

    async def run(self):
        print(" Iniciando download...")
        
        connector = await self.create_connector()
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers={"User-Agent": "Mozilla/5.0"}
        ) as session:
            
            links = await self.fetch_links(session)
            if not links:
                print("Nenhum PDF encontrado!")
                return False
                
            print(f" Encontrados {len(links)} arquivos para download")
            downloaded = await self.download_all(session, links)
            self.create_zip(downloaded)
            
            success_count = len([f for f in downloaded if f])
            print(f"\n Concluído! {success_count}/{len(links)} arquivos baixados")
            print(f" Arquivo ZIP criado: {self.zip_name}")
            return success_count > 0

def main():
    downloader = ANSDownloader()
    asyncio.run(downloader.run())

if __name__ == "__main__":
    main()