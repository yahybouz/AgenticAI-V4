import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Bot, Plus, Trash2, Activity, AlertCircle, X } from 'lucide-react';
import type { Agent, CreateAgentRequest } from '../types';

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setIsLoading(true);
      const data = await api.getAgents();
      setAgents(data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors du chargement des agents');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAgent = async (id: string) => {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cet agent ?')) return;

    try {
      await api.deleteAgent(id);
      setAgents(agents.filter((a) => a.id !== id));
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erreur lors de la suppression');
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Agents</h1>
          <p className="text-gray-600">
            Gérez vos agents personnalisés et utilisez les agents système
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          Créer un agent
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div key={agent.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                    agent.is_active ? 'bg-primary-100' : 'bg-gray-100'
                  }`}
                >
                  <Bot
                    className={`w-6 h-6 ${
                      agent.is_active ? 'text-primary-700' : 'text-gray-400'
                    }`}
                  />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{agent.name}</h3>
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                    {agent.domain}
                  </span>
                </div>
              </div>
              {agent.id.startsWith('custom::') && (
                <button
                  onClick={() => handleDeleteAgent(agent.id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="Supprimer"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>

            <p className="text-sm text-gray-600 mb-4 line-clamp-2">
              {agent.description}
            </p>

            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">
                  {agent.skills.length} compétence{agent.skills.length > 1 ? 's' : ''}
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {agent.skills.slice(0, 3).map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-blue-50 text-blue-700"
                  >
                    {skill}
                  </span>
                ))}
                {agent.skills.length > 3 && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-50 text-gray-600">
                    +{agent.skills.length - 3}
                  </span>
                )}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>
                  {agent.is_active ? (
                    <span className="text-green-600 font-medium">● Actif</span>
                  ) : (
                    <span className="text-gray-400">● Inactif</span>
                  )}
                </span>
                <span>
                  {new Date(agent.created_at).toLocaleDateString('fr-FR')}
                </span>
              </div>
            </div>
          </div>
        ))}

        {agents.length === 0 && (
          <div className="col-span-full card text-center py-12">
            <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Aucun agent
            </h3>
            <p className="text-gray-600 mb-4">
              Commencez par créer votre premier agent personnalisé
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="btn btn-primary mx-auto"
            >
              <Plus className="w-5 h-5 mr-2 inline" />
              Créer un agent
            </button>
          </div>
        )}
      </div>

      {/* Create Agent Modal (simplified for now) */}
      {showCreateModal && (
        <CreateAgentModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            loadAgents();
          }}
        />
      )}
    </div>
  );
}

interface CreateAgentModalProps {
  onClose: () => void;
  onSuccess: () => void;
}

function CreateAgentModal({ onClose, onSuccess }: CreateAgentModalProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [skillInput, setSkillInput] = useState('');
  const [formData, setFormData] = useState<CreateAgentRequest>({
    name: '',
    domain: 'RAG',
    skills: [],
    description: '',
  });

  const addSkill = () => {
    const trimmed = skillInput.trim();
    if (trimmed && !formData.skills.includes(trimmed)) {
      setFormData({ ...formData, skills: [...formData.skills, trimmed] });
      setSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData({
      ...formData,
      skills: formData.skills.filter((s) => s !== skill),
    });
  };

  const handleSkillKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill();
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await api.createAgent(formData);
      onSuccess();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Erreur lors de la création');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-semibold mb-4">Créer un nouvel agent</h2>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom de l'agent *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              required
              placeholder="Mon agent personnalisé"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Domaine *
            </label>
            <select
              value={formData.domain}
              onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
              className="input"
            >
              <option value="RAG">RAG - Recherche documentaire</option>
              <option value="CHAT">CHAT - Conversations générales</option>
              <option value="VOICE">VOICE - Traitement vocal</option>
              <option value="MAIL">MAIL - Gestion d'emails</option>
              <option value="COACH">COACH - Coaching et bien-être</option>
              <option value="DOCS">DOCS - Génération de documentation</option>
              <option value="PM">PM - Project Management</option>
              <option value="WEBINTEL">WEBINTEL - Intelligence web</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Compétences
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyDown={handleSkillKeyDown}
                className="input flex-1"
                placeholder="Ex: recherche, analyse, synthèse..."
              />
              <button
                type="button"
                onClick={addSkill}
                className="btn btn-secondary"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
            {formData.skills.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.skills.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-700"
                  >
                    {skill}
                    <button
                      type="button"
                      onClick={() => removeSkill(skill)}
                      className="hover:bg-blue-200 rounded-full p-0.5"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              className="input"
              rows={3}
              required
              placeholder="Description de l'agent..."
            />
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary flex-1"
            >
              Annuler
            </button>
            <button type="submit" disabled={isLoading} className="btn btn-primary flex-1">
              {isLoading ? 'Création...' : 'Créer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
