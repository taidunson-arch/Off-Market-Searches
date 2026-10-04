import { useState, useMemo, useCallback } from 'react';
import { affordableHousingData, getUniqueCounties, getUniqueYears, getUniqueFundingSources } from './data/affordableHousingData';
import { commercialLoanMaturities, getUniquePropertyTypes, getMaturityYears, getUniqueLoanTypes } from './data/commercialLoanData';
import type { AffordableHousingProperty } from './data/affordableHousingData';
import type { CommercialLoanMaturity } from './data/commercialLoanData';
import { generateExcelReport } from './utils/excelExport';

type TabType = 'dashboard' | 'affordable' | 'commercial' | 'combined' | 'analytics';
type LeadStatus = 'New' | 'Researching' | 'Contacted' | 'Under Review' | 'Passed';

function formatCurrency(value: number): string {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
  return `$${(value / 1000).toFixed(0)}K`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function formatDays(days: number): string {
  if (days < 0) return `${Math.abs(days)}d ago`;
  if (days < 365) return `${days}d`;
  return `${Math.floor(days / 365)}y ${Math.floor((days % 365) / 30)}m`;
}

function RiskBadge({ level }: { level: string }) {
  const colors: Record<string, string> = {
    High: 'bg-red-100 text-red-800 border-red-200',
    Critical: 'bg-red-200 text-red-900 border-red-300',
    Medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    Moderate: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    Low: 'bg-green-100 text-green-800 border-green-200',
  };
  return <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${colors[level] || 'bg-gray-100 text-gray-800'}`}>{level}</span>;
}

function FundingBadge({ source }: { source: string }) {
  const colors: Record<string, string> = { LIHTC: 'bg-blue-100 text-blue-800', HUD: 'bg-purple-100 text-purple-800', USDA: 'bg-emerald-100 text-emerald-800', 'LIHTC/HUD': 'bg-indigo-100 text-indigo-800', Other: 'bg-gray-100 text-gray-800' };
  const key = Object.keys(colors).find(k => source.includes(k)) || 'Other';
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[key] || colors.Other}`}>{source}</span>;
}

function StatusBadge({ status }: { status: LeadStatus }) {
  const colors: Record<LeadStatus, string> = {
    'New': 'bg-sky-100 text-sky-800',
    'Researching': 'bg-violet-100 text-violet-800',
    'Contacted': 'bg-amber-100 text-amber-800',
    'Under Review': 'bg-orange-100 text-orange-800',
    'Passed': 'bg-gray-100 text-gray-600',
  };
  return <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[status]}`}>{status}</span>;
}

function ScoreBar({ score }: { score: number }) {
  const color = score >= 75 ? 'bg-red-500' : score >= 55 ? 'bg-orange-500' : score >= 35 ? 'bg-yellow-500' : 'bg-green-500';
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 bg-gray-200 rounded-full h-2">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${score}%` }}></div>
      </div>
      <span className="text-xs font-medium text-gray-700">{score}</span>
    </div>
  );
}

