import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './pages/Layout.jsx';
import SelectPage from './pages/SelectPage.jsx';
import BattlePage from './pages/BattlePage.jsx';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<SelectPage />} />
        <Route path="/pokemon/:levelId" element={<BattlePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
