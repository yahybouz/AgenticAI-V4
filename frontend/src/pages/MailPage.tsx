import { useState } from 'react';
import { Mail, Send, Inbox, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import api from '../services/api';

interface MailThread {
  id: string;
  account_id: string;
  subject: string;
  from: string;
  preview: string;
  timestamp: string;
}

interface MailSummary {
  summary: string;
  risks: string[];
  next_steps: string[];
}

interface MailDraft {
  draft: string;
  requires_hitl: boolean;
}

export default function MailPage() {
  const [threads, setThreads] = useState<MailThread[]>([
    {
      id: 'thread-1',
      account_id: 'acc-1',
      subject: 'Urgent: Validation projet X',
      from: 'chef.projet@example.com',
      preview: 'Bonjour, nous avons besoin de votre validation urgente...',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
    },
    {
      id: 'thread-2',
      account_id: 'acc-1',
      subject: 'Budget Q1 2025',
      from: 'finance@example.com',
      preview: 'Voici le récapitulatif budgétaire pour le premier trimestre...',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
    },
  ]);

  const [selectedThread, setSelectedThread] = useState<MailThread | null>(null);
  const [summary, setSummary] = useState<MailSummary | null>(null);
  const [draft, setDraft] = useState<MailDraft | null>(null);
  const [replyInstructions, setReplyInstructions] = useState('');

  const [isLoadingSummary, setIsLoadingSummary] = useState(false);
  const [isGeneratingDraft, setIsGeneratingDraft] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const handleSummarize = async (thread: MailThread) => {
    setIsLoadingSummary(true);
    setSummary(null);
    setDraft(null);
    setSelectedThread(thread);

    try {
      const response = await api.client.post('/api/mail/summarize', {
        account_id: thread.account_id,
        thread_id: thread.id,
      });
      setSummary(response.data);
    } catch (error: any) {
      console.error('Error summarizing mail:', error);
      alert(error.response?.data?.detail || 'Erreur lors du résumé');
    } finally {
      setIsLoadingSummary(false);
    }
  };

  const handleGenerateDraft = async () => {
    if (!selectedThread || !replyInstructions.trim()) return;

    setIsGeneratingDraft(true);
    try {
      const response = await api.client.post('/api/mail/reply', {
        account_id: selectedThread.account_id,
        thread_id: selectedThread.id,
        instructions: replyInstructions.trim(),
      });
      setDraft(response.data);
    } catch (error: any) {
      console.error('Error generating draft:', error);
      alert(error.response?.data?.detail || 'Erreur lors de la génération');
    } finally {
      setIsGeneratingDraft(false);
    }
  };

  const handleSendDraft = async () => {
    if (!draft) return;

    if (!confirm('Êtes-vous sûr de vouloir envoyer cet email ?')) return;

    setIsSending(true);
    try {
      await api.client.post('/api/mail/send', {
        draft_id: 'draft-temp-id',
        approve: true,
      });
      alert('Email envoyé avec succès !');
      setDraft(null);
      setReplyInstructions('');
      setSummary(null);
      setSelectedThread(null);
    } catch (error: any) {
      console.error('Error sending mail:', error);
      alert(error.response?.data?.detail || "Erreur lors de l'envoi");
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center space-x-3">
          <Mail className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Mail Assistant</h1>
            <p className="text-sm text-gray-600">
              Résumé intelligent et génération de réponses
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex">
        {/* Liste des threads */}
        <div className="w-1/3 border-r bg-gray-50 overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center space-x-2 mb-4">
              <Inbox className="w-5 h-5 text-gray-600" />
              <h2 className="font-semibold text-gray-900">Boîte de réception</h2>
              <span className="ml-auto bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded">
                {threads.length}
              </span>
            </div>

            <div className="space-y-2">
              {threads.map((thread) => (
                <div
                  key={thread.id}
                  onClick={() => handleSummarize(thread)}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedThread?.id === thread.id
                      ? 'bg-blue-50 border-blue-200'
                      : 'bg-white border-gray-200 hover:border-blue-200'
                  }`}
                >
                  <div className="flex items-start justify-between mb-1">
                    <span className="font-medium text-sm text-gray-900 truncate">
                      {thread.from}
                    </span>
                    <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
                      {new Date(thread.timestamp).toLocaleTimeString('fr-FR', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                  <h3 className="font-semibold text-sm text-gray-900 mb-1 truncate">
                    {thread.subject}
                  </h3>
                  <p className="text-xs text-gray-600 truncate">{thread.preview}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Zone de détails et actions */}
        <div className="flex-1 overflow-y-auto p-6">
          {!selectedThread && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center text-gray-500">
                <Mail className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <p className="text-lg">Sélectionnez un email pour commencer</p>
              </div>
            </div>
          )}

          {selectedThread && (
            <div className="space-y-6">
              {/* Header */}
              <div className="bg-white rounded-lg border p-4">
                <h2 className="text-xl font-bold text-gray-900 mb-2">
                  {selectedThread.subject}
                </h2>
                <div className="flex items-center text-sm text-gray-600 space-x-4">
                  <span>De: {selectedThread.from}</span>
                  <span>•</span>
                  <span>
                    {new Date(selectedThread.timestamp).toLocaleString('fr-FR')}
                  </span>
                </div>
              </div>

              {/* Résumé */}
              {isLoadingSummary && (
                <div className="bg-white rounded-lg border p-6 text-center">
                  <Clock className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-2" />
                  <p className="text-gray-600">Analyse en cours...</p>
                </div>
              )}

              {summary && (
                <div className="bg-white rounded-lg border p-6 space-y-4">
                  <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <span>Résumé</span>
                  </h3>
                  <p className="text-gray-700">{summary.summary}</p>

                  {summary.risks.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 flex items-center space-x-2 mb-2">
                        <AlertTriangle className="w-4 h-4 text-orange-600" />
                        <span>Risques identifiés</span>
                      </h4>
                      <ul className="space-y-1">
                        {summary.risks.map((risk, i) => (
                          <li key={i} className="text-sm text-orange-700 flex items-start">
                            <span className="mr-2">•</span>
                            <span>{risk}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {summary.next_steps.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">
                        Prochaines étapes
                      </h4>
                      <ul className="space-y-1">
                        {summary.next_steps.map((step, i) => (
                          <li key={i} className="text-sm text-gray-700 flex items-start">
                            <span className="mr-2">{i + 1}.</span>
                            <span>{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Génération de réponse */}
              {summary && (
                <div className="bg-white rounded-lg border p-6 space-y-4">
                  <h3 className="font-bold text-gray-900 flex items-center space-x-2">
                    <Send className="w-5 h-5 text-blue-600" />
                    <span>Générer une réponse</span>
                  </h3>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Instructions pour la réponse
                    </label>
                    <textarea
                      value={replyInstructions}
                      onChange={(e) => setReplyInstructions(e.target.value)}
                      placeholder="Ex: Répondre de manière positive en demandant plus de détails sur le budget..."
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      rows={3}
                    />
                  </div>

                  <button
                    onClick={handleGenerateDraft}
                    disabled={!replyInstructions.trim() || isGeneratingDraft}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                  >
                    {isGeneratingDraft ? (
                      <>
                        <Clock className="w-4 h-4 animate-spin" />
                        <span>Génération...</span>
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4" />
                        <span>Générer le brouillon</span>
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Brouillon généré */}
              {draft && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6 space-y-4">
                  <h3 className="font-bold text-gray-900">Brouillon généré</h3>
                  <div className="bg-white rounded border p-4">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                      {draft.draft}
                    </pre>
                  </div>

                  {draft.requires_hitl && (
                    <div className="flex items-center space-x-2 text-sm text-orange-700">
                      <AlertTriangle className="w-4 h-4" />
                      <span>Validation humaine requise avant envoi</span>
                    </div>
                  )}

                  <div className="flex space-x-3">
                    <button
                      onClick={handleSendDraft}
                      disabled={isSending}
                      className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                    >
                      {isSending ? (
                        <>
                          <Clock className="w-4 h-4 animate-spin" />
                          <span>Envoi...</span>
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4" />
                          <span>Envoyer</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => setDraft(null)}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Annuler
                    </button>
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
