export interface CommercialLoanMaturity {
  id: string;
  propertyName: string;
  address: string;
  city: string;
  county: string;
  propertyType: string;
  loanAmount: number;
  originalLoanDate: string;
  loanMaturityDate: string;
  maturityYear: number;
  lender: string;
  loanType: string;
  interestRate: number;
  units: number;
  yearBuilt: number;
  sqft: number;
  occupancyRate: number;
  capRate: number;
  noi: number;
  ltv: number;
  dscr: number;
  distressLevel: 'Critical' | 'High' | 'Moderate' | 'Low';
  daysUntilMaturity: number;
  investmentScore: number;
  leadStatus: 'New' | 'Researching' | 'Contacted' | 'Under Review' | 'Passed';
  notes: string;
  conversionPotential: string;
}

function calcDays(dateStr: string): number {
  const now = new Date('2026-10-04');
  const mat = new Date(dateStr);
  return Math.ceil((mat.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
}

function calcScore(p: { loanAmount: number; distressLevel: string; ltv: number; occupancyRate: number; daysUntilMaturity: number }): number {
  let score = 40;
  if (p.loanAmount >= 20000000) score += 20;
  else if (p.loanAmount >= 10000000) score += 15;
  else if (p.loanAmount >= 5000000) score += 10;
  if (p.distressLevel === 'Critical') score += 20;
  else if (p.distressLevel === 'High') score += 15;
  if (p.ltv >= 80) score += 10;
  if (p.occupancyRate < 70) score += 5;
  if (p.daysUntilMaturity <= 365) score += 5;
  return Math.min(100, Math.max(1, score));
}

const rawData: Omit<CommercialLoanMaturity, 'daysUntilMaturity' | 'investmentScore' | 'leadStatus' | 'notes'>[] = [
  { id: "CLM001", propertyName: "Pioneer Tower Office Complex", address: "1200 SW Morrison St", city: "Portland", county: "Multnomah", propertyType: "Office", loanAmount: 45000000, originalLoanDate: "2021-03-15", loanMaturityDate: "2026-03-15", maturityYear: 2026, lender: "Wells Fargo", loanType: "CMBS", interestRate: 4.25, units: 0, yearBuilt: 2008, sqft: 185000, occupancyRate: 72, capRate: 5.8, noi: 2610000, ltv: 78, dscr: 1.12, distressLevel: "High", conversionPotential: "Office-to-Residential" },
  { id: "CLM002", propertyName: "Burnside Retail Center", address: "2400 E Burnside St", city: "Portland", county: "Multnomah", propertyType: "Retail", loanAmount: 18500000, originalLoanDate: "2020-06-30", loanMaturityDate: "2026-06-30", maturityYear: 2026, lender: "Banner Bank", loanType: "Portfolio", interestRate: 4.75, units: 0, yearBuilt: 1995, sqft: 62000, occupancyRate: 65, capRate: 7.2, noi: 1332000, ltv: 82, dscr: 0.95, distressLevel: "Critical", conversionPotential: "Mixed-Use Redevelopment" },
  { id: "CLM003", propertyName: "Willamette Industrial Park", address: "4500 SE Industrial Way", city: "Salem", county: "Marion", propertyType: "Industrial", loanAmount: 12000000, originalLoanDate: "2021-09-01", loanMaturityDate: "2026-09-01", maturityYear: 2026, lender: "KeyBank", loanType: "Bridge", interestRate: 5.50, units: 0, yearBuilt: 2001, sqft: 95000, occupancyRate: 88, capRate: 6.5, noi: 780000, ltv: 65, dscr: 1.35, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM004", propertyName: "Pearl District Lofts", address: "1100 NW Flanders St", city: "Portland", county: "Multnomah", propertyType: "Mixed-Use", loanAmount: 32000000, originalLoanDate: "2021-11-15", loanMaturityDate: "2026-11-15", maturityYear: 2026, lender: "Umpqua Bank", loanType: "Construction-to-Perm", interestRate: 3.95, units: 84, yearBuilt: 2019, sqft: 125000, occupancyRate: 91, capRate: 4.8, noi: 1536000, ltv: 71, dscr: 1.22, distressLevel: "Moderate", conversionPotential: "N/A" },
  { id: "CLM005", propertyName: "Brookings Coastal Apartments", address: "800 Chetco Ave", city: "Brookings", county: "Curry", propertyType: "Multifamily", loanAmount: 5000000, originalLoanDate: "2021-08-15", loanMaturityDate: "2026-08-15", maturityYear: 2026, lender: "California Oregon Bank", loanType: "Portfolio", interestRate: 4.10, units: 36, yearBuilt: 1985, sqft: 32000, occupancyRate: 97, capRate: 6.0, noi: 300000, ltv: 55, dscr: 1.45, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM006", propertyName: "Forest Grove Apartments", address: "2000 Main St", city: "Forest Grove", county: "Washington", propertyType: "Multifamily", loanAmount: 8000000, originalLoanDate: "2021-05-01", loanMaturityDate: "2026-05-01", maturityYear: 2026, lender: "Tri Counties Bank", loanType: "Portfolio", interestRate: 3.85, units: 48, yearBuilt: 1978, sqft: 42000, occupancyRate: 95, capRate: 5.5, noi: 440000, ltv: 60, dscr: 1.38, distressLevel: "Low", conversionPotential: "Value-Add Renovation" },
  { id: "CLM007", propertyName: "Eugene Medical Plaza", address: "3200 River Rd", city: "Eugene", county: "Lane", propertyType: "Medical Office", loanAmount: 22000000, originalLoanDate: "2022-01-31", loanMaturityDate: "2027-01-31", maturityYear: 2027, lender: "First Republic", loanType: "CMBS", interestRate: 3.65, units: 0, yearBuilt: 2012, sqft: 78000, occupancyRate: 94, capRate: 5.5, noi: 1210000, ltv: 68, dscr: 1.40, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM008", propertyName: "Bend Commerce Center", address: "62085 N Hwy 97", city: "Bend", county: "Deschutes", propertyType: "Office", loanAmount: 15000000, originalLoanDate: "2022-04-15", loanMaturityDate: "2027-04-15", maturityYear: 2027, lender: "Oregon Community Bank", loanType: "Portfolio", interestRate: 4.50, units: 0, yearBuilt: 2005, sqft: 55000, occupancyRate: 68, capRate: 7.0, noi: 1050000, ltv: 80, dscr: 0.98, distressLevel: "High", conversionPotential: "Office-to-Residential" },
  { id: "CLM009", propertyName: "McMinnville Wine Country Inn", address: "2300 NE Hwy 99W", city: "McMinnville", county: "Yamhill", propertyType: "Hospitality", loanAmount: 7000000, originalLoanDate: "2022-03-15", loanMaturityDate: "2027-03-15", maturityYear: 2027, lender: "Columbia State Bank", loanType: "SBA 504", interestRate: 4.25, units: 65, yearBuilt: 2005, sqft: 38000, occupancyRate: 72, capRate: 7.0, noi: 490000, ltv: 75, dscr: 1.05, distressLevel: "Moderate", conversionPotential: "Adaptive Reuse" },
  { id: "CLM010", propertyName: "Newport Harbor Marina", address: "500 SE Bay Blvd", city: "Newport", county: "Lincoln", propertyType: "Special Purpose", loanAmount: 8000000, originalLoanDate: "2022-09-15", loanMaturityDate: "2027-09-15", maturityYear: 2027, lender: "Oregon Community Bank", loanType: "Portfolio", interestRate: 5.00, units: 0, yearBuilt: 1988, sqft: 25000, occupancyRate: 78, capRate: 7.8, noi: 624000, ltv: 72, dscr: 1.08, distressLevel: "Moderate", conversionPotential: "Waterfront Residential" },
  { id: "CLM011", propertyName: "Medford Shopping Village", address: "1800 Crater Lake Hwy", city: "Medford", county: "Jackson", propertyType: "Retail", loanAmount: 9500000, originalLoanDate: "2022-06-30", loanMaturityDate: "2027-06-30", maturityYear: 2027, lender: "Columbia Bank", loanType: "SBA 504", interestRate: 4.50, units: 0, yearBuilt: 1998, sqft: 45000, occupancyRate: 75, capRate: 8.1, noi: 769500, ltv: 75, dscr: 1.02, distressLevel: "Moderate", conversionPotential: "Repositioning" },
  { id: "CLM012", propertyName: "Hillsboro Tech Campus", address: "2950 NW Stucki Ave", city: "Hillsboro", county: "Washington", propertyType: "Office/R&D", loanAmount: 55000000, originalLoanDate: "2022-08-31", loanMaturityDate: "2027-08-31", maturityYear: 2027, lender: "JPMorgan Chase", loanType: "CMBS", interestRate: 3.80, units: 0, yearBuilt: 2016, sqft: 220000, occupancyRate: 78, capRate: 5.2, noi: 2860000, ltv: 74, dscr: 1.15, distressLevel: "Moderate", conversionPotential: "Life Sciences Conversion" },
  { id: "CLM013", propertyName: "Gresham Multifamily Portfolio", address: "Multiple Addresses", city: "Gresham", county: "Multnomah", propertyType: "Multifamily", loanAmount: 28000000, originalLoanDate: "2022-12-15", loanMaturityDate: "2027-12-15", maturityYear: 2027, lender: "Zions Bank", loanType: "Agency (Fannie Mae)", interestRate: 3.55, units: 156, yearBuilt: 1988, sqft: 142000, occupancyRate: 92, capRate: 5.0, noi: 1400000, ltv: 72, dscr: 1.30, distressLevel: "Low", conversionPotential: "Value-Add Renovation" },
  { id: "CLM014", propertyName: "Tigard Professional Building", address: "12600 SW 68th Ave", city: "Tigard", county: "Washington", propertyType: "Office", loanAmount: 8500000, originalLoanDate: "2023-02-28", loanMaturityDate: "2028-02-28", maturityYear: 2028, lender: "Washington Federal", loanType: "Portfolio", interestRate: 5.25, units: 0, yearBuilt: 2003, sqft: 38000, occupancyRate: 62, capRate: 7.8, noi: 663000, ltv: 85, dscr: 0.88, distressLevel: "Critical", conversionPotential: "Office-to-Residential" },
  { id: "CLM015", propertyName: "Corvallis Student Housing", address: "2100 NW Monroe Ave", city: "Corvallis", county: "Benton", propertyType: "Student Housing", loanAmount: 19000000, originalLoanDate: "2023-05-15", loanMaturityDate: "2028-05-15", maturityYear: 2028, lender: "KeyBank", loanType: "Construction-to-Perm", interestRate: 4.15, units: 180, yearBuilt: 2015, sqft: 95000, occupancyRate: 95, capRate: 5.5, noi: 1045000, ltv: 68, dscr: 1.42, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM016", propertyName: "Beaverton Retail Corridor", address: "15600 SW Millikan Way", city: "Beaverton", county: "Washington", propertyType: "Retail", loanAmount: 14000000, originalLoanDate: "2023-08-31", loanMaturityDate: "2028-08-31", maturityYear: 2028, lender: "Pacific Continental Bank", loanType: "Portfolio", interestRate: 4.90, units: 0, yearBuilt: 2006, sqft: 52000, occupancyRate: 70, capRate: 7.5, noi: 1050000, ltv: 78, dscr: 1.01, distressLevel: "High", conversionPotential: "Mixed-Use Redevelopment" },
  { id: "CLM017", propertyName: "Albany Industrial Complex", address: "3500 Airport Rd", city: "Albany", county: "Linn", propertyType: "Industrial", loanAmount: 7500000, originalLoanDate: "2023-11-30", loanMaturityDate: "2028-11-30", maturityYear: 2028, lender: "HomeStreet Bank", loanType: "Bridge", interestRate: 5.75, units: 0, yearBuilt: 1990, sqft: 72000, occupancyRate: 85, capRate: 7.0, noi: 525000, ltv: 70, dscr: 1.18, distressLevel: "Moderate", conversionPotential: "N/A" },
  { id: "CLM018", propertyName: "The Dalles Data Center", address: "1500 West 9th St", city: "The Dalles", county: "Wasco", propertyType: "Data Center", loanAmount: 35000000, originalLoanDate: "2023-12-31", loanMaturityDate: "2028-12-31", maturityYear: 2028, lender: "Goldman Sachs", loanType: "CMBS", interestRate: 3.50, units: 0, yearBuilt: 2012, sqft: 120000, occupancyRate: 100, capRate: 5.0, noi: 1750000, ltv: 55, dscr: 1.55, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM019", propertyName: "Dallas Self Storage", address: "650 SE Oak St", city: "Dallas", county: "Polk", propertyType: "Self Storage", loanAmount: 4500000, originalLoanDate: "2023-06-30", loanMaturityDate: "2028-06-30", maturityYear: 2028, lender: "First National Bank of Oregon", loanType: "Portfolio", interestRate: 4.50, units: 0, yearBuilt: 2015, sqft: 55000, occupancyRate: 88, capRate: 6.5, noi: 292500, ltv: 58, dscr: 1.42, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM020", propertyName: "Lake Oswego Senior Living", address: "16800 Lower Boones Ferry Rd", city: "Lake Oswego", county: "Clackamas", propertyType: "Senior Living", loanAmount: 25000000, originalLoanDate: "2024-01-31", loanMaturityDate: "2029-01-31", maturityYear: 2029, lender: "AIG", loanType: "CMBS", interestRate: 4.75, units: 120, yearBuilt: 2010, sqft: 110000, occupancyRate: 82, capRate: 6.0, noi: 1500000, ltv: 73, dscr: 1.10, distressLevel: "Moderate", conversionPotential: "N/A" },
  { id: "CLM021", propertyName: "Redmond Distribution Center", address: "7050 SW 43rd St", city: "Redmond", county: "Deschutes", propertyType: "Industrial/Warehouse", loanAmount: 18000000, originalLoanDate: "2024-04-30", loanMaturityDate: "2029-04-30", maturityYear: 2029, lender: "CBRE Capital Markets", loanType: "CMBS", interestRate: 4.25, units: 0, yearBuilt: 2018, sqft: 150000, occupancyRate: 96, capRate: 5.8, noi: 1044000, ltv: 62, dscr: 1.48, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM022", propertyName: "Klamath Falls Mixed-Use", address: "200 Main St", city: "Klamath Falls", county: "Klamath", propertyType: "Mixed-Use", loanAmount: 6000000, originalLoanDate: "2024-07-15", loanMaturityDate: "2029-07-15", maturityYear: 2029, lender: "Oregon Community Credit Union", loanType: "Portfolio", interestRate: 5.50, units: 42, yearBuilt: 2004, sqft: 35000, occupancyRate: 72, capRate: 8.5, noi: 510000, ltv: 80, dscr: 0.92, distressLevel: "High", conversionPotential: "Downtown Revitalization" },
  { id: "CLM023", propertyName: "Wilsonville Business Park", address: "29000 SW Town Center Loop", city: "Wilsonville", county: "Clackamas", propertyType: "Flex/Office", loanAmount: 11000000, originalLoanDate: "2024-10-31", loanMaturityDate: "2029-10-31", maturityYear: 2029, lender: "Northwest Bank", loanType: "Portfolio", interestRate: 5.00, units: 0, yearBuilt: 2007, sqft: 65000, occupancyRate: 74, capRate: 6.8, noi: 748000, ltv: 76, dscr: 1.05, distressLevel: "Moderate", conversionPotential: "Logistics Conversion" },
  { id: "CLM024", propertyName: "Astoria Waterfront Hotel", address: "1000 Marine Dr", city: "Astoria", county: "Clatsop", propertyType: "Hospitality", loanAmount: 15000000, originalLoanDate: "2024-03-31", loanMaturityDate: "2029-03-31", maturityYear: 2029, lender: "Northwest Bank", loanType: "CMBS", interestRate: 5.25, units: 95, yearBuilt: 2001, sqft: 72000, occupancyRate: 68, capRate: 7.5, noi: 1125000, ltv: 82, dscr: 0.95, distressLevel: "High", conversionPotential: "Adaptive Reuse/Waterfront Res." },
  { id: "CLM025", propertyName: "Woodburn Outlet Expansion", address: "1800 Arney Rd", city: "Woodburn", county: "Marion", propertyType: "Retail", loanAmount: 22000000, originalLoanDate: "2024-06-30", loanMaturityDate: "2029-06-30", maturityYear: 2029, lender: "MetLife", loanType: "CMBS", interestRate: 4.00, units: 0, yearBuilt: 2003, sqft: 180000, occupancyRate: 82, capRate: 6.0, noi: 1320000, ltv: 70, dscr: 1.20, distressLevel: "Moderate", conversionPotential: "N/A" },
  { id: "CLM026", propertyName: "Roseburg Healthcare Campus", address: "2500 NW Stewart Pkwy", city: "Roseburg", county: "Douglas", propertyType: "Medical Office", loanAmount: 16000000, originalLoanDate: "2025-01-15", loanMaturityDate: "2030-01-15", maturityYear: 2030, lender: "Providence Health Finance", loanType: "Healthcare Loan", interestRate: 4.00, units: 0, yearBuilt: 2014, sqft: 58000, occupancyRate: 90, capRate: 6.2, noi: 992000, ltv: 70, dscr: 1.35, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM027", propertyName: "Ontario Agricultural Complex", address: "2200 SW 4th Ave", city: "Ontario", county: "Malheur", propertyType: "Industrial/Ag", loanAmount: 5500000, originalLoanDate: "2025-05-31", loanMaturityDate: "2030-05-31", maturityYear: 2030, lender: "Farm Credit Services", loanType: "Ag Loan", interestRate: 4.75, units: 0, yearBuilt: 1995, sqft: 85000, occupancyRate: 80, capRate: 7.5, noi: 412500, ltv: 65, dscr: 1.22, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM028", propertyName: "Springfield Auto Mall", address: "3500 Gateway St", city: "Springfield", county: "Lane", propertyType: "Retail/Special Purpose", loanAmount: 12500000, originalLoanDate: "2025-08-31", loanMaturityDate: "2030-08-31", maturityYear: 2030, lender: "Bank of the West", loanType: "Portfolio", interestRate: 5.50, units: 0, yearBuilt: 2002, sqft: 95000, occupancyRate: 60, capRate: 9.0, noi: 1125000, ltv: 88, dscr: 0.82, distressLevel: "Critical", conversionPotential: "Redevelopment Site" },
  { id: "CLM029", propertyName: "Grants Pass Retail Center", address: "1200 NE 6th St", city: "Grants Pass", county: "Josephine", propertyType: "Retail", loanAmount: 6500000, originalLoanDate: "2025-09-30", loanMaturityDate: "2030-09-30", maturityYear: 2030, lender: "Umpqua Bank", loanType: "Portfolio", interestRate: 5.75, units: 0, yearBuilt: 1992, sqft: 48000, occupancyRate: 58, capRate: 9.5, noi: 617500, ltv: 90, dscr: 0.78, distressLevel: "Critical", conversionPotential: "Value Play Repositioning" },
  { id: "CLM030", propertyName: "Prineville Cloud Campus", address: "4000 SE Airport Way", city: "Prineville", county: "Crook", propertyType: "Data Center", loanAmount: 48000000, originalLoanDate: "2025-12-31", loanMaturityDate: "2030-12-31", maturityYear: 2030, lender: "Morgan Stanley", loanType: "CMBS", interestRate: 3.25, units: 0, yearBuilt: 2015, sqft: 200000, occupancyRate: 100, capRate: 4.8, noi: 2304000, ltv: 50, dscr: 1.65, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM031", propertyName: "Salem Civic Center Office", address: "500 Summer St NE", city: "Salem", county: "Marion", propertyType: "Office", loanAmount: 19500000, originalLoanDate: "2026-01-31", loanMaturityDate: "2031-01-31", maturityYear: 2031, lender: "KeyBank", loanType: "CMBS", interestRate: 5.00, units: 0, yearBuilt: 2000, sqft: 88000, occupancyRate: 70, capRate: 6.8, noi: 1326000, ltv: 76, dscr: 1.05, distressLevel: "Moderate", conversionPotential: "Government/Medical Office" },
  { id: "CLM032", propertyName: "Portland Harbor Industrial", address: "7700 NE Dock St", city: "Portland", county: "Multnomah", propertyType: "Industrial", loanAmount: 38000000, originalLoanDate: "2026-03-31", loanMaturityDate: "2031-03-31", maturityYear: 2031, lender: "Wells Fargo", loanType: "CMBS", interestRate: 4.50, units: 0, yearBuilt: 2010, sqft: 250000, occupancyRate: 92, capRate: 5.5, noi: 2090000, ltv: 60, dscr: 1.45, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM033", propertyName: "Eugene University District", address: "1500 University St", city: "Eugene", county: "Lane", propertyType: "Mixed-Use", loanAmount: 27000000, originalLoanDate: "2026-06-30", loanMaturityDate: "2031-06-30", maturityYear: 2031, lender: "Umpqua Bank", loanType: "Construction-to-Perm", interestRate: 4.25, units: 120, yearBuilt: 2020, sqft: 145000, occupancyRate: 88, capRate: 5.0, noi: 1350000, ltv: 72, dscr: 1.25, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM034", propertyName: "Bend Old Mill District", address: "650 SW Century Dr", city: "Bend", county: "Deschutes", propertyType: "Retail/Mixed-Use", loanAmount: 31000000, originalLoanDate: "2026-09-30", loanMaturityDate: "2031-09-30", maturityYear: 2031, lender: "Columbia Bank", loanType: "Portfolio", interestRate: 4.75, units: 0, yearBuilt: 2012, sqft: 165000, occupancyRate: 85, capRate: 5.5, noi: 1705000, ltv: 68, dscr: 1.30, distressLevel: "Low", conversionPotential: "N/A" },
  { id: "CLM035", propertyName: "Medford Distribution Hub", address: "4200 Crater Lake Hwy", city: "Medford", county: "Jackson", propertyType: "Industrial/Warehouse", loanAmount: 14000000, originalLoanDate: "2026-08-31", loanMaturityDate: "2031-08-31", maturityYear: 2031, lender: "Banner Bank", loanType: "Bridge", interestRate: 5.50, units: 0, yearBuilt: 2019, sqft: 110000, occupancyRate: 90, capRate: 6.2, noi: 868000, ltv: 65, dscr: 1.32, distressLevel: "Low", conversionPotential: "N/A" },
];

export const commercialLoanMaturities: CommercialLoanMaturity[] = rawData.map(p => {
  const days = calcDays(p.loanMaturityDate);
  return {
    ...p,
    daysUntilMaturity: days,
    investmentScore: calcScore({ loanAmount: p.loanAmount, distressLevel: p.distressLevel, ltv: p.ltv, occupancyRate: p.occupancyRate, daysUntilMaturity: days }),
    leadStatus: 'New' as const,
    notes: '',
  };
});

export const getUniquePropertyTypes = (): string[] => [...new Set(commercialLoanMaturities.map(p => p.propertyType))].sort();
export const getUniqueLenders = (): string[] => [...new Set(commercialLoanMaturities.map(p => p.lender))].sort();
export const getMaturityYears = (): number[] => [...new Set(commercialLoanMaturities.map(p => p.maturityYear))].sort();
export const getUniqueLoanTypes = (): string[] => [...new Set(commercialLoanMaturities.map(p => p.loanType))].sort();
