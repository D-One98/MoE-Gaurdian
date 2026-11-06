import { useState } from 'react';
import { AppShell } from './components/layout/AppShell';
import type { NavRoute } from './components/layout/Sidebar';
import type { DemoRole } from './types/contracts';
import { INITIAL_MOCK_AUDIT_RESPONSE } from './services/mockAdapter';
import { PrismLogo } from './components/ui/PrismLogo';

export function App() {
  const [activeRoute, setActiveRoute] = useState<NavRoute>('dashboard');
  const [currentRole, setCurrentRole] = useState<DemoRole>('AUTHORISED_REVIEWER');
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);
  const audit = INITIAL_MOCK_AUDIT_RESPONSE;

  const triggerLoaderPreview = () => {
    setIsLoadingAudit(true);
    setTimeout(() => setIsLoadingAudit(false), 3000);
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
      <div className="bg-[#121215] border border-zinc-800/90 rounded-xl p-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <PrismLogo size="lg" animated={true} />
          <div>
            <h2 className="text-base font-semibold text-zinc-100">
              Step 4 Complete: Application Shell & Animated 4-Piece Prism Ready
            </h2>
            <p className="text-xs text-zinc-400 mt-1">
              Active Route: <span className="font-mono text-emerald-400">{activeRoute}</span> • Role:{' '}
              <span className="font-mono text-zinc-200">{currentRole}</span>
            </p>
          </div>
        </div>
        <button
          onClick={triggerLoaderPreview}
          className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-xs font-semibold text-white transition-colors cursor-pointer"
        >
          Test Full-Screen Audit Loader (3s)
        </button>
      </div>
    </AppShell>
  );
}

export default App;
