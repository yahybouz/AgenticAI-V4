import { useState } from 'react';
import { Heart, TrendingUp, Calendar, Award, BarChart3, Plus, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

interface Activity {
  type: string;
  duration: number;
  intensity: 'low' | 'moderate' | 'high';
  notes?: string;
  timestamp: string;
}

interface Report {
  period: string;
  total_activities: number;
  total_duration: number;
  average_intensity: string;
  recommendations: string[];
  insights: string;
}

export default function CoachPage() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [report, setReport] = useState<Report | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  const [newActivity, setNewActivity] = useState({
    type: 'exercise',
    duration: 30,
    intensity: 'moderate' as 'low' | 'moderate' | 'high',
    notes: '',
  });

  const logActivity = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await api.client.post('/api/coach/log', {
        ...newActivity,
        timestamp: new Date().toISOString(),
      });

      const activity: Activity = {
        ...newActivity,
        timestamp: new Date().toISOString(),
      };

      setActivities((prev) => [activity, ...prev]);
      setShowAddModal(false);
      setNewActivity({
        type: 'exercise',
        duration: 30,
        intensity: 'moderate',
        notes: '',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur lors de l'enregistrement");
      console.error('Log activity error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const generateReport = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.client.get('/api/coach/report', {
        params: { period: '7d' },
      });

      setReport({
        period: '7 derniers jours',
        total_activities: response.data.total_activities || 0,
        total_duration: response.data.total_duration || 0,
        average_intensity: response.data.average_intensity || 'moderate',
        recommendations: response.data.recommendations || [],
        insights: response.data.insights || 'Continuez comme ça !',
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la génération du rapport');
      console.error('Generate report error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'moderate':
        return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-700 border-green-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Coach Bien-être</h1>
          <p className="text-gray-600">
            Suivez votre activité et améliorez votre bien-être
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Nouvelle activité
        </button>
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

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Calendar className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="text-sm font-medium text-gray-600">Activités</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">{activities.length}</p>
          <p className="text-xs text-gray-500 mt-1">Cette semaine</p>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-100 rounded-lg">
              <TrendingUp className="w-5 h-5 text-green-600" />
            </div>
            <h3 className="text-sm font-medium text-gray-600">Durée totale</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {activities.reduce((sum, a) => sum + a.duration, 0)} min
          </p>
          <p className="text-xs text-gray-500 mt-1">En mouvement</p>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Heart className="w-5 h-5 text-purple-600" />
            </div>
            <h3 className="text-sm font-medium text-gray-600">Bien-être</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">Excellent</p>
          <p className="text-xs text-gray-500 mt-1">État général</p>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-orange-100 rounded-lg">
              <Award className="w-5 h-5 text-orange-600" />
            </div>
            <h3 className="text-sm font-medium text-gray-600">Objectif</h3>
          </div>
          <p className="text-2xl font-bold text-gray-900">75%</p>
          <p className="text-xs text-gray-500 mt-1">Atteint</p>
        </div>
      </div>

      {/* Report */}
      {report && (
        <div className="card border-2 border-primary-200 bg-primary-50">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-primary-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5" />
              Rapport - {report.period}
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="p-3 bg-white rounded-lg">
              <p className="text-xs text-gray-600">Activités</p>
              <p className="text-xl font-bold text-gray-900">{report.total_activities}</p>
            </div>
            <div className="p-3 bg-white rounded-lg">
              <p className="text-xs text-gray-600">Durée totale</p>
              <p className="text-xl font-bold text-gray-900">{report.total_duration} min</p>
            </div>
            <div className="p-3 bg-white rounded-lg">
              <p className="text-xs text-gray-600">Intensité moyenne</p>
              <p className="text-xl font-bold text-gray-900 capitalize">
                {report.average_intensity}
              </p>
            </div>
          </div>

          <div className="p-4 bg-white rounded-lg mb-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Insights:</p>
            <p className="text-sm text-gray-600">{report.insights}</p>
          </div>

          {report.recommendations.length > 0 && (
            <div>
              <p className="text-sm font-medium text-primary-800 mb-2">Recommandations:</p>
              <ul className="space-y-1">
                {report.recommendations.map((rec, index) => (
                  <li key={index} className="text-sm text-primary-700 flex items-start gap-2">
                    <span className="text-primary-500">•</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-3">
        <button
          onClick={generateReport}
          disabled={isLoading || activities.length === 0}
          className="btn btn-secondary flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
              Génération...
            </>
          ) : (
            <>
              <BarChart3 className="w-4 h-4" />
              Générer un rapport
            </>
          )}
        </button>
      </div>

      {/* Activities List */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Historique des activités</h2>

        {activities.length === 0 ? (
          <div className="text-center py-12">
            <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucune activité enregistrée
            </h3>
            <p className="text-gray-600 mb-4">
              Commencez à suivre vos activités pour améliorer votre bien-être
            </p>
            <button onClick={() => setShowAddModal(true)} className="btn btn-primary">
              <Plus className="w-4 h-4 mr-2 inline" />
              Ajouter une activité
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {activities.map((activity, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {activity.type}
                    </span>
                    <span
                      className={`text-xs px-2 py-1 rounded border ${getIntensityColor(
                        activity.intensity
                      )}`}
                    >
                      {activity.intensity}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(activity.timestamp).toLocaleString('fr-FR')}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>{activity.duration} minutes</span>
                  {activity.notes && <span className="text-xs italic">{activity.notes}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Add Activity Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-xl font-semibold mb-4">Nouvelle activité</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Type d'activité
                </label>
                <select
                  value={newActivity.type}
                  onChange={(e) => setNewActivity({ ...newActivity, type: e.target.value })}
                  className="input"
                >
                  <option value="exercise">Exercice</option>
                  <option value="meditation">Méditation</option>
                  <option value="yoga">Yoga</option>
                  <option value="running">Course</option>
                  <option value="walking">Marche</option>
                  <option value="other">Autre</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Durée (minutes)
                </label>
                <input
                  type="number"
                  value={newActivity.duration}
                  onChange={(e) =>
                    setNewActivity({ ...newActivity, duration: parseInt(e.target.value) || 0 })
                  }
                  className="input"
                  min="1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Intensité</label>
                <select
                  value={newActivity.intensity}
                  onChange={(e) =>
                    setNewActivity({
                      ...newActivity,
                      intensity: e.target.value as 'low' | 'moderate' | 'high',
                    })
                  }
                  className="input"
                >
                  <option value="low">Faible</option>
                  <option value="moderate">Modérée</option>
                  <option value="high">Élevée</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Notes (optionnel)
                </label>
                <textarea
                  value={newActivity.notes}
                  onChange={(e) => setNewActivity({ ...newActivity, notes: e.target.value })}
                  className="input"
                  rows={3}
                  placeholder="Commentaires..."
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn btn-secondary flex-1"
                >
                  Annuler
                </button>
                <button
                  onClick={logActivity}
                  disabled={isLoading}
                  className="btn btn-primary flex-1"
                >
                  {isLoading ? 'Enregistrement...' : 'Enregistrer'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
