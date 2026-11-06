import { useState } from 'react';
import { AppShell } from './components/layout/AppShell';
import type { NavRoute } from './components/layout/Sidebar';
import type { DemoRole } from './types/contracts';
import { INITIAL_MOCK_AUDIT_RESPONSE } from './services/mockAdapter';
import { DashboardView } from './components/dashboard/DashboardView';

export function App() {
  const [activeRoute, setActiveRoute] = useState<NavRoute>('dashboard');
  const [currentRole, setCurrentRole] = useState<DemoRole>('AUTHORISED_REVIEWER');
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);
  const audit = INITIAL_MOCK_AUDIT_RESPONSE;

  const triggerLoaderPreview = () => {
    setIsLoadingAudit(true);
    setTimeout(() => setIsLoadingAudit(false), 2600);
  };

  return (
    <AppShell
      activeRoute={activeRoute}
      onSelectRoute={setActiveRoute}
      currentRole={currentRole}
      onChangeRole={setCurrentRole}
      overallStatus={audit.overall_status}
      auditId={audit.audit_id}
      orgId={audit.org_id}
      findingsCount={audit.findings.length}
      isStale={false}
      isMockMode={true}
      isLoadingAudit={isLoadingAudit}
      onTriggerDemoLoader={triggerLoaderPreview}
    >
      {activeRoute === 'dashboard' ? (
        <DashboardView
          audit={audit}
          isStale={false}
          onNavigate={setActiveRoute}
        />
      ) : (
        <div className="bg-[#121215] border border-zinc-800/90 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-zinc-100">
            Screen Under Construction: <span className="font-mono text-emerald-400">{activeRoute}</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Click "Dashboard" in the left sidebar to view the completed Dashboard screen.
          </p>
        </div>
      )}
    </AppShell>
  );
}

export default App;