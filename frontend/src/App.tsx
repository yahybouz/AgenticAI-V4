import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import AgentsPage from './pages/AgentsPage';
import DocumentsPage from './pages/DocumentsPage';
import ChatPage from './pages/ChatPage';
import MonitoringPage from './pages/MonitoringPage';
import VoicePage from './pages/VoicePage';
import WebIntelPage from './pages/WebIntelPage';
import CoachPage from './pages/CoachPage';

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
}

function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Private routes */}
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <Layout>
                <DashboardPage />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/agents"
          element={
            <PrivateRoute>
              <Layout>
                <AgentsPage />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/documents"
          element={
            <PrivateRoute>
              <Layout>
                <DocumentsPage />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/chat"
          element={
            <PrivateRoute>
              <Layout>
                <ChatPage />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/monitoring"
          element={
            <PrivateRoute>
              <Layout>
                <MonitoringPage />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/voice"
          element={
            <PrivateRoute>
              <Layout>
                <VoicePage />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/webintel"
          element={
            <PrivateRoute>
              <Layout>
                <WebIntelPage />
              </Layout>
            </PrivateRoute>
          }
        />
        <Route
          path="/coach"
          element={
            <PrivateRoute>
              <Layout>
                <CoachPage />
              </Layout>
            </PrivateRoute>
          }
        />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="*" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
