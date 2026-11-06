import React from 'react';
import type { Severity } from '../../types/contracts';
import { SeverityBadge } from '../ui/Badge';
import { BookOpen, ShieldCheck, Database, Palette } from 'lucide-react';

// Static workspace constitution reference (Clearly labelled for Round 2 UI display)
const CONSTITUTION_RULES: Array<{
    rule_id: string;
    category: string;
    title: string;
    description: string;
    mandatory_flag: boolean;
    severity: Severity;
}> = [
        {
            rule_id: 'RULE-TERM-01',
            category: 'APPROVED_TERMINOLOGY',
            title: 'Official Brand Casing ("Inkloom AI")',
            description:
                'Always write "Inkloom AI" with a space and uppercase AI. Never write domain-style "Inkloom.ai" in narrative copy.',
            mandatory_flag: true,
            severity: 'MEDIUM',
        },
        {
            rule_id: 'RULE-BAN-02',
            category: 'BANNED_TERM',
            title: 'Prohibited Unqualified Superlatives & Guarantees',
            description:
                'Banned phrases include "100% guaranteed", "zero-risk", and unverified "#1 globally ranked" superlatives.',
            mandatory_flag: true,
            severity: 'CRITICAL',
        },
        {
            rule_id: 'RULE-DISC-03',
            category: 'MANDATORY_DISCLAIMER',
            title: 'Laboratory Battery Testing Condition',
            description:
                'Any mention of battery life metrics must state "up to" and "under specified laboratory testing conditions".',
            mandatory_flag: true,
            severity: 'HIGH',
        },
    ];

const APPROVED_FACTS = [
    {
        fact_id: 'FACT-BAT-02',
        document_name: 'Product_Specifications_v2.pdf',
        verified_page_or_row: 4,
        canonical_excerpt:
            'Up to 12 hours under specified laboratory testing conditions.',
        required_conditions:
            'Must include qualifier "up to" and testing condition "under specified laboratory testing conditions".',
    },
    {
        fact_id: 'FACT-ARCH-01',
        document_name: 'Brand_Guidelines_2026.pdf',
        verified_page_or_row: 2,
        canonical_excerpt:
            'VERITY MoE combines deterministic RuleGuard checks with evidence-grounded ClaimGuard verification.',
        required_conditions: 'Describe deterministic checks as reproducible for configured rules.',
    },
];

const BRAND_PALETTE = [
    { name: 'Carbon Zinc 950', hex: '#09090B', role: 'Primary Application Canvas' },
    { name: 'Elevated Surface', hex: '#121215', role: 'Card & Inspector Background' },
    { name: 'Verity Emerald', hex: '#10B981', role: 'Primary Brand & Verified Accent' },
    { name: 'Escalation Amber', hex: '#F59E0B', role: 'Partial Claim / Review Warning' },
];

export const BrandConstitutionView: React.FC = () => {
    return (
        <div className="space-y-6">
            {/* Header Banner */}
            <div className="bg-[#121215] border border-zinc-800/90 rounded-xl p-5 flex items-center justify-between">
                <div className="space-y-1">
                    <div className="flex items-center gap-2 text-xs font-mono text-emerald-400">
                        <BookOpen className="w-4 h-4" />
                        <span>Brand Constitution Registry • v1.0.0</span>
                    </div>
                    <h2 className="text-base font-semibold text-zinc-100 tracking-tight">
                        Approved Terminology, Banned Terms, Facts Vault & Brand Palette
                    </h2>
                </div>
            </div>

            {/* 1. Terminology, Banned Terms & Mandatory Disclaimers */}
            <div className="bg-[#121215] border border-zinc-800/90 rounded-xl overflow-hidden">
                <div className="px-5 py-3.5 bg-zinc-900/60 border-b border-zinc-800/80 flex items-center gap-2 text-xs font-semibold text-zinc-200">
                    <ShieldCheck className="w-4 h-4 text-emerald-400" />
                    <span>Configured Terminology, Banned Terms & Mandatory Disclaimers</span>
                </div>
                <div className="divide-y divide-zinc-800/70">
                    {CONSTITUTION_RULES.map((rule) => (
                        <div
                            key={rule.rule_id}
                            className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                        >
                            <div className="space-y-1">
                                <div className="flex flex-wrap items-center gap-2 font-mono text-xs">
                                    <span className="font-bold text-zinc-100">{rule.rule_id}</span>
                                    <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-300 text-[10px]">
                                        {rule.category}
                                    </span>
                                    {rule.mandatory_flag && (
                                        <span className="px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-800/70 text-emerald-300 text-[10px]">
                                            mandatory_flag: true
                                        </span>
                                    )}
                                </div>
                                <div className="text-sm font-semibold text-zinc-200">
                                    {rule.title}
                                </div>
                                <p className="text-xs text-zinc-400">{rule.description}</p>
                            </div>
                            <SeverityBadge severity={rule.severity} />
                        </div>
                    ))}
                </div>
            </div>

            {/* 2. Approved Facts Vault & Required Conditions */}
            <div className="bg-[#121215] border border-zinc-800/90 rounded-xl overflow-hidden">
                <div className="px-5 py-3.5 bg-zinc-900/60 border-b border-zinc-800/80 flex items-center gap-2 text-xs font-semibold text-zinc-200">
                    <Database className="w-4 h-4 text-amber-400" />
                    <span>Approved Facts Vault & Required Qualifiers</span>
                </div>
                <div className="divide-y divide-zinc-800/70">
                    {APPROVED_FACTS.map((fact) => (
                        <div key={fact.fact_id} className="p-4 space-y-2">
                            <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
                                <span className="font-bold text-emerald-400">{fact.fact_id}</span>
                                <span className="text-zinc-400">
                                    Source: <strong className="text-zinc-200">{fact.document_name}</strong> (Page/Row{' '}
                                    {fact.verified_page_or_row})
                                </span>
                            </div>
                            <blockquote className="p-3 rounded bg-zinc-950 border border-zinc-800 text-xs text-zinc-200 font-mono">
                                "{fact.canonical_excerpt}"
                            </blockquote>
                            <div className="text-xs text-amber-300/90 font-mono">
                                Required Condition: {fact.required_conditions}
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 3. Approved Brand Colour Palette */}
            <div className="bg-[#121215] border border-zinc-800/90 rounded-xl p-5 space-y-4">
                <div className="flex items-center gap-2 text-xs font-semibold text-zinc-200">
                    <Palette className="w-4 h-4 text-sky-400" />
                    <span>Approved Brand Hex Palette (CIEDE2000 ΔE Reference)</span>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {BRAND_PALETTE.map((swatch) => (
                        <div
                            key={swatch.hex}
                            className="p-3.5 rounded-lg bg-zinc-950 border border-zinc-800 space-y-2"
                        >
                            <div
                                className="h-12 rounded-md border border-zinc-700"
                                style={{ backgroundColor: swatch.hex }}
                            />
                            <div className="text-xs font-semibold text-zinc-100">
                                {swatch.name}
                            </div>
                            <div className="text-xs font-mono text-emerald-400">
                                {swatch.hex}
                            </div>
                            <div className="text-[11px] text-zinc-500">{swatch.role}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};