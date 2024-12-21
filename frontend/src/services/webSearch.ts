import { WebSearchResult } from '../types';

/**
 * Servicio para realizar búsquedas web
 * Integra diferentes fuentes de búsqueda y procesa los resultados
 */
class WebSearchService {
  private readonly MAX_RESULTS = 5;
  private readonly CACHE_DURATION = 1000 * 60 * 60; // 1 hora
  private cache: Map<string, { results: WebSearchResult[]; timestamp: number }>;

  constructor() {
    this.cache = new Map();
  }

  /**
   * Realiza una búsqueda web
   * @param query - Término de búsqueda
   * @returns Resultados de la búsqueda
   */
  async search(query: string): Promise<WebSearchResult[]> {
    try {
      // Verificar caché
      const cached = this.getCachedResults(query);
      if (cached) {
        return cached;
      }

      // Realizar búsqueda en paralelo en múltiples fuentes
      const results = await Promise.all([
        this.searchDuckDuckGo(query),
        // TODO: Agregar más fuentes de búsqueda
      ]);

      // Combinar y filtrar resultados
      const combinedResults = this.processResults(
        results.flat().filter(Boolean)
      );

      // Guardar en caché
      this.cacheResults(query, combinedResults);

      return combinedResults;

    } catch (error) {
      console.error('Error en búsqueda web:', error);
      throw new Error('Error al realizar la búsqueda web');
    }
  }

  /**
   * Realiza una búsqueda en DuckDuckGo
   */
  private async searchDuckDuckGo(query: string): Promise<WebSearchResult[]> {
    try {
      // Usar la API de DuckDuckGo
      const response = await fetch(
        `https://api.duckduckgo.com/?q=${encodeURIComponent(query)}&format=json`
      );

      if (!response.ok) {
        throw new Error('Error en la respuesta de DuckDuckGo');
      }

      const data = await response.json();

      // Transformar resultados al formato común
      return data.RelatedTopics?.map((topic: any) => ({
        title: topic.Text?.split(' - ')[0] || '',
        snippet: topic.Text || '',
        url: topic.FirstURL || '',
        source: 'DuckDuckGo'
      })) || [];

    } catch (error) {
      console.error('Error en búsqueda DuckDuckGo:', error);
      return [];
    }
  }

  /**
   * Procesa y filtra los resultados de búsqueda
   */
  private processResults(results: WebSearchResult[]): WebSearchResult[] {
    // Eliminar duplicados basados en URL
    const uniqueResults = Array.from(
      new Map(results.map(r => [r.url, r])).values()
    );

    // Ordenar por relevancia (implementación básica)
    const sortedResults = uniqueResults.sort((a, b) => {
      const scoreA = this.calculateRelevanceScore(a);
      const scoreB = this.calculateRelevanceScore(b);
      return scoreB - scoreA;
    });

    // Limitar número de resultados
    return sortedResults.slice(0, this.MAX_RESULTS);
  }

  /**
   * Calcula un puntaje de relevancia para un resultado
   */
  private calculateRelevanceScore(result: WebSearchResult): number {
    let score = 0;

    // Longitud del snippet (preferir resultados más detallados)
    score += Math.min(result.snippet.length / 100, 5);

    // Presencia de URL (preferir resultados con URLs válidas)
    if (result.url && result.url.startsWith('http')) {
      score += 2;
    }

    // Fuente confiable (ejemplo básico)
    if (result.url.includes('.edu') || result.url.includes('.gov')) {
      score += 3;
    }

    return score;
  }

  /**
   * Obtiene resultados cacheados si están disponibles y vigentes
   */
  private getCachedResults(query: string): WebSearchResult[] | null {
    const cached = this.cache.get(query);
    if (!cached) return null;

    const isExpired = Date.now() - cached.timestamp > this.CACHE_DURATION;
    if (isExpired) {
      this.cache.delete(query);
      return null;
    }

    return cached.results;
  }

  /**
   * Guarda resultados en caché
   */
  private cacheResults(query: string, results: WebSearchResult[]): void {
    this.cache.set(query, {
      results,
      timestamp: Date.now()
    });

    // Limpiar caché antigua
    this.cleanCache();
  }

  /**
   * Limpia entradas antiguas del caché
   */
  private cleanCache(): void {
    const now = Date.now();
    for (const [query, data] of this.cache.entries()) {
      if (now - data.timestamp > this.CACHE_DURATION) {
        this.cache.delete(query);
      }
    }
  }
}

// Exportar una instancia única del servicio
export const webSearchService = new WebSearchService();
