import { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import { FileText, Upload, Trash2, Search, AlertCircle, X } from 'lucide-react';
import type { Document, SearchRequest, SearchResponse } from '../types';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoading(true);
      const data = await api.getDocuments();
      setDocuments(data);
      setError(null);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors du chargement des documents');
    } finally {
      setIsLoading(false);
    }
  };

  const uploadFile = async (file: File) => {
    setIsUploading(true);
    setError(null);

    try {
      await api.uploadDocument(file, 'documents');
      await loadDocuments();
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de l\'upload');
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    await uploadFile(file);
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      await uploadFile(file);
    }
  };

  const handleDeleteDocument = async (id: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) return;

    try {
      await api.deleteDocument(id);
      setDocuments(documents.filter((d) => d.id !== id));
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erreur lors de la suppression');
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const searchRequest: SearchRequest = {
        query: searchQuery,
        collection_name: 'documents',
        top_k: 5,
        enable_reranking: true,
      };
      const results = await api.searchDocuments(searchRequest);
      setSearchResults(results);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la recherche');
    } finally {
      setIsSearching(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Documents</h1>
          <p className="text-gray-600">
            Gérez vos documents et effectuez des recherches sémantiques
          </p>
        </div>
      </div>

      {/* Drag & Drop Upload Zone */}
      <div
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        className={`card border-2 border-dashed transition-all ${
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileUpload}
          className="hidden"
          accept=".pdf,.docx,.txt,.md,.html,.json,.csv"
        />
        <div className="text-center py-8">
          <div
            className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors ${
              isDragging ? 'bg-primary-100' : 'bg-gray-100'
            }`}
          >
            <Upload
              className={`w-8 h-8 ${
                isDragging ? 'text-primary-600' : 'text-gray-400'
              }`}
            />
          </div>
          {isUploading ? (
            <div className="space-y-2">
              <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-sm font-medium text-gray-700">Upload en cours...</p>
            </div>
          ) : (
            <>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {isDragging ? 'Déposez votre fichier ici' : 'Glissez-déposez un document'}
              </h3>
              <p className="text-sm text-gray-600 mb-4">
                ou{' '}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  parcourez vos fichiers
                </button>
              </p>
              <p className="text-xs text-gray-500">
                Formats supportés: PDF, DOCX, TXT, MD, HTML, JSON, CSV
              </p>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm text-red-800">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Search Bar */}
      <div className="card">
        <form onSubmit={handleSearch} className="flex gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher dans les documents..."
              className="input pl-10"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching}
            className="btn btn-primary whitespace-nowrap"
          >
            {isSearching ? 'Recherche...' : 'Rechercher'}
          </button>
        </form>
      </div>

      {/* Search Results */}
      {searchResults && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">
              Résultats de recherche ({searchResults.total_found})
            </h2>
            <button
              onClick={() => setSearchResults(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          <div className="space-y-4">
            {searchResults.results.map((result, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <span className="text-xs font-medium text-gray-500">
                    Score: {(result.score * 100).toFixed(1)}%
                  </span>
                  {result.metadata?.filename && (
                    <span className="text-xs text-gray-500">{result.metadata.filename}</span>
                  )}
                </div>
                <p className="text-sm text-gray-700 line-clamp-3">{result.content}</p>
              </div>
            ))}
          </div>
          <div className="mt-4 text-xs text-gray-500 text-right">
            Recherche effectuée en {searchResults.search_time_ms}ms
            {searchResults.reranked && ' (avec reranking)'}
          </div>
        </div>
      )}

      {/* Documents List */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">
          Mes documents ({documents.length})
        </h2>

        {documents.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucun document
            </h3>
            <p className="text-gray-600 mb-4">
              Commencez par uploader votre premier document
            </p>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn btn-primary mx-auto"
            >
              <Upload className="w-5 h-5 mr-2 inline" />
              Upload document
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                    Nom
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                    Type
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                    Taille
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                    Chunks
                  </th>
                  <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">
                    Date
                  </th>
                  <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-3">
                        <FileText className="w-5 h-5 text-primary-600 flex-shrink-0" />
                        <span className="text-sm font-medium text-gray-900 truncate max-w-xs">
                          {doc.filename}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                        {doc.file_type || 'N/A'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {formatFileSize(doc.file_size)}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {doc.chunks_count}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {new Date(doc.uploaded_at).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Supprimer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
