import { Navigate, Route, Routes } from 'react-router-dom';
import { AppShell } from './shared/layout/AppShell';
import { RegisterPage } from './features/auth/RegisterPage';
import { MfaSetupPage } from './features/auth/MfaSetupPage';
import { LoginPage } from './features/auth/LoginPage';
import { MfaVerifyPage } from './features/auth/MfaVerifyPage';
import { DashboardPage } from './features/dashboard/DashboardPage';

export function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/mfa-setup" element={<MfaSetupPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/mfa-verify" element={<MfaVerifyPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="*" element={<Navigate to="/register" replace />} />
      </Routes>
    </AppShell>
  );
}
