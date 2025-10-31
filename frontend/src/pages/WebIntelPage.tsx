import { useState } from 'react';
import { Search, Globe, ExternalLink, Clock, Zap, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

interface WebIntelResult {
  title: string;
  url: string;
  snippet: string;
  relevance: number;
}

interface Brief {
  summary: string;
  sources: string[];
  timestamp: string;
}

export default function WebIntelPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<WebIntelResult[]>([]);
  const [brief, setBrief] = useState<Brief | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isGeneratingBrief, setIsGeneratingBrief] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    setResults([]);

    try {
      const response = await api.client.post('/api/webintel/query', {
        query: query.trim(),
        max_results: 10,
      });

      setResults(response.data.results || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la recherche web');
      console.error('Search error:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const generateBrief = async () => {
    if (!query.trim()) return;

    setIsGeneratingBrief(true);
    setError(null);

    try {
      const response = await api.client.get('/api/webintel/brief', {
        params: { topic: query.trim() },
      });

      setBrief({
        summary: response.data.summary || 'Brief généré avec succès',
        sources: response.data.sources || [],
        timestamp: new Date().toISOString(),
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la génération du brief');
      console.error('Brief generation error:', err);
    } finally {
      setIsGeneratingBrief(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Web Intelligence</h1>
        <p className="text-gray-600">
          Recherchez sur le web et générez des briefs intelligents
        </p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-red-800">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">
            ×
          </button>
        </div>
      )}

      {/* Search Bar */}
      <div className="card">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Recherchez n'importe quoi sur le web..."
                className="input pl-10"
              />
            </div>
            <button
              type="submit"
              disabled={isSearching || !query.trim()}
              className="btn btn-primary whitespace-nowrap min-w-[120px]"
            >
              {isSearching ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Recherche...
                </div>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2 inline" />
                  Rechercher
                </>
              )}
            </button>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={generateBrief}
              disabled={isGeneratingBrief || !query.trim()}
              className="btn btn-secondary flex items-center gap-2"
            >
              {isGeneratingBrief ? (
                <>
                  <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
                  Génération...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Générer un brief
                </>
              )}
            </button>
            <div className="flex-1 flex items-center gap-2 text-xs text-gray-500">
              <Globe className="w-4 h-4" />
              <span>
                Recherche intelligente avec analyse contextuelle et génération de synthèse
              </span>
            </div>
          </div>
        </form>
      </div>

      {/* Brief */}
      {brief && (
        <div className="card border-2 border-primary-200 bg-primary-50">
          <div className="flex items-center gap-2 mb-4">
            <Zap className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-primary-900">Brief Intelligent</h2>
            <span className="text-xs text-primary-600 ml-auto flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(brief.timestamp).toLocaleTimeString('fr-FR')}
            </span>
          </div>

          <div className="prose prose-sm max-w-none mb-4">
            <p className="text-gray-800 whitespace-pre-wrap">{brief.summary}</p>
          </div>

          {brief.sources.length > 0 && (
            <div className="pt-4 border-t border-primary-200">
              <p className="text-xs font-medium text-primary-800 mb-2">Sources:</p>
              <div className="flex flex-wrap gap-2">
                {brief.sources.map((source, index) => (
                  <span
                    key={index}
                    className="text-xs px-2 py-1 bg-white text-primary-700 rounded border border-primary-200"
                  >
                    {source}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-primary-600" />
            Résultats de recherche ({results.length})
          </h2>

          <div className="space-y-4">
            {results.map((result, index) => (
              <div
                key={index}
                className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 flex-1">{result.title}</h3>
                  {result.relevance && (
                    <span className="ml-3 text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                      {(result.relevance * 100).toFixed(0)}% pertinent
                    </span>
                  )}
                </div>

                <p className="text-sm text-gray-600 mb-3 line-clamp-2">{result.snippet}</p>

                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-primary-600 hover:text-primary-800 flex items-center gap-1"
                >
                  <ExternalLink className="w-3 h-3" />
                  {result.url}
                </a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!isSearching && results.length === 0 && !brief && (
        <div className="card text-center py-16">
          <Globe className="w-20 h-20 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Recherchez sur le web
          </h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Utilisez l'intelligence artificielle pour rechercher, analyser et synthétiser
            des informations du web en temps réel.
          </p>
          <div className="flex gap-4 justify-center text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <Search className="w-4 h-4" />
              <span>Recherche avancée</span>
            </div>
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              <span>Briefs automatiques</span>
            </div>
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4" />
              <span>Sources vérifiées</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
