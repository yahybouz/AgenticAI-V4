import { useState } from 'react';
import { FileText, Calendar, Users, Download, CheckCircle2, Clock } from 'lucide-react';
import api from '../services/api';

interface Meeting {
  id: string;
  title: string;
  date: string;
  participants: string[];
  status: 'scheduled' | 'completed' | 'cr_generated';
}

interface CompteRendu {
  document_id: string;
  meeting_id: string;
  sections: {
    title: string;
    content: string;
  }[];
  trace_id: string;
}

interface CompiledDoc {
  artifact_path: string;
  trace_id: string;
}

export default function DocsPage() {
  const [meetings] = useState<Meeting[]>([
    {
      id: 'meet-1',
      title: 'Sprint Planning Q1',
      date: new Date(Date.now() - 86400000).toISOString(),
      participants: ['Alice Martin', 'Bob Durant', 'Charlie Dubois'],
      status: 'completed',
    },
    {
      id: 'meet-2',
      title: 'Revue Architecture Microservices',
      date: new Date(Date.now() - 172800000).toISOString(),
      participants: ['David Chen', 'Emma Wilson', 'Frank Lopez'],
      status: 'completed',
    },
    {
      id: 'meet-3',
      title: 'Point Client - Migration Cloud',
      date: new Date(Date.now() + 86400000).toISOString(),
      participants: ['Alice Martin', 'Client XYZ'],
      status: 'scheduled',
    },
  ]);

  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);
  const [crSections, setCRSections] = useState<string>(
    'Décisions\nActions\nRisques'
  );
  const [compteRendu, setCompteRendu] = useState<CompteRendu | null>(null);
  const [compiledDoc, setCompiledDoc] = useState<CompiledDoc | null>(null);
  const [exportFormat, setExportFormat] = useState<'pdf' | 'docx' | 'md'>('pdf');

  const [isGeneratingCR, setIsGeneratingCR] = useState(false);
  const [isCompiling, setIsCompiling] = useState(false);

  const handleGenerateCR = async () => {
    if (!selectedMeeting) return;

    setIsGeneratingCR(true);
    setCompteRendu(null);

    try {
      const sections = crSections.split('\n').filter((s) => s.trim());
      const response = await api.client.post('/api/docs/cr/build', {
        meeting_id: selectedMeeting.id,
        sections,
      });

      // Simuler un CR généré
      setCompteRendu({
        document_id: response.data.document_id || 'doc-123',
        meeting_id: selectedMeeting.id,
        trace_id: response.data.trace_id,
        sections: [
          {
            title: 'Décisions',
            content:
              '• Migration vers Azure planifiée pour Q2 2025\n• Budget validé: 150K€\n• Stack technique: Kubernetes + PostgreSQL',
          },
          {
            title: 'Actions',
            content:
              '• [Alice] Préparer POC migration (deadline: 15/02)\n• [Bob] Audit de sécurité (deadline: 20/02)\n• [Charlie] Formation équipe DevOps (deadline: 01/03)',
          },
          {
            title: 'Risques',
            content:
              '• Dépendances legacy non identifiées → Mitigation: Audit approfondi\n• Équipe sous-staffée → Mitigation: Recrutement en cours',
          },
        ],
      });
    } catch (error: any) {
      console.error('Error generating CR:', error);
      alert(error.response?.data?.detail || 'Erreur lors de la génération');
    } finally {
      setIsGeneratingCR(false);
    }
  };

  const handleCompileDoc = async () => {
    if (!compteRendu) return;

    setIsCompiling(true);
    try {
      const response = await api.client.post('/api/docs/compile', {
        doc_id: compteRendu.document_id,
        format: exportFormat,
      });

      setCompiledDoc({
        artifact_path: response.data.artifact_path,
        trace_id: response.data.trace_id,
      });
    } catch (error: any) {
      console.error('Error compiling doc:', error);
      alert(error.response?.data?.detail || 'Erreur lors de la compilation');
    } finally {
      setIsCompiling(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cr_generated':
        return 'bg-blue-100 text-blue-800';
      case 'scheduled':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Terminé';
      case 'cr_generated':
        return 'CR Généré';
      case 'scheduled':
        return 'Planifié';
      default:
        return status;
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center space-x-3">
          <FileText className="w-8 h-8 text-indigo-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Documentation & Comptes-Rendus
            </h1>
            <p className="text-sm text-gray-600">
              Génération automatique de CR et compilation de documents
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex">
        {/* Liste des meetings */}
        <div className="w-1/3 border-r bg-gray-50 overflow-y-auto p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Réunions</h2>
          <div className="space-y-3">
            {meetings.map((meeting) => (
              <div
                key={meeting.id}
                onClick={() => setSelectedMeeting(meeting)}
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedMeeting?.id === meeting.id
                    ? 'bg-indigo-50 border-indigo-200'
                    : 'bg-white border-gray-200 hover:border-indigo-200'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900 text-sm">
                    {meeting.title}
                  </h3>
                </div>

                <div className="flex items-center space-x-2 text-xs text-gray-600 mb-2">
                  <Calendar className="w-3 h-3" />
                  <span>
                    {new Date(meeting.date).toLocaleDateString('fr-FR')}
                  </span>
                </div>

                <div className="flex items-center space-x-2 text-xs text-gray-600 mb-2">
                  <Users className="w-3 h-3" />
                  <span>{meeting.participants.length} participants</span>
                </div>

                <span
                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(
                    meeting.status
                  )}`}
                >
                  {getStatusLabel(meeting.status)}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Zone principale */}
        <div className="flex-1 overflow-y-auto p-6">
          {!selectedMeeting && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg">Sélectionnez une réunion pour commencer</p>
              </div>
            </div>
          )}

          {selectedMeeting && (
            <div className="space-y-6">
              {/* Header meeting */}
              <div className="bg-white rounded-lg border p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {selectedMeeting.title}
                    </h2>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-2">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {new Date(selectedMeeting.date).toLocaleDateString(
                            'fr-FR',
                            {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                            }
                          )}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Users className="w-4 h-4" />
                        <span>{selectedMeeting.participants.length} participants</span>
                      </div>
                    </div>
                  </div>
                  <span
                    className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(
                      selectedMeeting.status
                    )}`}
                  >
                    {getStatusLabel(selectedMeeting.status)}
                  </span>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-700 mb-2 text-sm">
                    Participants:
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedMeeting.participants.map((participant, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                      >
                        {participant}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Génération CR */}
              <div className="bg-white rounded-lg border p-6 space-y-4">
                <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-indigo-600" />
                  <span>Générer le Compte-Rendu</span>
                </h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sections du CR (une par ligne)
                  </label>
                  <textarea
                    value={crSections}
                    onChange={(e) => setCRSections(e.target.value)}
                    placeholder="Décisions&#10;Actions&#10;Risques"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    rows={4}
                  />
                </div>

                <button
                  onClick={handleGenerateCR}
                  disabled={isGeneratingCR || selectedMeeting.status === 'scheduled'}
                  className="w-full bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                >
                  {isGeneratingCR ? (
                    <>
                      <Clock className="w-4 h-4 animate-spin" />
                      <span>Génération en cours...</span>
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4" />
                      <span>Générer le CR</span>
                    </>
                  )}
                </button>

                {selectedMeeting.status === 'scheduled' && (
                  <p className="text-sm text-orange-600">
                    Cette réunion n'a pas encore eu lieu
                  </p>
                )}
              </div>

              {/* CR généré */}
              {compteRendu && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 space-y-4">
                  <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span>Compte-Rendu généré</span>
                  </h3>

                  <div className="bg-white rounded-lg border p-4 space-y-4">
                    {compteRendu.sections.map((section, i) => (
                      <div key={i} className="border-b last:border-b-0 pb-4 last:pb-0">
                        <h4 className="font-bold text-gray-900 mb-2">
                          {section.title}
                        </h4>
                        <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                          {section.content}
                        </pre>
                      </div>
                    ))}
                  </div>

                  <div className="pt-4 border-t">
                    <h4 className="font-semibold text-gray-900 mb-3">
                      Exporter le document
                    </h4>

                    <div className="flex items-center space-x-4 mb-3">
                      <label className="text-sm font-medium text-gray-700">
                        Format:
                      </label>
                      <div className="flex space-x-2">
                        {(['pdf', 'docx', 'md'] as const).map((format) => (
                          <button
                            key={format}
                            onClick={() => setExportFormat(format)}
                            className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                              exportFormat === format
                                ? 'bg-indigo-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                          >
                            {format.toUpperCase()}
                          </button>
                        ))}
                      </div>
                    </div>

                    <button
                      onClick={handleCompileDoc}
                      disabled={isCompiling}
                      className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                    >
                      {isCompiling ? (
                        <>
                          <Clock className="w-4 h-4 animate-spin" />
                          <span>Compilation...</span>
                        </>
                      ) : (
                        <>
                          <Download className="w-4 h-4" />
                          <span>Compiler et télécharger</span>
                        </>
                      )}
                    </button>
                  </div>

                  {compiledDoc && (
                    <div className="bg-blue-50 border border-blue-200 rounded p-3">
                      <p className="text-sm text-blue-800">
                        <span className="font-semibold">Document généré:</span>{' '}
                        {compiledDoc.artifact_path}
                      </p>
                      <p className="text-xs text-blue-600 mt-1">
                        Trace ID: {compiledDoc.trace_id}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