// Detail Modal
function PropertyModal({ property, type, onClose, onUpdateStatus, onUpdateNotes }: {
  property: AffordableHousingProperty | CommercialLoanMaturity;
  type: 'affordable' | 'commercial';
  onClose: () => void;
  onUpdateStatus: (id: string, status: LeadStatus) => void;
  onUpdateNotes: (id: string, notes: string) => void;
}) {
  const [notes, setNotes] = useState(property.notes);
  const [status, setStatus] = useState<LeadStatus>(property.leadStatus);

  const handleSave = () => {
    onUpdateStatus(property.id, status);
    onUpdateNotes(property.id, notes);
    onClose();
  };

  const isAffordable = type === 'affordable';
  const ah = isAffordable ? (property as AffordableHousingProperty) : null;
  const cl = !isAffordable ? (property as CommercialLoanMaturity) : null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{property.propertyName}</h2>
              <p className="text-sm text-gray-500 mt-1">{property.address}, {property.city}, {property.county}</p>
            </div>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 p-1">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        </div>

        <div className="p-6 space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">Score</p>
              <p className="text-lg font-bold text-gray-900">{property.investmentScore}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">{isAffordable ? 'Expiration' : 'Maturity'}</p>
              <p className="text-sm font-bold text-gray-900">{formatDate(isAffordable ? ah!.expirationDate : cl!.loanMaturityDate)}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">Days Left</p>
              <p className={`text-lg font-bold ${(isAffordable ? ah!.daysUntilExpiration : cl!.daysUntilMaturity) < 365 ? 'text-red-600' : 'text-gray-900'}`}>{formatDays(isAffordable ? ah!.daysUntilExpiration : cl!.daysUntilMaturity)}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <p className="text-xs text-gray-500">Risk</p>
              <RiskBadge level={isAffordable ? ah!.riskLevel : cl!.distressLevel} />
            </div>
          </div>

          {/* Property Details */}
          {isAffordable && ah && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Property Details</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-gray-500">Total Units:</span> <span className="font-medium">{ah.totalUnits}</span></div>
                <div><span className="text-gray-500">Restricted Units:</span> <span className="font-medium">{ah.restrictedUnits}</span></div>
                <div><span className="text-gray-500">Funding Source:</span> <FundingBadge source={ah.fundingSource} /></div>
                <div><span className="text-gray-500">OHCS Funded:</span> <span className="font-medium">{ah.ohcsFunded ? 'Yes' : 'No'}</span></div>
                <div><span className="text-gray-500">HUD:</span> <span className="font-medium">{ah.hud ? 'Yes' : 'No'}</span></div>
                <div><span className="text-gray-500">USDA:</span> <span className="font-medium">{ah.usda ? 'Yes' : 'No'}</span></div>
                <div className="col-span-2"><span className="text-gray-500">Preservation Status:</span> <span className="font-medium">{ah.preservationStatus || 'None'}</span></div>
              </div>

              {/* AMI Breakdown */}
              {(ah.ami30 > 0 || ah.ami40 > 0 || ah.ami50 > 0 || ah.ami60 > 0 || ah.ami70 > 0 || ah.ami80 > 0) && (
                <div className="mt-4">
                  <h4 className="text-xs font-semibold text-gray-600 mb-2">AMI Level Breakdown</h4>
                  <div className="flex gap-1 h-6 rounded overflow-hidden">
                    {ah.ami30 > 0 && <div className="bg-red-400 flex items-center justify-center text-xs text-white" style={{ width: `${(ah.ami30 / ah.totalUnits) * 100}%` }} title={`${ah.ami30} units at 30% AMI`}>{ah.ami30}</div>}
                    {ah.ami40 > 0 && <div className="bg-orange-400 flex items-center justify-center text-xs text-white" style={{ width: `${(ah.ami40 / ah.totalUnits) * 100}%` }} title={`${ah.ami40} units at 40% AMI`}>{ah.ami40}</div>}
                    {ah.ami50 > 0 && <div className="bg-yellow-400 flex items-center justify-center text-xs text-white" style={{ width: `${(ah.ami50 / ah.totalUnits) * 100}%` }} title={`${ah.ami50} units at 50% AMI`}>{ah.ami50}</div>}
                    {ah.ami60 > 0 && <div className="bg-green-400 flex items-center justify-center text-xs text-white" style={{ width: `${(ah.ami60 / ah.totalUnits) * 100}%` }} title={`${ah.ami60} units at 60% AMI`}>{ah.ami60}</div>}
                    {ah.ami70 > 0 && <div className="bg-teal-400 flex items-center justify-center text-xs text-white" style={{ width: `${(ah.ami70 / ah.totalUnits) * 100}%` }} title={`${ah.ami70} units at 70% AMI`}>{ah.ami70}</div>}
                    {ah.ami80 > 0 && <div className="bg-blue-400 flex items-center justify-center text-xs text-white" style={{ width: `${(ah.ami80 / ah.totalUnits) * 100}%` }} title={`${ah.ami80} units at 80% AMI`}>{ah.ami80}</div>}
                  </div>
                  <div className="flex gap-3 mt-1 flex-wrap">
                    <span className="text-xs text-gray-500 flex items-center gap-1"><span className="w-2 h-2 bg-red-400 rounded"></span>30%</span>
                    <span className="text-xs text-gray-500 flex items-center gap-1"><span className="w-2 h-2 bg-orange-400 rounded"></span>40%</span>
                    <span className="text-xs text-gray-500 flex items-center gap-1"><span className="w-2 h-2 bg-yellow-400 rounded"></span>50%</span>
                    <span className="text-xs text-gray-500 flex items-center gap-1"><span className="w-2 h-2 bg-green-400 rounded"></span>60%</span>
                    <span className="text-xs text-gray-500 flex items-center gap-1"><span className="w-2 h-2 bg-teal-400 rounded"></span>70%</span>
                    <span className="text-xs text-gray-500 flex items-center gap-1"><span className="w-2 h-2 bg-blue-400 rounded"></span>80%</span>
                  </div>
                </div>
              )}

              {/* Preservation Strategy */}
              <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
                <h4 className="text-xs font-semibold text-blue-800 mb-1">📋 Preservation Strategy</h4>
                <p className="text-xs text-blue-700">
                  {ah.preservationStatus.includes('ROFR') ? 'Right of First Refusal active — coordinate with local jurisdiction before approaching owner.' :
                   ah.preservationStatus.includes('Government Owned') ? 'Government-owned — explore intergovernmental transfer or long-term ground lease.' :
                   ah.hud ? 'HUD contract expiring — contact HUD field office for contract extension options or mark-to-market.' :
                   ah.usda ? 'USDA Rural Development — explore Section 515 loan maturity options and RHS preservation tools.' :
                   'LIHTC expiration — evaluate extended use agreement, qualified contract, or nonprofit acquisition.'}
                </p>
              </div>
            </div>
          )}

          {!isAffordable && cl && (
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-3">Loan & Property Details</h3>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div><span className="text-gray-500">Loan Amount:</span> <span className="font-medium">{formatCurrency(cl.loanAmount)}</span></div>
                <div><span className="text-gray-500">Loan Type:</span> <span className="font-medium">{cl.loanType}</span></div>
                <div><span className="text-gray-500">Lender:</span> <span className="font-medium">{cl.lender}</span></div>
                <div><span className="text-gray-500">Interest Rate:</span> <span className="font-medium">{cl.interestRate}%</span></div>
                <div><span className="text-gray-500">Property Type:</span> <span className="font-medium">{cl.propertyType}</span></div>
                <div><span className="text-gray-500">Year Built:</span> <span className="font-medium">{cl.yearBuilt}</span></div>
                <div><span className="text-gray-500">Sq Ft:</span> <span className="font-medium">{cl.sqft.toLocaleString()}</span></div>
                <div><span className="text-gray-500">Units:</span> <span className="font-medium">{cl.units || 'N/A'}</span></div>
                <div><span className="text-gray-500">LTV:</span> <span className={`font-medium ${cl.ltv >= 80 ? 'text-red-600' : cl.ltv >= 70 ? 'text-yellow-600' : 'text-green-600'}`}>{cl.ltv}%</span></div>
                <div><span className="text-gray-500">DSCR:</span> <span className={`font-medium ${cl.dscr < 1.0 ? 'text-red-600' : cl.dscr < 1.2 ? 'text-yellow-600' : 'text-green-600'}`}>{cl.dscr.toFixed(2)}</span></div>
                <div><span className="text-gray-500">Occupancy:</span> <span className={`font-medium ${cl.occupancyRate < 70 ? 'text-red-600' : cl.occupancyRate < 85 ? 'text-yellow-600' : 'text-green-600'}`}>{cl.occupancyRate}%</span></div>
                <div><span className="text-gray-500">Cap Rate:</span> <span className="font-medium">{cl.capRate}%</span></div>
                <div><span className="text-gray-500">NOI:</span> <span className="font-medium">{formatCurrency(cl.noi)}</span></div>
                <div><span className="text-gray-500">Origination:</span> <span className="font-medium">{formatDate(cl.originalLoanDate)}</span></div>
              </div>

              {cl.conversionPotential !== 'N/A' && (
                <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-3">
                  <h4 className="text-xs font-semibold text-amber-800 mb-1">🔄 Conversion Potential</h4>
                  <p className="text-xs text-amber-700">{cl.conversionPotential} — distressed asset with repositioning upside. Evaluate highest-and-best-use scenario.</p>
                </div>
              )}
            </div>
          )}

          {/* Lead Management */}
          <div className="border-t pt-4">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Lead Management</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">Status</label>
                <select value={status} onChange={e => setStatus(e.target.value as LeadStatus)} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                  <option value="New">New</option>
                  <option value="Researching">Researching</option>
                  <option value="Contacted">Contacted</option>
                  <option value="Under Review">Under Review</option>
                  <option value="Passed">Passed</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 block mb-1">Notes</label>
                <textarea value={notes} onChange={e => setNotes(e.target.value)} rows={3} placeholder="Add research notes, contact info, deal terms..." className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm resize-none" />
              </div>
              <button onClick={handleSave} className="w-full bg-blue-600 text-white py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Download Hero Banner
