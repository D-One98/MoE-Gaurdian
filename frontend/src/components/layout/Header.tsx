import React from 'react';
import type { AuditStatus, DemoRole } from '../../types/contracts';
import { AuditStatusBadge } from '../ui/Badge';
import type { NavRoute } from './Sidebar';
import { Search, Bell, User, AlertCircle } from 'lucide-react';

interface HeaderProps {
    activeRoute: NavRoute;
    currentRole: DemoRole;
    onChangeRole: (role: DemoRole) => void;
    overallStatus: AuditStatus;
    auditId: string;
    isStale: boolean;
    onTriggerDemoLoader?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
    currentRole,
    onChangeRole,
    overallStatus,
    auditId,
    isStale,
    onTriggerDemoLoader,
}) => {
    return (
        <header className="h-16 bg-[#09090B] border-b border-zinc-800/80 px-6 flex items-center justify-between gap-4 shrink-0">
            {/* Left: Campaigns > AUD-2026-0042 Breadcrumb */}
            <div className="flex items-center gap-2 text-xs font-medium">
                <span className="text-zinc-400">Campaigns</span>
                <span className="text-zinc-600">&gt;</span>
                <span className="text-zinc-100 font-mono font-semibold">{auditId}</span>

                {isStale && (
                    <span className="ml-2 inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-amber-950/80 border border-amber-800/70 text-amber-300 text-[11px] font-mono">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                        STALE_AFTER_EDIT
                    </span>
                )}
            </div>

            {/* Center: Top Command Bar */}
            <div className="hidden md:flex items-center gap-2 bg-[#121215] border border-zinc-800 rounded-lg px-3 py-1.5 w-80 text-xs text-zinc-400">
                <Search className="w-3.5 h-3.5 text-zinc-500" />
                <input
                    type="text"
                    readOnly
                    onClick={onTriggerDemoLoader}
                    placeholder="Search findings or click to preview loader..."
                    className="bg-transparent w-full text-xs text-zinc-300 placeholder:text-zinc-500 focus:outline-none cursor-pointer"
                />
            </div>

            {/* Right: Status Badge + Role Switcher Pill + Icons */}
            <div className="flex items-center gap-3">
                <AuditStatusBadge status={overallStatus} />

                {/* Interactive DemoRole Selector styled like the Emerald Pill in your screenshot */}
                <div className="flex items-center bg-emerald-950/60 border border-emerald-800/70 rounded px-2.5 py-0.5">
                    <select
                        aria-label="Current user role"
                        value={currentRole}
                        onChange={(e) => onChangeRole(e.target.value as DemoRole)}
                        className="bg-transparent text-[11px] font-mono font-semibold text-emerald-300 focus:outline-none cursor-pointer"
                    >
                        <option value="CREATOR" className="bg-zinc-900 text-zinc-100">
                            CREATOR
                        </option>
                        <option value="BRAND_MANAGER" className="bg-zinc-900 text-zinc-100">
                            BRAND_MANAGER
                        </option>
                        <option value="AUTHORISED_REVIEWER" className="bg-zinc-900 text-zinc-100">
                            AUTHORISED_REVIEWER
                        </option>
                        <option value="WORKSPACE_ADMIN" className="bg-zinc-900 text-zinc-100">
                            WORKSPACE_ADMIN
                        </option>
                    </select>
                </div>

                <button
                    type="button"
                    onClick={onTriggerDemoLoader}
                    title="Preview Animated Prism Loading State"
                    className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/60 transition-colors"
                >
                    <Bell className="w-4 h-4" />
                </button>
                <div className="w-7 h-7 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-zinc-300">
                    <User className="w-3.5 h-3.5" />
                </div>
            </div>
        </header>
    );
};