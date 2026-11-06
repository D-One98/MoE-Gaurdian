import { useState, useMemo } from 'react';
import { AppShell } from './components/layout/AppShell';
import type { NavRoute } from './components/layout/Sidebar';
import type {
  AuditResponse,
  ContentBlock,
  DemoRole,
} from './types/contracts';
import {
  INITIAL_CONTENT_BLOCKS,
  INITIAL_MOCK_AUDIT_RESPONSE,
  createMockAudit,
} from './services/mockAdapter';
import { DashboardView } from './components/dashboard/DashboardView';
import { BlockEditorView } from './components/editor/BlockEditorView';

// Deterministic revision hash helper for stale-finding detection (Section 4D)
function computeEditorRevisionHash(blocks: ContentBlock[], altText: string): string {
  const serialized =
    blocks.map((b) => `${b.document_block_id}:${b.text}`).join('||') +
    `||alt:${altText.trim()}`;
  let h1 = 0xdeadbeef ^ serialized.length;
  let h2 = 0x41c6ce57 ^ serialized.length;
  for (let i = 0, ch; i < serialized.length; i++) {
    ch = serialized.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 =
    Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^
    Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 =
    Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^
    Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  const hex =
    (h2 >>> 0).toString(16).padStart(8, '0') +
    (h1 >>> 0).toString(16).padStart(8, '0');
  return `sha256:${hex}e55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08`;
}

export function App() {
  const [activeRoute, setActiveRoute] = useState<NavRoute>('dashboard');
  const [currentRole, setCurrentRole] = useState<DemoRole>('CREATOR');
  const [isLoadingAudit, setIsLoadingAudit] = useState(false);

  // Canonical Editor State (Source of Truth for Draft Editing)
  const [campaignId, setCampaignId] = useState<string>(
    INITIAL_MOCK_AUDIT_RESPONSE.campaign_id
  );
  const [blocks, setBlocks] = useState<ContentBlock[]>(INITIAL_CONTENT_BLOCKS);
  const [altText, setAltText] = useState<string>(
    'Enterprise product banner showing compliance dashboard on dark carbon background'
  );
  const [nextBlockSeq, setNextBlockSeq] = useState<number>(4);

  // Current live revision hash of the editor
  const currentRevisionHash = useMemo(
    () => computeEditorRevisionHash(blocks, altText),
    [blocks, altText]
  );

  // Active Audit Response State (Initialised in sync with initial blocks)
  const [audit, setAudit] = useState<AuditResponse>(() => ({
    ...INITIAL_MOCK_AUDIT_RESPONSE,
    document_revision_hash: computeEditorRevisionHash(
      INITIAL_CONTENT_BLOCKS,
      'Enterprise product banner showing compliance dashboard on dark carbon background'
    ),
  }));

  // Stale-finding detection: True whenever editor content differs from last audited hash
  const isStale = currentRevisionHash !== audit.document_revision_hash;

  // Update a block's text while strictly preserving its document_block_id
  const handleUpdateBlockText = (blockId: string, newText: string) => {
    setBlocks((prev) =>
      prev.map((b) =>
        b.document_block_id === blockId ? { ...b, text: newText } : b
      )
    );
  };

  // Add a new canonical block with a stable ID
  const handleAddBlock = () => {
    const formattedNum = String(nextBlockSeq).padStart(2, '0');
    const newBlock: ContentBlock = {
      document_block_id: `blk-paragraph-${formattedNum}`,
      text: '',
    };
    setBlocks((prev) => [...prev, newBlock]);
    setNextBlockSeq((n) => n + 1);
  };

  // Remove a block by ID
  const handleRemoveBlock = (blockId: string) => {
    setBlocks((prev) => prev.filter((b) => b.document_block_id !== blockId));
  };

  // Reset blocks to initial launch announcement sample
  const handleResetDefaultBlocks = () => {
    const defaultAlt =
      'Enterprise product banner showing compliance dashboard on dark carbon background';
    setBlocks(INITIAL_CONTENT_BLOCKS);
    setAltText(defaultAlt);
    const syncedHash = computeEditorRevisionHash(INITIAL_CONTENT_BLOCKS, defaultAlt);
    setAudit({
      ...INITIAL_MOCK_AUDIT_RESPONSE,
      document_revision_hash: syncedHash,
    });
  };

  // Submit Draft to VERITY MoE Audit (Shows Animated 4-Piece Prism Loader)
  const handleRunAudit = () => {
    setIsLoadingAudit(true);
    setTimeout(() => {
      const updatedAudit = createMockAudit(
        {
          campaign_id: campaignId,
          submitted_by_role: currentRole,
          blocks,
          alt_text: altText || null,
        },
        currentRevisionHash
      );
      setAudit(updatedAudit);
      setIsLoadingAudit(false);
    }, 1800);
  };

  const triggerLoaderPreview = () => {
    setIsLoadingAudit(true);
    setTimeout(() => setIsLoadingAudit(false), 2400);
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
      isStale={isStale}
      isMockMode={true}
      isLoadingAudit={isLoadingAudit}
      onTriggerDemoLoader={triggerLoaderPreview}
    >
      {activeRoute === 'dashboard' && (
        <DashboardView
          audit={audit}
          isStale={isStale}
          onNavigate={setActiveRoute}
        />
      )}

      {activeRoute === 'editor' && (
        <BlockEditorView
          campaignId={campaignId}
          onChangeCampaignId={setCampaignId}
          blocks={blocks}
          onUpdateBlockText={handleUpdateBlockText}
          onAddBlock={handleAddBlock}
          onRemoveBlock={handleRemoveBlock}
          onResetDefaultBlocks={handleResetDefaultBlocks}
          altText={altText}
          onChangeAltText={setAltText}
          currentRole={currentRole}
          currentRevisionHash={currentRevisionHash}
          lastAuditedHash={audit.document_revision_hash}
          isStale={isStale}
          isLoadingAudit={isLoadingAudit}
          findings={audit.findings}
          onRunAudit={handleRunAudit}
          onNavigate={setActiveRoute}
        />
      )}

      {activeRoute !== 'dashboard' && activeRoute !== 'editor' && (
        <div className="bg-[#121215] border border-zinc-800/90 rounded-xl p-6">
          <h2 className="text-sm font-semibold text-zinc-100">
            Next Up on Checklist:{' '}
            <span className="font-mono text-emerald-400">{activeRoute}</span>
          </h2>
          <p className="text-xs text-zinc-400 mt-1">
            Dashboard and Content Editor are now live! Select "Dashboard" or "Content Editor" in the left sidebar.
          </p>
        </div>
      )}
    </AppShell>
  );
}

export default App;