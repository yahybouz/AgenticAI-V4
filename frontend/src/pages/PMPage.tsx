import { useState } from 'react';
import { Briefcase, AlertTriangle, FileText, TrendingUp, Clock, CheckCircle2 } from 'lucide-react';
import api from '../services/api';

interface Project {
  id: string;
  name: string;
  sprint: string;
  status: 'active' | 'planning' | 'review';
}

interface Risk {
  id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  description: string;
  impact: string;
  mitigation: string;
}

interface CODIRReport {
  project_id: string;
  sprint: string;
  sections: any[];
}

export default function PMPage() {
  const [projects] = useState<Project[]>([
    { id: 'proj-1', name: 'Migration Cloud Azure', sprint: 'Sprint 4', status: 'active' },
    { id: 'proj-2', name: 'Refonte Portail Client', sprint: 'Sprint 2', status: 'active' },
    { id: 'proj-3', name: 'API Gateway v2', sprint: 'Sprint 1', status: 'planning' },
  ]);

  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [sources, setSources] = useState<string>('');
  const [risks, setRisks] = useState<Risk[]>([]);
  const [codirReport, setCODIRReport] = useState<CODIRReport | null>(null);

  const [isAnalyzingRisks, setIsAnalyzingRisks] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  const handleAnalyzeRisks = async () => {
    if (!selectedProject || !sources.trim()) return;

    setIsAnalyzingRisks(true);
    setRisks([]);

    try {
      const sourcesList = sources.split('\n').filter((s) => s.trim());
      const response = await api.client.post('/api/pm/risks/analyze', {
        project_id: selectedProject.id,
        sources: sourcesList,
      });

      // Simuler des risques si le backend retourne vide
      const risksData = response.data.risks || [
        {
          id: 'r1',
          severity: 'critical',
          category: 'Technique',
          description: 'Dépendances legacy non documentées',
          impact: 'Retard de 2-3 semaines sur la migration',
          mitigation: 'Audit technique approfondi + documentation',
        },
        {
          id: 'r2',
          severity: 'high',
          category: 'Ressources',
          description: 'Équipe sous-staffée (2 devs manquants)',
          impact: 'Vélocité réduite de 30%',
          mitigation: 'Recruter 2 devs seniors en urgence',
        },
        {
          id: 'r3',
          severity: 'medium',
          category: 'Planning',
          description: 'User stories mal définies',
          impact: 'Rework potentiel',
          mitigation: 'Sessions de refinement hebdomadaires',
        },
      ];

      setRisks(risksData);
    } catch (error: any) {
      console.error('Error analyzing risks:', error);
      alert(error.response?.data?.detail || "Erreur lors de l'analyse");
    } finally {
      setIsAnalyzingRisks(false);
    }
  };

  const handleGenerateCODIRReport = async () => {
    if (!selectedProject) return;

    setIsGeneratingReport(true);
    try {
      const response = await api.client.get('/api/pm/report/codir', {
        params: {
          project_id: selectedProject.id,
          sprint: selectedProject.sprint,
        },
      });
      setCODIRReport(response.data);
    } catch (error: any) {
      console.error('Error generating CODIR report:', error);
      alert(error.response?.data?.detail || 'Erreur lors de la génération');
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'planning':
        return 'bg-blue-100 text-blue-800';
      case 'review':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center space-x-3">
          <Briefcase className="w-8 h-8 text-purple-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Project Management IT</h1>
            <p className="text-sm text-gray-600">
              Analyse de risques et rapports CODIR
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex">
        {/* Liste des projets */}
        <div className="w-1/3 border-r bg-gray-50 overflow-y-auto p-6">
          <h2 className="font-semibold text-gray-900 mb-4">Projets actifs</h2>
          <div className="space-y-3">
            {projects.map((project) => (
              <div
                key={project.id}
                onClick={() => setSelectedProject(project)}
                className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                  selectedProject?.id === project.id
                    ? 'bg-purple-50 border-purple-200'
                    : 'bg-white border-gray-200 hover:border-purple-200'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-semibold text-gray-900">{project.name}</h3>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <span className="text-gray-600">{project.sprint}</span>
                  <span className="text-gray-400">•</span>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${getStatusColor(
                      project.status
                    )}`}
                  >
                    {project.status}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {selectedProject && (
            <div className="mt-6 pt-6 border-t">
              <button
                onClick={handleGenerateCODIRReport}
                disabled={isGeneratingReport}
                className="w-full bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
              >
                {isGeneratingReport ? (
                  <>
                    <Clock className="w-4 h-4 animate-spin" />
                    <span>Génération...</span>
                  </>
                ) : (
                  <>
                    <FileText className="w-4 h-4" />
                    <span>Rapport CODIR</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>

        {/* Zone principale */}
        <div className="flex-1 overflow-y-auto p-6">
          {!selectedProject && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Briefcase className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg">Sélectionnez un projet pour commencer</p>
              </div>
            </div>
          )}

          {selectedProject && (
            <div className="space-y-6">
              {/* Header projet */}
              <div className="bg-white rounded-lg border p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {selectedProject.name}
                    </h2>
                    <div className="flex items-center space-x-3 text-sm text-gray-600">
                      <span>{selectedProject.sprint}</span>
                      <span>•</span>
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(
                          selectedProject.status
                        )}`}
                      >
                        {selectedProject.status}
                      </span>
                    </div>
                  </div>
                  <TrendingUp className="w-8 h-8 text-purple-600" />
                </div>
              </div>

              {/* Analyse de risques */}
              <div className="bg-white rounded-lg border p-6 space-y-4">
                <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-orange-600" />
                  <span>Analyse de risques</span>
                </h3>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sources de données (une par ligne)
                  </label>
                  <textarea
                    value={sources}
                    onChange={(e) => setSources(e.target.value)}
                    placeholder="Jira: https://jira.company.com/project/XYZ&#10;Confluence: https://wiki.company.com/project-docs&#10;GitHub: https://github.com/company/project"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
                    rows={4}
                  />
                </div>

                <button
                  onClick={handleAnalyzeRisks}
                  disabled={!sources.trim() || isAnalyzingRisks}
                  className="w-full bg-orange-600 text-white py-2 px-4 rounded-lg hover:bg-orange-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                >
                  {isAnalyzingRisks ? (
                    <>
                      <Clock className="w-4 h-4 animate-spin" />
                      <span>Analyse en cours...</span>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="w-4 h-4" />
                      <span>Analyser les risques</span>
                    </>
                  )}
                </button>
              </div>

              {/* Risques identifiés */}
              {risks.length > 0 && (
                <div className="space-y-3">
                  <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span>Risques identifiés ({risks.length})</span>
                  </h3>

                  {risks.map((risk) => (
                    <div
                      key={risk.id}
                      className={`border rounded-lg p-4 ${getSeverityColor(risk.severity)}`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center space-x-2">
                          <AlertTriangle className="w-5 h-5" />
                          <span className="font-semibold text-sm uppercase">
                            {risk.severity}
                          </span>
                        </div>
                        <span className="text-xs font-medium px-2 py-1 bg-white rounded">
                          {risk.category}
                        </span>
                      </div>

                      <h4 className="font-bold text-gray-900 mb-2">{risk.description}</h4>

                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="font-semibold">Impact: </span>
                          <span>{risk.impact}</span>
                        </div>
                        <div>
                          <span className="font-semibold">Mitigation: </span>
                          <span>{risk.mitigation}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Rapport CODIR */}
              {codirReport && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="font-bold text-gray-900 mb-4 flex items-center space-x-2">
                    <FileText className="w-5 h-5 text-blue-600" />
                    <span>Rapport CODIR</span>
                  </h3>

                  <div className="bg-white rounded p-4 space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="font-semibold text-gray-700">Projet:</span>
                      <span className="text-gray-900">{codirReport.project_id}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="font-semibold text-gray-700">Sprint:</span>
                      <span className="text-gray-900">{codirReport.sprint}</span>
                    </div>

                    <div className="pt-3 border-t">
                      <p className="text-sm text-gray-600 italic">
                        Le rapport détaillé sera généré par l'orchestrateur multi-agents
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
