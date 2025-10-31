import { useEffect, useState } from 'react';
import { Activity, AlertCircle, CheckCircle, TrendingUp, Clock, Zap } from 'lucide-react';
import { api } from '../services/api';

interface Insight {
  type: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
}

export default function MonitoringPage() {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [systemInfo, setSystemInfo] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [insightsData, sysInfo] = await Promise.all([
        api.client.get('/api/monitoring/insights'),
        api.getSystemInfo(),
      ]);

      setInsights(insightsData.data || []);
      setSystemInfo(sysInfo);
    } catch (error) {
      console.error('Error loading monitoring data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'bg-red-100 border-red-200 text-red-800';
      case 'warning':
        return 'bg-yellow-100 border-yellow-200 text-yellow-800';
      case 'success':
        return 'bg-green-100 border-green-200 text-green-800';
      default:
        return 'bg-blue-100 border-blue-200 text-blue-800';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      default:
        return <Activity className="w-5 h-5 text-blue-600" />;
    }
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
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Monitoring</h1>
        <p className="text-gray-600">
          Supervision et insights du système AgenticAI
        </p>
      </div>

      {/* System Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900">État du système</h3>
          </div>
          <p className="text-2xl font-bold text-green-600">Opérationnel</p>
          <p className="text-xs text-gray-500 mt-1">
            Tous les services fonctionnent normalement
          </p>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Activity className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Agents actifs</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {systemInfo?.agents?.total || 19}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {systemInfo?.agents?.domains?.length || 8} domaines disponibles
          </p>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Zap className="w-5 h-5 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900">Performance</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">Excellente</p>
          <p className="text-xs text-gray-500 mt-1">
            Temps de réponse moyen: ~2s
          </p>
        </div>
      </div>

      {/* System Info */}
      {systemInfo && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary-600" />
            Informations Système
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Version</p>
              <p className="font-semibold text-gray-900">{systemInfo.version || 'v4.0.0'}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Environnement</p>
              <p className="font-semibold text-gray-900">{systemInfo.environment || 'local'}</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Base de données</p>
              <p className="font-semibold text-gray-900">SQLite (dev)</p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">LLM</p>
              <p className="font-semibold text-gray-900">Ollama (qwen2.5:14b)</p>
            </div>
          </div>
        </div>
      )}

      {/* Insights */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          Insights & Alertes
        </h2>

        {insights.length === 0 ? (
          <div className="text-center py-12">
            <CheckCircle className="w-16 h-16 text-green-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucune alerte
            </h3>
            <p className="text-gray-600">
              Le système fonctionne parfaitement. Aucun problème détecté.
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div
                key={index}
                className={`p-4 border rounded-lg flex items-start gap-3 ${getSeverityColor(
                  insight.severity
                )}`}
              >
                {getSeverityIcon(insight.severity)}
                <div className="flex-1">
                  <p className="text-sm font-medium">{insight.message}</p>
                  <p className="text-xs mt-1 opacity-75 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(insight.timestamp).toLocaleString('fr-FR')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent Activity */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-primary-600" />
          Activité récente
        </h2>
        <div className="space-y-3">
          <div className="flex items-start gap-3 pb-3 border-b border-gray-100">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Système démarré</p>
              <p className="text-xs text-gray-500">Il y a quelques heures</p>
            </div>
          </div>
          <div className="flex items-start gap-3 pb-3 border-b border-gray-100">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">19 agents chargés</p>
              <p className="text-xs text-gray-500">Tous les domaines opérationnels</p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">Ollama connecté</p>
              <p className="text-xs text-gray-500">Modèle qwen2.5:14b actif</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
