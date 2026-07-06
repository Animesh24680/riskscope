export function downloadBlob(content, filename, mimeType = 'text/csv') {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

export function exportPredictionsToCsv(results) {
    const headers = ['Is_Delinquent', 'Risk_Probability', 'Confidence', 'Top_Factor', 'Method'];
    const rows = results.map(r => [
        r.is_delinquent, r.risk_probability,
        r.confidence, r.shap_explanation?.top_factor || '',
        r.method || 'ml_model'
    ].join(','));
    const csv = headers.join(',') + '\n' + rows.join('\n');
    downloadBlob(csv, `predictions_${new Date().toISOString().slice(0,10)}.csv`);
}
