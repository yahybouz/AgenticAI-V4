import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { api } from '../services/api';
import { Bot, FileText, Activity, HardDrive, TrendingUp, Users, BarChart3, PieChart } from 'lucide-react';
import type { UserStats } from '../types';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart as RePieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [userStats, sysInfo] = await Promise.all([
        api.getUserStats(),
        api.getSystemInfo(),
      ]);
      setStats(userStats);
      setSystemInfo(sysInfo);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Mock data for charts (in production, this would come from API)
  const activityData = [
    { date: '25/10', queries: 12, agents: 3 },
    { date: '26/10', queries: 19, agents: 5 },
    { date: '27/10', queries: 15, agents: 4 },
    { date: '28/10', queries: 28, agents: 6 },
    { date: '29/10', queries: 22, agents: 5 },
    { date: '30/10', queries: 35, agents: 7 },
    { date: '31/10', queries: 42, agents: 8 },
  ];

  const agentUsageData = [
    { name: 'Chat', value: 35, color: '#3B82F6' },
    { name: 'RAG', value: 25, color: '#10B981' },
    { name: 'Coach', value: 15, color: '#F59E0B' },
    { name: 'Docs', value: 12, color: '#8B5CF6' },
    { name: 'Mail', value: 8, color: '#EF4444' },
    { name: 'Other', value: 5, color: '#6B7280' },
  ];

  const domainActivityData = [
    { domain: 'Chat', count: 145 },
    { domain: 'RAG', count: 98 },
    { domain: 'Docs', count: 76 },
    { domain: 'Coach', count: 54 },
    { domain: 'Mail', count: 32 },
    { domain: 'PM', count: 28 },
    { domain: 'Voice', count: 15 },
    { domain: 'WebIntel', count: 12 },
  ];

  const statCards = [
    {
      name: 'Agents',
      value: stats?.agents_count || 0,
      max: user?.max_agents || 0,
      icon: Bot,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-700',
    },
    {
      name: 'Documents',
      value: stats?.documents_count || 0,
      max: user?.max_documents || 0,
      icon: FileText,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-700',
    },
    {
      name: 'Stockage',
      value: `${stats?.storage_used_mb?.toFixed(1) || 0} MB`,
      max: `${user?.max_storage_mb || 0} MB`,
      icon: HardDrive,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-700',
    },
    {
      name: 'Requêtes',
      value: stats?.total_queries || 0,
      max: null,
      icon: Activity,
      color: 'bg-orange-500',
      bgColor: 'bg-orange-50',
      textColor: 'text-orange-700',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Bonjour, {user?.full_name || user?.username} ! 👋
        </h1>
        <p className="text-gray-600">
          Voici un aperçu de votre activité sur AgenticAI
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const percentage = stat.max
            ? typeof stat.value === 'number'
              ? (stat.value / stat.max) * 100
              : 0
            : null;

          return (
            <div key={stat.name} className="card">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl ${stat.bgColor}`}>
                  <stat.icon className={`w-6 h-6 ${stat.textColor}`} />
                </div>
                {percentage !== null && (
                  <span className="text-xs font-medium text-gray-500">
                    {percentage.toFixed(0)}%
                  </span>
                )}
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">
                  {stat.value}
                  {stat.max && (
                    <span className="text-sm font-normal text-gray-500">
                      {' '}
                      / {stat.max}
                    </span>
                  )}
                </p>
              </div>
              {percentage !== null && (
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${stat.color} transition-all duration-300`}
                      style={{ width: `${Math.min(percentage, 100)}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* System Info */}
      {systemInfo && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Bot className="w-5 h-5 text-primary-600" />
              Système d'Agents
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600">Agents totaux</span>
                <span className="font-semibold text-gray-900">
                  {systemInfo.agents?.total || 0}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600">Domaines disponibles</span>
                <span className="font-semibold text-gray-900">
                  {systemInfo.agents?.domains?.length || 0}
                </span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-600">Orchestrateur</span>
                <span className="font-semibold text-gray-900">
                  {systemInfo.orchestrator || 'N/A'}
                </span>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-primary-600" />
              Informations du Compte
            </h2>
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600">Rôle</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                  {user?.role}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600">Statut</span>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {user?.status}
                </span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-gray-100">
                <span className="text-sm text-gray-600">Modèle par défaut</span>
                <span className="font-semibold text-gray-900 text-sm">
                  {user?.default_model || 'qwen2.5:14b'}
                </span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-gray-600">Dernière connexion</span>
                <span className="font-semibold text-gray-900 text-sm">
                  {user?.last_login
                    ? new Date(user.last_login).toLocaleDateString('fr-FR')
                    : 'Jamais'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Over Time */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            Activité sur 7 jours
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={activityData}>
              <defs>
                <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis
                dataKey="date"
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}
              />
              <Area
                type="monotone"
                dataKey="queries"
                stroke="#3B82F6"
                fillOpacity={1}
                fill="url(#colorQueries)"
                name="Requêtes"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Agent Usage Distribution */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <PieChart className="w-5 h-5 text-primary-600" />
            Distribution des Agents
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <RePieChart>
              <Pie
                data={agentUsageData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {agentUsageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </RePieChart>
          </ResponsiveContainer>
        </div>

        {/* Domain Activity Bar Chart */}
        <div className="card lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary-600" />
            Activité par Domaine
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={domainActivityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis
                dataKey="domain"
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
              />
              <YAxis
                stroke="#6B7280"
                style={{ fontSize: '12px' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}
                cursor={{ fill: 'rgba(59, 130, 246, 0.1)' }}
              />
              <Bar
                dataKey="count"
                fill="#3B82F6"
                radius={[8, 8, 0, 0]}
                name="Utilisation"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Actions rapides</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a
            href="/agents"
            className="flex items-center gap-3 p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-primary-500 hover:bg-primary-50 transition-colors group"
          >
            <Bot className="w-8 h-8 text-gray-400 group-hover:text-primary-600" />
            <div>
              <p className="font-medium text-gray-900">Créer un agent</p>
              <p className="text-sm text-gray-500">Nouvel agent personnalisé</p>
            </div>
          </a>
          <a
            href="/documents"
            className="flex items-center gap-3 p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-primary-500 hover:bg-primary-50 transition-colors group"
          >
            <FileText className="w-8 h-8 text-gray-400 group-hover:text-primary-600" />
            <div>
              <p className="font-medium text-gray-900">Upload document</p>
              <p className="text-sm text-gray-500">Ajouter à la base</p>
            </div>
          </a>
          <a
            href="/chat"
            className="flex items-center gap-3 p-4 rounded-lg border-2 border-dashed border-gray-300 hover:border-primary-500 hover:bg-primary-50 transition-colors group"
          >
            <TrendingUp className="w-8 h-8 text-gray-400 group-hover:text-primary-600" />
            <div>
              <p className="font-medium text-gray-900">Démarrer un chat</p>
              <p className="text-sm text-gray-500">Interagir avec les agents</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
