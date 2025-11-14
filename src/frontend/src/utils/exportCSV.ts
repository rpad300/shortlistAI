/**
 * Utility functions for exporting data to CSV format.
 */

export const exportToCSV = (data: any[], filename: string) => {
  if (!data || data.length === 0) {
    alert('No data to export');
    return;
  }

  // Get headers from first object
  const headers = Object.keys(data[0]);
  
  // Create CSV content
  const csvContent = [
    // Header row
    headers.join(','),
    // Data rows
    ...data.map(row => 
      headers.map(header => {
        const value = row[header];
        // Handle different data types
        if (value === null || value === undefined) {
          return '';
        }
        if (typeof value === 'object') {
          return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
        }
        // Escape quotes and wrap in quotes if contains comma
        const stringValue = String(value);
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
          return `"${stringValue.replace(/"/g, '""')}"`;
        }
        return stringValue;
      }).join(',')
    )
  ].join('\n');

  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', `${filename}_${new Date().toISOString().split('T')[0]}.csv`);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

export const exportCandidatesToCSV = (candidates: any[]) => {
  const exportData = candidates.map(c => ({
    Name: c.name,
    Email: c.email,
    Phone: c.phone || '',
    Country: c.country || '',
    Consent: c.consent_given ? 'Yes' : 'No',
    'Created At': new Date(c.created_at).toISOString()
  }));
  
  exportToCSV(exportData, 'candidates');
};

export const exportAnalysesToCSV = (analyses: any[]) => {
  const exportData = analyses.map(a => ({
    Mode: a.mode,
    Provider: a.provider,
    Score: a.global_score || 'N/A',
    Language: a.language,
    'Candidate ID': a.candidate_id,
    'Job Posting ID': a.job_posting_id,
    'Created At': new Date(a.created_at).toISOString()
  }));
  
  exportToCSV(exportData, 'analyses');
};

export const exportCompaniesToCSV = (companies: any[]) => {
  const exportData = companies.map(c => ({
    Name: c.name,
    'Created At': new Date(c.created_at).toISOString(),
    'Updated At': new Date(c.updated_at).toISOString()
  }));
  
  exportToCSV(exportData, 'companies');
};

export const exportInterviewersToCSV = (interviewers: any[]) => {
  const exportData = interviewers.map(i => ({
    Name: i.name,
    Email: i.email,
    Phone: i.phone || '',
    Country: i.country || '',
    Consent: i.consent_given ? 'Yes' : 'No',
    'Created At': new Date(i.created_at).toISOString()
  }));
  
  exportToCSV(exportData, 'interviewers');
};

export const exportJobPostingsToCSV = (postings: any[]) => {
  const exportData = postings.map(p => ({
    'Job Description': p.raw_text.substring(0, 500), // Limit length
    Language: p.language || 'N/A',
    'Created At': new Date(p.created_at).toISOString()
  }));
  
  exportToCSV(exportData, 'job_postings');
};

export const exportAIUsageToCSV = (logs: any[]) => {
  const exportData = logs.map(log => ({
    Timestamp: new Date(log.created_at).toISOString(),
    Provider: log.provider,
    Mode: log.mode,
    Language: log.language,
    'Input Tokens': log.input_tokens || 0,
    'Output Tokens': log.output_tokens || 0,
    'Total Tokens': log.total_tokens || ((log.input_tokens || 0) + (log.output_tokens || 0)),
    Score: log.global_score !== undefined && log.global_score !== null 
      ? (log.global_score * 100).toFixed(1) + '%' 
      : 'N/A',
    Cost: `$${log.estimated_cost?.toFixed(6) || '0.000000'}`,
    'Candidate ID': log.candidate_id,
    'Job Posting ID': log.job_posting_id,
    'Analysis ID': log.id
  }));
  
  exportToCSV(exportData, 'ai_usage_logs');
};