function DownloadBanner() {
  const [exportMode, setExportMode] = useState<'all' | 'filtered'>('all');

  return (
    <div className="bg-gradient-to-r from-green-600 to-emerald-700 rounded-xl shadow-lg p-5 mb-6 text-white">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold flex items-center gap-2">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            Export to Excel
          </h2>
          <p className="text-sm text-green-100 mt-1">
            Download a multi-sheet workbook with all data, analytics, and a data dictionary.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg overflow-hidden border border-green-400">
            <button
              onClick={() => setExportMode('all')}
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${exportMode === 'all' ? 'bg-white text-green-700' : 'bg-green-500 text-white hover:bg-green-400'}`}
            >
              All Data
            </button>
            <button
              onClick={() => setExportMode('filtered')}
              className={`px-3 py-1.5 text-xs font-medium transition-colors ${exportMode === 'filtered' ? 'bg-white text-green-700' : 'bg-green-500 text-white hover:bg-green-400'}`}
            >
              Filtered
            </button>
          </div>
          <button
            onClick={() => {
              const fileName = generateExcelReport();
              alert(`✅ Report downloaded: ${fileName}\n\n📊 6 Sheets included:\n1. Executive Summary\n2. Affordable Housing (${affordableHousingData.length} properties)\n3. Commercial Loans (${commercialLoanMaturities.length} loans)\n4. Combined Leads\n5. Analytics & Market Intelligence\n6. Data Dictionary`);
            }}
            className="px-5 py-2.5 bg-white text-green-700 rounded-lg text-sm font-bold hover:bg-green-50 transition-colors shadow-md flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
            Download .xlsx
          </button>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-4 text-xs text-green-200">
        <span>📋 {affordableHousingData.length} affordable housing properties</span>
        <span>🏢 {commercialLoanMaturities.length} commercial loans</span>
        <span>📈 {affordableHousingData.reduce((s, p) => s + p.totalUnits, 0).toLocaleString()} total units tracked</span>
        <span>💰 {formatCurrency(commercialLoanMaturities.reduce((s, p) => s + p.loanAmount, 0))} in loan value</span>
      </div>
    </div>
  );
}

// Dashboard
function Dashboard({ onNavigate }: { onNavigate: (tab: TabType) => void }) {
  const totalAffordableUnits = affordableHousingData.reduce((s, p) => s + p.totalUnits, 0);
  const totalCommercialValue = commercialLoanMaturities.reduce((s, p) => s + p.loanAmount, 0);
  const highRiskAH = affordableHousingData.filter(p => p.riskLevel === 'High').length;
  const criticalCL = commercialLoanMaturities.filter(p => p.distressLevel === 'Critical').length;
  const expiring12mo = affordableHousingData.filter(p => p.daysUntilExpiration <= 365 && p.daysUntilExpiration > 0).length;
  const maturing12mo = commercialLoanMaturities.filter(p => p.daysUntilMaturity <= 365 && p.daysUntilMaturity > 0).length;

  const yearBreakdown = useMemo(() => {
    const b: Record<number, { count: number; units: number }> = {};
    affordableHousingData.forEach(p => { if (!b[p.expirationYear]) b[p.expirationYear] = { count: 0, units: 0 }; b[p.expirationYear].count++; b[p.expirationYear].units += p.totalUnits; });
    return b;
  }, []);

  const countyBreakdown = useMemo(() => {
    const b: Record<string, number> = {};
    affordableHousingData.forEach(p => { b[p.county] = (b[p.county] || 0) + p.totalUnits; });
    return Object.entries(b).sort((a, b) => b[1] - a[1]).slice(0, 10);
  }, []);

  const typeBreakdown = useMemo(() => {
    const b: Record<string, { count: number; value: number }> = {};
    commercialLoanMaturities.forEach(p => { if (!b[p.propertyType]) b[p.propertyType] = { count: 0, value: 0 }; b[p.propertyType].count++; b[p.propertyType].value += p.loanAmount; });
    return Object.entries(b).sort((a, b) => b[1].value - a[1].value);
  }, []);

  const fundingBreakdown = useMemo(() => {
    const b: Record<string, { count: number; units: number }> = {};
    affordableHousingData.forEach(p => { if (!b[p.fundingSource]) b[p.fundingSource] = { count: 0, units: 0 }; b[p.fundingSource].count++; b[p.fundingSource].units += p.totalUnits; });
    return Object.entries(b).sort((a, b) => b[1].units - a[1].units);
  }, []);

  // Top opportunities
  const topOpportunities = useMemo(() => {
    const ah = affordableHousingData.filter(p => p.investmentScore >= 70).sort((a, b) => b.investmentScore - a.investmentScore).slice(0, 5);
    const cl = commercialLoanMaturities.filter(p => p.investmentScore >= 70).sort((a, b) => b.investmentScore - a.investmentScore).slice(0, 5);
    return { ah, cl };
  }, []);

  return (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Affordable Units Tracked</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{totalAffordableUnits.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center text-2xl">🏠</div>
          </div>
          <p className="text-xs text-gray-400 mt-2">{affordableHousingData.length} properties • 2025-2035</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Commercial Loans Tracked</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{formatCurrency(totalCommercialValue)}</p>
            </div>
            <div className="w-12 h-12 bg-orange-50 rounded-lg flex items-center justify-center text-2xl">🏢</div>
          </div>
          <p className="text-xs text-gray-400 mt-2">{commercialLoanMaturities.length} loans • 2026-2031</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">High-Priority Leads</p>
              <p className="text-3xl font-bold text-red-600 mt-1">{highRiskAH + criticalCL}</p>
            </div>
            <div className="w-12 h-12 bg-red-50 rounded-lg flex items-center justify-center text-2xl">⚠️</div>
          </div>
          <p className="text-xs text-gray-400 mt-2">{highRiskAH} AH high-risk + {criticalCL} comm. critical</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500 font-medium">Expiring/Maturing (12mo)</p>
              <p className="text-3xl font-bold text-amber-600 mt-1">{expiring12mo + maturing12mo}</p>
            </div>
            <div className="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center text-2xl">📅</div>
          </div>
          <p className="text-xs text-gray-400 mt-2">{expiring12mo} AH + {maturing12mo} commercial</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Affordable Housing Expiration Timeline</h3>
          <div className="space-y-2">
            {Object.entries(yearBreakdown).sort().map(([year, data]) => (
              <div key={year} className="flex items-center gap-3">
                <span className="text-sm font-medium text-gray-600 w-12">{year}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-6 relative overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full flex items-center justify-end pr-2" style={{ width: `${Math.max((data.units / 2000) * 100, 8)}%` }}>
                    <span className="text-xs text-white font-medium">{data.units} units</span>
                  </div>
                </div>
                <span className="text-xs text-gray-500 w-16 text-right">{data.count} props</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Commercial Loans by Property Type</h3>
          <div className="space-y-2">
            {typeBreakdown.map(([type, data]) => (
              <div key={type} className="flex items-center gap-3">
                <span className="text-sm font-medium text-gray-600 w-32 truncate" title={type}>{type}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-6 relative overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-orange-400 to-orange-600 rounded-full flex items-center justify-end pr-2" style={{ width: `${Math.max((data.value / 55000000) * 100, 10)}%` }}>
                    <span className="text-xs text-white font-medium">{formatCurrency(data.value)}</span>
                  </div>
                </div>
                <span className="text-xs text-gray-500 w-12 text-right">{data.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Funding & Counties */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Funding Source Breakdown</h3>
          <div className="space-y-2">
            {fundingBreakdown.map(([source, data]) => (
              <div key={source} className="flex items-center justify-between py-1.5">
                <FundingBadge source={source} />
                <div className="text-right">
                  <span className="text-sm font-medium text-gray-900">{data.units.toLocaleString()}</span>
                  <span className="text-xs text-gray-500 ml-1">units ({data.count})</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Top Counties by Units at Risk</h3>
          <div className="space-y-2">
            {countyBreakdown.map(([county, units]) => (
              <div key={county} className="flex items-center justify-between py-1">
                <span className="text-sm text-gray-700">{county}</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-100 rounded-full h-2"><div className="h-full bg-blue-500 rounded-full" style={{ width: `${(units / countyBreakdown[0][1]) * 100}%` }}></div></div>
                  <span className="text-sm font-medium text-gray-900 w-12 text-right">{units}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Commercial Distress Summary</h3>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div className="bg-red-50 rounded-lg p-2 text-center">
              <p className="text-xl font-bold text-red-700">{commercialLoanMaturities.filter(p => p.distressLevel === 'Critical').length}</p>
              <p className="text-xs text-red-600">Critical</p>
            </div>
            <div className="bg-orange-50 rounded-lg p-2 text-center">
              <p className="text-xl font-bold text-orange-700">{commercialLoanMaturities.filter(p => p.distressLevel === 'High').length}</p>
              <p className="text-xs text-orange-600">High</p>
            </div>
            <div className="bg-yellow-50 rounded-lg p-2 text-center">
              <p className="text-xl font-bold text-yellow-700">{commercialLoanMaturities.filter(p => p.distressLevel === 'Moderate').length}</p>
              <p className="text-xs text-yellow-600">Moderate</p>
            </div>
            <div className="bg-green-50 rounded-lg p-2 text-center">
              <p className="text-xl font-bold text-green-700">{commercialLoanMaturities.filter(p => p.distressLevel === 'Low').length}</p>
              <p className="text-xs text-green-600">Low</p>
            </div>
          </div>
          <p className="text-xs text-gray-500">Total distressed value: {formatCurrency(commercialLoanMaturities.filter(p => p.distressLevel === 'Critical' || p.distressLevel === 'High').reduce((s, p) => s + p.loanAmount, 0))}</p>
        </div>
      </div>

      {/* Top Opportunities */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900">🏠 Top Affordable Housing Opportunities</h3>
            <button onClick={() => onNavigate('affordable')} className="text-xs text-blue-600 hover:underline">View All →</button>
          </div>
          <div className="space-y-2">
            {topOpportunities.ah.map(p => (
              <div key={p.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-900">{p.propertyName}</p>
                  <p className="text-xs text-gray-500">{p.city} • {p.totalUnits} units • {formatDate(p.expirationDate)}</p>
                </div>
                <ScoreBar score={p.investmentScore} />
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-900">🏢 Top Commercial Loan Opportunities</h3>
            <button onClick={() => onNavigate('commercial')} className="text-xs text-blue-600 hover:underline">View All →</button>
          </div>
          <div className="space-y-2">
            {topOpportunities.cl.map(p => (
              <div key={p.id} className="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
                <div>
                  <p className="text-sm font-medium text-gray-900">{p.propertyName}</p>
                  <p className="text-xs text-gray-500">{p.city} • {formatCurrency(p.loanAmount)} • {formatDate(p.loanMaturityDate)}</p>
                </div>
                <ScoreBar score={p.investmentScore} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// Affordable Housing Tab
function AffordableHousingTab({ onOpenDetail, leadStates }: { onOpenDetail: (p: AffordableHousingProperty) => void; leadStates: Record<string, { status: LeadStatus; notes: string }> }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedYear, setSelectedYear] = useState<number | 'all'>('all');
  const [selectedCounty, setSelectedCounty] = useState<string>('all');
  const [selectedFunding, setSelectedFunding] = useState<string>('all');
  const [selectedRisk, setSelectedRisk] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('investmentScore');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const counties = getUniqueCounties();
  const years = getUniqueYears();
  const fundingSources = getUniqueFundingSources();

  const filteredData = useMemo(() => {
    let data = [...affordableHousingData];
    if (searchTerm) { const t = searchTerm.toLowerCase(); data = data.filter(p => p.propertyName.toLowerCase().includes(t) || p.city.toLowerCase().includes(t) || p.address.toLowerCase().includes(t) || p.county.toLowerCase().includes(t)); }
    if (selectedYear !== 'all') data = data.filter(p => p.expirationYear === selectedYear);
    if (selectedCounty !== 'all') data = data.filter(p => p.county === selectedCounty);
    if (selectedFunding !== 'all') data = data.filter(p => p.fundingSource === selectedFunding);
    if (selectedRisk !== 'all') data = data.filter(p => p.riskLevel === selectedRisk);
    data.sort((a, b) => {
      let vA: any, vB: any;
      switch (sortBy) {
        case 'expirationDate': vA = a.expirationDate; vB = b.expirationDate; break;
        case 'propertyName': vA = a.propertyName; vB = b.propertyName; break;
        case 'totalUnits': vA = a.totalUnits; vB = b.totalUnits; break;
        case 'city': vA = a.city; vB = b.city; break;
        case 'investmentScore': vA = a.investmentScore; vB = b.investmentScore; break;
        case 'daysUntilExpiration': vA = a.daysUntilExpiration; vB = b.daysUntilExpiration; break;
        default: vA = a.expirationDate; vB = b.expirationDate;
      }
      if (typeof vA === 'number') return sortDir === 'asc' ? vA - vB : vB - vA;
      return sortDir === 'asc' ? String(vA).localeCompare(String(vB)) : String(vB).localeCompare(String(vA));
    });
    return data;
  }, [searchTerm, selectedYear, selectedCounty, selectedFunding, selectedRisk, sortBy, sortDir]);

  const pagedData = filteredData.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(filteredData.length / pageSize);

  const handleSort = (field: string) => { if (sortBy === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc'); else { setSortBy(field); setSortDir('desc'); } };

  const exportExcel = useCallback(() => {
    const fileName = generateExcelReport({ filteredAH: filteredData });
    alert(`✅ Downloaded: ${fileName}\n\nContains filtered results (${filteredData.length} properties) across all sheets.`);
  }, [filteredData]);

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-3">
          <div className="lg:col-span-2">
            <label className="text-xs font-medium text-gray-500 mb-1 block">Search</label>
            <input type="text" placeholder="Property, city, address..." value={searchTerm} onChange={e => { setSearchTerm(e.target.value); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Year</label>
            <select value={selectedYear} onChange={e => { setSelectedYear(e.target.value === 'all' ? 'all' : Number(e.target.value)); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Years</option>
              {years.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">County</label>
            <select value={selectedCounty} onChange={e => { setSelectedCounty(e.target.value); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Counties</option>
              {counties.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Funding</label>
            <select value={selectedFunding} onChange={e => { setSelectedFunding(e.target.value); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Sources</option>
              {fundingSources.map(f => <option key={f} value={f}>{f}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Risk</label>
            <select value={selectedRisk} onChange={e => { setSelectedRisk(e.target.value); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Levels</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between flex-wrap gap-2">
          <p className="text-sm text-gray-500">{filteredData.length} properties • {filteredData.reduce((s, p) => s + p.totalUnits, 0).toLocaleString()} units</p>
          <button onClick={exportExcel} className="px-3 py-1.5 bg-green-100 hover:bg-green-200 rounded-lg text-xs font-medium text-green-700 transition-colors flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
            Export Filtered to Excel
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('daysUntilExpiration')}>Due {sortBy === 'daysUntilExpiration' && (sortDir === 'asc' ? '↑' : '↓')}</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('propertyName')}>Property {sortBy === 'propertyName' && (sortDir === 'asc' ? '↑' : '↓')}</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Location</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('totalUnits')}>Units {sortBy === 'totalUnits' && (sortDir === 'asc' ? '↑' : '↓')}</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Funding</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Risk</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('investmentScore')}>Score {sortBy === 'investmentScore' && (sortDir === 'asc' ? '↑' : '↓')}</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {pagedData.map(property => (
                <tr key={property.id} className="hover:bg-blue-50/50 transition-colors cursor-pointer" onClick={() => onOpenDetail(property)}>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <p className="text-xs text-gray-700">{formatDate(property.expirationDate)}</p>
                    <p className={`text-xs font-medium ${property.daysUntilExpiration <= 365 ? 'text-red-600' : property.daysUntilExpiration <= 1095 ? 'text-amber-600' : 'text-gray-500'}`}>{formatDays(property.daysUntilExpiration)}</p>
                  </td>
                  <td className="px-3 py-2.5">
                    <p className="font-medium text-gray-900 text-xs">{property.propertyName}</p>
                    <p className="text-xs text-gray-500 truncate max-w-40">{property.address}</p>
                  </td>
                  <td className="px-3 py-2.5">
                    <p className="text-xs text-gray-700">{property.city}</p>
                    <p className="text-xs text-gray-500">{property.county}</p>
                  </td>
                  <td className="px-3 py-2.5 font-medium text-gray-900 text-xs">{property.totalUnits}</td>
                  <td className="px-3 py-2.5"><FundingBadge source={property.fundingSource} /></td>
                  <td className="px-3 py-2.5"><RiskBadge level={property.riskLevel} /></td>
                  <td className="px-3 py-2.5"><ScoreBar score={property.investmentScore} /></td>
                  <td className="px-3 py-2.5"><StatusBadge status={leadStates[property.id]?.status || property.leadStatus} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
            <p className="text-xs text-gray-500">Page {page + 1} of {totalPages}</p>
            <div className="flex gap-1">
              <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="px-3 py-1 text-xs rounded border border-gray-300 disabled:opacity-50 hover:bg-white">← Prev</button>
              <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="px-3 py-1 text-xs rounded border border-gray-300 disabled:opacity-50 hover:bg-white">Next →</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Commercial Loan Tab
function CommercialLoanTab({ onOpenDetail, leadStates }: { onOpenDetail: (p: CommercialLoanMaturity) => void; leadStates: Record<string, { status: LeadStatus; notes: string }> }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedYear, setSelectedYear] = useState<number | 'all'>('all');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [selectedDistress, setSelectedDistress] = useState<string>('all');
  const [selectedLoanType, setSelectedLoanType] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('investmentScore');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [page, setPage] = useState(0);
  const pageSize = 20;

  const propertyTypes = getUniquePropertyTypes();
  const maturityYears = getMaturityYears();
  const loanTypes = getUniqueLoanTypes();

  const filteredData = useMemo(() => {
    let data = [...commercialLoanMaturities];
    if (searchTerm) { const t = searchTerm.toLowerCase(); data = data.filter(p => p.propertyName.toLowerCase().includes(t) || p.city.toLowerCase().includes(t) || p.lender.toLowerCase().includes(t) || p.propertyType.toLowerCase().includes(t)); }
    if (selectedYear !== 'all') data = data.filter(p => p.maturityYear === selectedYear);
    if (selectedType !== 'all') data = data.filter(p => p.propertyType === selectedType);
    if (selectedDistress !== 'all') data = data.filter(p => p.distressLevel === selectedDistress);
    if (selectedLoanType !== 'all') data = data.filter(p => p.loanType === selectedLoanType);
    data.sort((a, b) => {
      let vA: any, vB: any;
      switch (sortBy) {
        case 'loanMaturityDate': vA = a.loanMaturityDate; vB = b.loanMaturityDate; break;
        case 'propertyName': vA = a.propertyName; vB = b.propertyName; break;
        case 'loanAmount': vA = a.loanAmount; vB = b.loanAmount; break;
        case 'ltv': vA = a.ltv; vB = b.ltv; break;
        case 'investmentScore': vA = a.investmentScore; vB = b.investmentScore; break;
        case 'daysUntilMaturity': vA = a.daysUntilMaturity; vB = b.daysUntilMaturity; break;
        default: vA = a.loanMaturityDate; vB = b.loanMaturityDate;
      }
      if (typeof vA === 'number') return sortDir === 'asc' ? vA - vB : vB - vA;
      return sortDir === 'asc' ? String(vA).localeCompare(String(vB)) : String(vB).localeCompare(String(vA));
    });
    return data;
  }, [searchTerm, selectedYear, selectedType, selectedDistress, selectedLoanType, sortBy, sortDir]);

  const pagedData = filteredData.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(filteredData.length / pageSize);

  const handleSort = (field: string) => { if (sortBy === field) setSortDir(d => d === 'asc' ? 'desc' : 'asc'); else { setSortBy(field); setSortDir('desc'); } };

  const exportExcel = useCallback(() => {
    const fileName = generateExcelReport({ filteredCL: filteredData });
    alert(`✅ Downloaded: ${fileName}\n\nContains filtered results (${filteredData.length} loans) across all sheets.`);
  }, [filteredData]);

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Search</label>
            <input type="text" placeholder="Property, city, lender..." value={searchTerm} onChange={e => { setSearchTerm(e.target.value); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500" />
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Maturity Year</label>
            <select value={selectedYear} onChange={e => { setSelectedYear(e.target.value === 'all' ? 'all' : Number(e.target.value)); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Years</option>
              {maturityYears.map(y => <option key={y} value={y}>{y}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Property Type</label>
            <select value={selectedType} onChange={e => { setSelectedType(e.target.value); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Types</option>
              {propertyTypes.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Loan Type</label>
            <select value={selectedLoanType} onChange={e => { setSelectedLoanType(e.target.value); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Types</option>
              {loanTypes.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs font-medium text-gray-500 mb-1 block">Distress Level</label>
            <select value={selectedDistress} onChange={e => { setSelectedDistress(e.target.value); setPage(0); }} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="all">All Levels</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Moderate">Moderate</option>
              <option value="Low">Low</option>
            </select>
          </div>
        </div>
        <div className="mt-3 flex items-center justify-between flex-wrap gap-2">
          <p className="text-sm text-gray-500">{filteredData.length} loans • {formatCurrency(filteredData.reduce((s, p) => s + p.loanAmount, 0))} total value</p>
          <button onClick={exportExcel} className="px-3 py-1.5 bg-green-100 hover:bg-green-200 rounded-lg text-xs font-medium text-green-700 transition-colors flex items-center gap-1">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
            Export Filtered to Excel
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('daysUntilMaturity')}>Due {sortBy === 'daysUntilMaturity' && (sortDir === 'asc' ? '↑' : '↓')}</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('propertyName')}>Property {sortBy === 'propertyName' && (sortDir === 'asc' ? '↑' : '↓')}</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Type</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('loanAmount')}>Amount {sortBy === 'loanAmount' && (sortDir === 'asc' ? '↑' : '↓')}</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Lender</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('ltv')}>LTV {sortBy === 'ltv' && (sortDir === 'asc' ? '↑' : '↓')}</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">DSCR</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Occ</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Distress</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600 cursor-pointer hover:text-gray-900" onClick={() => handleSort('investmentScore')}>Score {sortBy === 'investmentScore' && (sortDir === 'asc' ? '↑' : '↓')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {pagedData.map(loan => (
                <tr key={loan.id} className="hover:bg-orange-50/50 transition-colors cursor-pointer" onClick={() => onOpenDetail(loan)}>
                  <td className="px-3 py-2.5 whitespace-nowrap">
                    <p className="text-xs text-gray-700">{formatDate(loan.loanMaturityDate)}</p>
                    <p className={`text-xs font-medium ${loan.daysUntilMaturity <= 365 ? 'text-red-600' : loan.daysUntilMaturity <= 1095 ? 'text-amber-600' : 'text-gray-500'}`}>{formatDays(loan.daysUntilMaturity)}</p>
                  </td>
                  <td className="px-3 py-2.5">
                    <p className="font-medium text-gray-900 text-xs">{loan.propertyName}</p>
                    <p className="text-xs text-gray-500">{loan.city}</p>
                  </td>
                  <td className="px-3 py-2.5"><span className="px-1.5 py-0.5 bg-gray-100 rounded text-xs font-medium text-gray-700">{loan.propertyType}</span></td>
                  <td className="px-3 py-2.5 font-medium text-gray-900 text-xs">{formatCurrency(loan.loanAmount)}</td>
                  <td className="px-3 py-2.5 text-xs text-gray-600">{loan.lender}</td>
                  <td className="px-3 py-2.5"><span className={`text-xs font-medium ${loan.ltv >= 80 ? 'text-red-600' : loan.ltv >= 70 ? 'text-yellow-600' : 'text-green-600'}`}>{loan.ltv}%</span></td>
                  <td className="px-3 py-2.5"><span className={`text-xs font-medium ${loan.dscr < 1.0 ? 'text-red-600' : loan.dscr < 1.2 ? 'text-yellow-600' : 'text-green-600'}`}>{loan.dscr.toFixed(2)}</span></td>
                  <td className="px-3 py-2.5"><span className={`text-xs font-medium ${loan.occupancyRate < 70 ? 'text-red-600' : loan.occupancyRate < 85 ? 'text-yellow-600' : 'text-green-600'}`}>{loan.occupancyRate}%</span></td>
                  <td className="px-3 py-2.5"><RiskBadge level={loan.distressLevel} /></td>
                  <td className="px-3 py-2.5"><ScoreBar score={loan.investmentScore} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200 bg-gray-50">
            <p className="text-xs text-gray-500">Page {page + 1} of {totalPages}</p>
            <div className="flex gap-1">
              <button onClick={() => setPage(p => Math.max(0, p - 1))} disabled={page === 0} className="px-3 py-1 text-xs rounded border border-gray-300 disabled:opacity-50 hover:bg-white">← Prev</button>
              <button onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))} disabled={page >= totalPages - 1} className="px-3 py-1 text-xs rounded border border-gray-300 disabled:opacity-50 hover:bg-white">Next →</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// Combined Leads Tab
function CombinedLeadsTab({ onOpenAHDetail, onOpenCLDetail, ahLeadStates, clLeadStates }: {
  onOpenAHDetail: (p: AffordableHousingProperty) => void;
  onOpenCLDetail: (p: CommercialLoanMaturity) => void;
  ahLeadStates: Record<string, { status: LeadStatus; notes: string }>;
  clLeadStates: Record<string, { status: LeadStatus; notes: string }>;
}) {
  const [filterType, setFilterType] = useState<'all' | 'affordable' | 'commercial'>('all');
  const [distressOnly, setDistressOnly] = useState(false);
  const [timeFilter, setTimeFilter] = useState<string>('all');

  interface CombinedLead { id: string; source: 'affordable' | 'commercial'; name: string; location: string; date: string; year: number; units: number; value?: number; risk: string; detail: string; score: number; status: LeadStatus; }

  const combinedLeads: CombinedLead[] = useMemo(() => {
    const leads: CombinedLead[] = [];
    affordableHousingData.forEach(p => { leads.push({ id: p.id, source: 'affordable', name: p.propertyName, location: `${p.city}, ${p.county}`, date: p.expirationDate, year: p.expirationYear, units: p.totalUnits, risk: p.riskLevel, detail: `${p.fundingSource} • ${p.totalUnits} units`, score: p.investmentScore, status: ahLeadStates[p.id]?.status || p.leadStatus }); });
    commercialLoanMaturities.forEach(p => { leads.push({ id: p.id, source: 'commercial', name: p.propertyName, location: `${p.city}, ${p.county}`, date: p.loanMaturityDate, year: p.maturityYear, units: p.units, value: p.loanAmount, risk: p.distressLevel, detail: `${p.propertyType} • ${formatCurrency(p.loanAmount)}`, score: p.investmentScore, status: clLeadStates[p.id]?.status || p.leadStatus }); });
    return leads.sort((a, b) => a.date.localeCompare(b.date));
  }, [ahLeadStates, clLeadStates]);

  const filtered = useMemo(() => {
    let data = [...combinedLeads];
    if (filterType !== 'all') data = data.filter(l => l.source === filterType);
    if (distressOnly) data = data.filter(l => l.risk === 'High' || l.risk === 'Critical');
    if (timeFilter === '12mo') data = data.filter(l => { const d = Math.ceil((new Date(l.date).getTime() - new Date('2026-10-04').getTime()) / (1000 * 60 * 60 * 24)); return d <= 365 && d > 0; });
    else if (timeFilter === '24mo') data = data.filter(l => { const d = Math.ceil((new Date(l.date).getTime() - new Date('2026-10-04').getTime()) / (1000 * 60 * 60 * 24)); return d <= 730 && d > 0; });
    return data;
  }, [combinedLeads, filterType, distressOnly, timeFilter]);

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            <button onClick={() => setFilterType('all')} className={`px-3 py-1.5 text-xs font-medium ${filterType === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}>All</button>
            <button onClick={() => setFilterType('affordable')} className={`px-3 py-1.5 text-xs font-medium ${filterType === 'affordable' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}>🏠 Affordable</button>
            <button onClick={() => setFilterType('commercial')} className={`px-3 py-1.5 text-xs font-medium ${filterType === 'commercial' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'}`}>🏢 Commercial</button>
          </div>
          <select value={timeFilter} onChange={e => setTimeFilter(e.target.value)} className="px-3 py-1.5 border border-gray-300 rounded-lg text-xs">
            <option value="all">All Timeframes</option>
            <option value="12mo">Next 12 Months</option>
            <option value="24mo">Next 24 Months</option>
          </select>
          <label className="flex items-center gap-2 text-xs text-gray-700">
            <input type="checkbox" checked={distressOnly} onChange={e => setDistressOnly(e.target.checked)} className="rounded border-gray-300 text-blue-600" />
            High/Critical Only
          </label>
          <span className="text-xs text-gray-500 ml-auto">{filtered.length} leads</span>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Date</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Source</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Property</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Location</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Details</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Score</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Risk</th>
                <th className="text-left px-3 py-3 font-medium text-gray-600">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filtered.map(lead => (
                <tr key={`${lead.source}-${lead.id}`} className="hover:bg-gray-50 transition-colors cursor-pointer" onClick={() => lead.source === 'affordable' ? onOpenAHDetail(affordableHousingData.find(p => p.id === lead.id)!) : onOpenCLDetail(commercialLoanMaturities.find(p => p.id === lead.id)!)}>
                  <td className="px-3 py-2.5 text-xs text-gray-700 whitespace-nowrap">{formatDate(lead.date)}</td>
                  <td className="px-3 py-2.5"><span className={`px-2 py-0.5 rounded text-xs font-medium ${lead.source === 'affordable' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'}`}>{lead.source === 'affordable' ? '🏠 AH' : '🏢 CL'}</span></td>
                  <td className="px-3 py-2.5 font-medium text-gray-900 text-xs">{lead.name}</td>
                  <td className="px-3 py-2.5 text-xs text-gray-600">{lead.location}</td>
                  <td className="px-3 py-2.5 text-xs text-gray-600">{lead.detail}</td>
                  <td className="px-3 py-2.5"><ScoreBar score={lead.score} /></td>
                  <td className="px-3 py-2.5"><RiskBadge level={lead.risk} /></td>
                  <td className="px-3 py-2.5"><StatusBadge status={lead.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// Analytics Tab
function AnalyticsTab() {
  const amiBreakdown = useMemo(() => {
    const total30 = affordableHousingData.reduce((s, p) => s + p.ami30, 0);
    const total40 = affordableHousingData.reduce((s, p) => s + p.ami40, 0);
    const total50 = affordableHousingData.reduce((s, p) => s + p.ami50, 0);
    const total60 = affordableHousingData.reduce((s, p) => s + p.ami60, 0);
    const total70 = affordableHousingData.reduce((s, p) => s + p.ami70, 0);
    const total80 = affordableHousingData.reduce((s, p) => s + p.ami80, 0);
    const total = total30 + total40 + total50 + total60 + total70 + total80;
    return [
      { level: '30% AMI', units: total30, color: 'bg-red-400' },
      { level: '40% AMI', units: total40, color: 'bg-orange-400' },
      { level: '50% AMI', units: total50, color: 'bg-yellow-400' },
      { level: '60% AMI', units: total60, color: 'bg-green-400' },
      { level: '70% AMI', units: total70, color: 'bg-teal-400' },
      { level: '80% AMI', units: total80, color: 'bg-blue-400' },
    ].filter(a => a.units > 0).map(a => ({ ...a, pct: total > 0 ? (a.units / total) * 100 : 0 }));
  }, []);

  const ltvDistribution = useMemo(() => {
    const buckets = { '<60': 0, '60-70': 0, '70-80': 0, '80+': 0 };
    commercialLoanMaturities.forEach(p => {
      if (p.ltv < 60) buckets['<60']++;
      else if (p.ltv < 70) buckets['60-70']++;
      else if (p.ltv < 80) buckets['70-80']++;
      else buckets['80+']++;
    });
    return buckets;
  }, []);

  const avgMetrics = useMemo(() => {
    const avgLTV = commercialLoanMaturities.reduce((s, p) => s + p.ltv, 0) / commercialLoanMaturities.length;
    const avgDSCR = commercialLoanMaturities.reduce((s, p) => s + p.dscr, 0) / commercialLoanMaturities.length;
    const avgOcc = commercialLoanMaturities.reduce((s, p) => s + p.occupancyRate, 0) / commercialLoanMaturities.length;
    const avgCap = commercialLoanMaturities.reduce((s, p) => s + p.capRate, 0) / commercialLoanMaturities.length;
    const totalNOI = commercialLoanMaturities.reduce((s, p) => s + p.noi, 0);
    return { avgLTV, avgDSCR, avgOcc, avgCap, totalNOI };
  }, []);

  const yearOverYear = useMemo(() => {
    const ahByYear: Record<number, number> = {};
    affordableHousingData.forEach(p => { ahByYear[p.expirationYear] = (ahByYear[p.expirationYear] || 0) + p.totalUnits; });
    const clByYear: Record<number, number> = {};
    commercialLoanMaturities.forEach(p => { clByYear[p.maturityYear] = (clByYear[p.maturityYear] || 0) + p.loanAmount; });
    const allYears = [...new Set([...Object.keys(ahByYear), ...Object.keys(clByYear)])].map(Number).sort();
    return allYears.map(y => ({ year: y, ahUnits: ahByYear[y] || 0, clValue: clByYear[y] || 0 }));
  }, []);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-center">
          <p className="text-xs text-gray-500">Avg LTV (Commercial)</p>
          <p className="text-2xl font-bold text-gray-900">{avgMetrics.avgLTV.toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-center">
          <p className="text-xs text-gray-500">Avg DSCR (Commercial)</p>
          <p className="text-2xl font-bold text-gray-900">{avgMetrics.avgDSCR.toFixed(2)}</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-center">
          <p className="text-xs text-gray-500">Avg Occupancy</p>
          <p className="text-2xl font-bold text-gray-900">{avgMetrics.avgOcc.toFixed(1)}%</p>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-center">
          <p className="text-xs text-gray-500">Total Portfolio NOI</p>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(avgMetrics.totalNOI)}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">AMI Level Distribution (Affordable Housing)</h3>
          <div className="space-y-3">
            {amiBreakdown.map(ami => (
              <div key={ami.level} className="flex items-center gap-3">
                <span className="text-xs font-medium text-gray-600 w-16">{ami.level}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-5 relative overflow-hidden">
                  <div className={`h-full ${ami.color} rounded-full flex items-center justify-end pr-2`} style={{ width: `${Math.max(ami.pct, 5)}%` }}>
                    <span className="text-xs text-white font-medium">{ami.units}</span>
                  </div>
                </div>
                <span className="text-xs text-gray-500 w-12 text-right">{ami.pct.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
          <h3 className="text-sm font-semibold text-gray-900 mb-4">LTV Distribution (Commercial Loans)</h3>
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(ltvDistribution).map(([range, count]) => {
              const pct = (count / commercialLoanMaturities.length) * 100;
              const color = range === '80+' ? 'bg-red-400' : range === '70-80' ? 'bg-orange-400' : range === '60-70' ? 'bg-yellow-400' : 'bg-green-400';
              return (
                <div key={range} className="bg-gray-50 rounded-lg p-3 text-center">
                  <p className="text-xs text-gray-500">LTV {range}%</p>
                  <p className="text-xl font-bold text-gray-900">{count}</p>
                  <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1"><div className={`h-full ${color} rounded-full`} style={{ width: `${pct}%` }}></div></div>
                  <p className="text-xs text-gray-500">{pct.toFixed(0)}%</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Year-by-Year Exposure (Units & Loan Value)</h3>
        <div className="space-y-2">
          {yearOverYear.map(y => (
            <div key={y.year} className="flex items-center gap-3">
              <span className="text-sm font-medium text-gray-600 w-12">{y.year}</span>
              <div className="flex-1 flex gap-1">
                <div className="bg-blue-400 rounded h-5 flex items-center px-2" style={{ width: `${Math.max((y.ahUnits / 3000) * 50, 3)}%` }}>
                  <span className="text-xs text-white">{y.ahUnits > 0 ? `${y.ahUnits}u` : ''}</span>
                </div>
                <div className="bg-orange-400 rounded h-5 flex items-center px-2" style={{ width: `${Math.max((y.clValue / 60000000) * 50, 3)}%` }}>
                  <span className="text-xs text-white">{y.clValue > 0 ? formatCurrency(y.clValue) : ''}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="flex gap-4 mt-3">
          <span className="text-xs text-gray-500 flex items-center gap-1"><span className="w-3 h-3 bg-blue-400 rounded"></span>AH Units</span>
          <span className="text-xs text-gray-500 flex items-center gap-1"><span className="w-3 h-3 bg-orange-400 rounded"></span>Commercial Loan Value</span>
        </div>
      </div>
    </div>
  );
}

// Main App
export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const [modalProperty, setModalProperty] = useState<{ property: AffordableHousingProperty | CommercialLoanMaturity; type: 'affordable' | 'commercial' } | null>(null);
  const [ahLeadStates, setAhLeadStates] = useState<Record<string, { status: LeadStatus; notes: string }>>({});
  const [clLeadStates, setClLeadStates] = useState<Record<string, { status: LeadStatus; notes: string }>>({});

  const updateAHLead = useCallback((id: string, status: LeadStatus, notes: string) => {
    setAhLeadStates(prev => ({ ...prev, [id]: { status, notes } }));
  }, []);

  const updateCLLead = useCallback((id: string, status: LeadStatus, notes: string) => {
    setClLeadStates(prev => ({ ...prev, [id]: { status, notes } }));
  }, []);

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'affordable', label: 'Affordable Housing', icon: '🏠' },
    { id: 'commercial', label: 'Loan Maturities', icon: '🏢' },
    { id: 'combined', label: 'Combined Leads', icon: '📋' },
    { id: 'analytics', label: 'Analytics', icon: '📈' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              </div>
              <div>
                <h1 className="text-base font-bold text-gray-900">Off-Market Sourcing System</h1>
                <p className="text-xs text-gray-500 -mt-0.5 hidden sm:block">Affordable Housing Restrictions & Commercial Loan Maturity Tracker</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  const fileName = generateExcelReport();
                  alert(`✅ Excel report downloaded: ${fileName}\n\nContains 6 sheets:\n• Executive Summary\n• Affordable Housing (all properties)\n• Commercial Loans (all maturities)\n• Combined Leads\n• Analytics\n• Data Dictionary`);
                }}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-sm"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                <span className="hidden sm:inline">Download Excel Report</span>
                <span className="sm:hidden">Excel</span>
              </button>
              <span className="text-xs text-gray-400 hidden md:block">Oregon • Oct 2026</span>
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            </div>
          </div>
        </div>
      </header>

      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto">
            {tabs.map(tab => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-1.5 px-3 py-2.5 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${activeTab === tab.id ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}>
                <span>{tab.icon}</span>{tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-5">
        <DownloadBanner />
        {activeTab === 'dashboard' && <Dashboard onNavigate={setActiveTab} />}
        {activeTab === 'affordable' && <AffordableHousingTab onOpenDetail={p => setModalProperty({ property: p, type: 'affordable' })} leadStates={ahLeadStates} />}
        {activeTab === 'commercial' && <CommercialLoanTab onOpenDetail={p => setModalProperty({ property: p, type: 'commercial' })} leadStates={clLeadStates} />}
        {activeTab === 'combined' && <CombinedLeadsTab onOpenAHDetail={p => setModalProperty({ property: p, type: 'affordable' })} onOpenCLDetail={p => setModalProperty({ property: p, type: 'commercial' })} ahLeadStates={ahLeadStates} clLeadStates={clLeadStates} />}
        {activeTab === 'analytics' && <AnalyticsTab />}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
          <div className="flex flex-col md:flex-row items-center justify-between gap-2">
            <p className="text-xs text-gray-500">Sources: OHCS Inventory, HUD/USDA Expirations, Commercial Loan Records • {affordableHousingData.length} AH properties + {commercialLoanMaturities.length} commercial loans</p>
            <p className="text-xs text-gray-400">Coverage: Restrictions expiring 2025-2035 • Loans maturing 2026-2031</p>
          </div>
        </div>
      </footer>

      {modalProperty && (
        <PropertyModal
          property={modalProperty.property}
          type={modalProperty.type}
          onClose={() => setModalProperty(null)}
          onUpdateStatus={(id, status) => {
            if (modalProperty.type === 'affordable') updateAHLead(id, status, ahLeadStates[id]?.notes || '');
            else updateCLLead(id, status, clLeadStates[id]?.notes || '');
          }}
          onUpdateNotes={(id, notes) => {
            if (modalProperty.type === 'affordable') updateAHLead(id, ahLeadStates[id]?.status || 'New', notes);
            else updateCLLead(id, clLeadStates[id]?.status || 'New', notes);
          }}
        />
      )}
    </div>
  );
}
