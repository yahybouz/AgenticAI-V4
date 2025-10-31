import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Bookmark, Play, Pause, Trash2, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

interface VoiceSession {
  id: string;
  transcript: string;
  duration: number;
  timestamp: string;
}

interface VoiceBookmark {
  id: string;
  transcript: string;
  timestamp: string;
  tags: string[];
}

export default function VoicePage() {
  const [isRecording, setIsRecording] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [sessions, setSessions] = useState<VoiceSession[]>([]);
  const [bookmarks, setBookmarks] = useState<VoiceBookmark[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      const audioChunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        await processAudio(audioBlob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
      setError(null);
      setRecordingTime(0);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      setError("Impossible d'accéder au microphone. Vérifiez les permissions.");
      console.error('Error accessing microphone:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  };

  const processAudio = async (audioBlob: Blob) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.wav');

      const response = await api.client.post('/api/voice/session', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const newSession: VoiceSession = {
        id: Date.now().toString(),
        transcript: response.data.transcript || 'Transcription en cours...',
        duration: recordingTime,
        timestamp: new Date().toISOString(),
      };

      setSessions((prev) => [newSession, ...prev]);
      setCurrentTranscript(response.data.transcript || '');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de la transcription');
      console.error('Error processing audio:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const createBookmark = async (transcript: string) => {
    try {
      await api.client.post('/api/voice/bookmark', {
        transcript,
        tags: ['vocal'],
      });

      const newBookmark: VoiceBookmark = {
        id: Date.now().toString(),
        transcript,
        timestamp: new Date().toISOString(),
        tags: ['vocal'],
      };

      setBookmarks((prev) => [newBookmark, ...prev]);
    } catch (err) {
      console.error('Error creating bookmark:', err);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Voice Assistant</h1>
        <p className="text-gray-600">Enregistrez et transcrivez vos notes vocales</p>
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

      {/* Recording Control */}
      <div className="card">
        <div className="text-center py-12">
          <div className="relative inline-block mb-6">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              disabled={isLoading}
              className={`w-24 h-24 rounded-full flex items-center justify-center transition-all transform hover:scale-105 ${
                isRecording
                  ? 'bg-red-500 hover:bg-red-600 animate-pulse'
                  : 'bg-primary-600 hover:bg-primary-700'
              } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isRecording ? (
                <MicOff className="w-10 h-10 text-white" />
              ) : (
                <Mic className="w-10 h-10 text-white" />
              )}
            </button>
            {isRecording && (
              <div className="absolute inset-0 rounded-full border-4 border-red-500 animate-ping"></div>
            )}
          </div>

          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {isRecording ? 'Enregistrement en cours...' : 'Appuyez pour enregistrer'}
          </h3>

          {isRecording && (
            <div className="text-3xl font-mono font-bold text-red-600 mb-2">
              {formatTime(recordingTime)}
            </div>
          )}

          <p className="text-sm text-gray-600">
            {isRecording
              ? 'Cliquez à nouveau pour arrêter'
              : 'Votre audio sera transcrit automatiquement'}
          </p>

          {isLoading && (
            <div className="mt-4">
              <div className="inline-flex items-center gap-2 text-sm text-gray-600">
                <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
                Transcription en cours...
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Current Transcript */}
      {currentTranscript && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Dernière transcription</h2>
            <button
              onClick={() => createBookmark(currentTranscript)}
              className="btn btn-secondary flex items-center gap-2"
            >
              <Bookmark className="w-4 h-4" />
              Sauvegarder
            </button>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <p className="text-gray-900">{currentTranscript}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sessions History */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Historique des sessions</h2>

          {sessions.length === 0 ? (
            <div className="text-center py-8">
              <Mic className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-sm text-gray-500">Aucune session enregistrée</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {sessions.map((session) => (
                <div key={session.id} className="p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-medium text-gray-500">
                      {new Date(session.timestamp).toLocaleString('fr-FR')}
                    </span>
                    <span className="text-xs text-gray-500">{formatTime(session.duration)}</span>
                  </div>
                  <p className="text-sm text-gray-700 line-clamp-2">{session.transcript}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Bookmarks */}
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Bookmark className="w-5 h-5 text-primary-600" />
            Bookmarks sauvegardés
          </h2>

          {bookmarks.length === 0 ? (
            <div className="text-center py-8">
              <Bookmark className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-sm text-gray-500">Aucun bookmark</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {bookmarks.map((bookmark) => (
                <div key={bookmark.id} className="p-3 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex gap-1">
                      {bookmark.tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 text-xs bg-primary-100 text-primary-700 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(bookmark.timestamp).toLocaleDateString('fr-FR')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{bookmark.transcript}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
