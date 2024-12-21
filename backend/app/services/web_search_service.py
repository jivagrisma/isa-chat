import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from loguru import logger
import re
from urllib.parse import quote_plus

from app.core.config import settings

class WebSearchService:
    """
    Servicio para realizar búsquedas web.
    Integra diferentes fuentes de búsqueda y procesa los resultados.
    """

    def __init__(self):
        """Inicializa el servicio de búsqueda web."""
        self.session = None
        self.cache = {}
        self.cache_duration = timedelta(hours=1)

    async def initialize(self):
        """Inicializa la sesión HTTP."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Cierra la sesión HTTP."""
        if self.session:
            await self.session.close()
            self.session = None

    async def search(
        self,
        query: str,
        max_results: int = 5,
        include_snippets: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda web.
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            include_snippets: Si se deben incluir fragmentos de texto
            
        Returns:
            List[Dict[str, Any]]: Lista de resultados
        """
        try:
            # Verificar caché
            cache_key = f"{query}_{max_results}_{include_snippets}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached

            # Realizar búsquedas en paralelo
            results = await self._search_all_sources(query, max_results)
            
            # Procesar y combinar resultados
            processed_results = self._process_results(results, include_snippets)
            
            # Guardar en caché
            self._cache_results(cache_key, processed_results)
            
            return processed_results[:max_results]
            
        except Exception as e:
            logger.error(f"Error en búsqueda web: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al realizar la búsqueda web"
            )

    async def _search_all_sources(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Realiza búsquedas en todas las fuentes disponibles.
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            List[Dict[str, Any]]: Resultados combinados
        """
        tasks = [
            self._search_duckduckgo(query, max_results),
            # Agregar más fuentes aquí
        ]
        
        results = []
        for task in tasks:
            try:
                result = await task
                results.extend(result)
            except Exception as e:
                logger.error(f"Error en fuente de búsqueda: {e}")
                continue
                
        return results

    async def _search_duckduckgo(
        self,
        query: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Realiza una búsqueda en DuckDuckGo.
        
        Args:
            query: Término de búsqueda
            max_results: Número máximo de resultados
            
        Returns:
            List[Dict[str, Any]]: Resultados de DuckDuckGo
        """
        if not self.session:
            await self.initialize()

        try:
            encoded_query = quote_plus(query)
            url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json"
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Error en DuckDuckGo API: {response.status}")
                    
                data = await response.json()
                
                results = []
                for topic in data.get('RelatedTopics', [])[:max_results]:
                    if 'Text' in topic:
                        # Separar título y snippet
                        text = topic.get('Text', '')
                        title = text.split(' - ')[0] if ' - ' in text else text
                        snippet = text.split(' - ')[1] if ' - ' in text else ''
                        
                        results.append({
                            'title': title,
                            'url': topic.get('FirstURL', ''),
                            'snippet': snippet,
                            'source': 'DuckDuckGo',
                            'timestamp': datetime.utcnow().isoformat()
                        })
                        
                return results
                
        except Exception as e:
            logger.error(f"Error en búsqueda DuckDuckGo: {e}")
            return []

    def _process_results(
        self,
        results: List[Dict[str, Any]],
        include_snippets: bool
    ) -> List[Dict[str, Any]]:
        """
        Procesa y filtra los resultados de búsqueda.
        
        Args:
            results: Lista de resultados
            include_snippets: Si se deben incluir fragmentos
            
        Returns:
            List[Dict[str, Any]]: Resultados procesados
        """
        # Eliminar duplicados
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                
                # Limpiar y validar resultado
                processed = {
                    'title': self._clean_text(result.get('title', '')),
                    'url': url,
                    'source': result.get('source', 'Unknown'),
                    'timestamp': result.get('timestamp', datetime.utcnow().isoformat())
                }
                
                if include_snippets:
                    processed['snippet'] = self._clean_text(result.get('snippet', ''))
                    
                # Calcular relevancia
                processed['score'] = self._calculate_relevance(processed)
                
                unique_results.append(processed)
                
        # Ordenar por relevancia
        return sorted(unique_results, key=lambda x: x['score'], reverse=True)

    def _clean_text(self, text: str) -> str:
        """
        Limpia y normaliza texto.
        
        Args:
            text: Texto a limpiar
            
        Returns:
            str: Texto limpio
        """
        # Eliminar HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalizar espacios
        text = ' '.join(text.split())
        
        # Eliminar caracteres especiales
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()

    def _calculate_relevance(self, result: Dict[str, Any]) -> float:
        """
        Calcula un puntaje de relevancia para un resultado.
        
        Args:
            result: Resultado a evaluar
            
        Returns:
            float: Puntaje de relevancia
        """
        score = 0.0
        
        # Longitud del título
        title_len = len(result.get('title', ''))
        if 20 <= title_len <= 100:
            score += 0.3
            
        # Longitud del snippet
        if 'snippet' in result:
            snippet_len = len(result['snippet'])
            if 50 <= snippet_len <= 300:
                score += 0.3
                
        # URL confiable
        url = result.get('url', '').lower()
        if any(domain in url for domain in ['.edu', '.gov', '.org']):
            score += 0.2
            
        # Fuente confiable
        if result.get('source') in ['DuckDuckGo']:
            score += 0.2
            
        return score

    def _get_from_cache(
        self,
        key: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Obtiene resultados del caché.
        
        Args:
            key: Clave de caché
            
        Returns:
            Optional[List[Dict[str, Any]]]: Resultados cacheados o None
        """
        if key in self.cache:
            timestamp, results = self.cache[key]
            if datetime.utcnow() - timestamp < self.cache_duration:
                return results
            else:
                del self.cache[key]
        return None

    def _cache_results(
        self,
        key: str,
        results: List[Dict[str, Any]]
    ) -> None:
        """
        Guarda resultados en caché.
        
        Args:
            key: Clave de caché
            results: Resultados a cachear
        """
        self.cache[key] = (datetime.utcnow(), results)
        
        # Limpiar caché antiguo
        self._clean_cache()

    def _clean_cache(self) -> None:
        """Limpia entradas antiguas del caché."""
        now = datetime.utcnow()
        expired_keys = [
            k for k, (t, _) in self.cache.items()
            if now - t > self.cache_duration
        ]
        for k in expired_keys:
            del self.cache[k]

    async def __aenter__(self):
        """Soporte para context manager asíncrono."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Limpieza al salir del context manager."""
        await self.close()

# Instancia global del servicio
web_search_service = WebSearchService()
