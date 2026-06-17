// Navigation
document.querySelectorAll('.nav-btn[data-page]').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        const page = document.getElementById(`page-${btn.dataset.page}`);
        if (page) page.classList.add('active');
        if (btn.dataset.page === 'dashboard') loadDashboard();
    });
});

// Theme Toggle
const themeToggle = document.getElementById('themeToggle');
const html = document.documentElement;
const savedTheme = localStorage.getItem('theme') || 'dark';
html.setAttribute('data-theme', savedTheme);

themeToggle.addEventListener('click', () => {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
});

// Toast
showToast('Welcome! Enter customer data to get started.', 'info', 4000);

// ─── PREDICT PAGE ───────────────────────────────────────────────
const form = document.getElementById('riskForm');
const assessBtn = document.getElementById('assessBtn');
const btnText = assessBtn.querySelector('.btn-text');
const btnSpinner = assessBtn.querySelector('.btn-spinner');
const resultBox = document.getElementById('resultBox');
const resultIcon = document.getElementById('resultIcon');
const resultText = document.getElementById('resultText');
const resultMessage = document.getElementById('resultMessage');
const shapExplanation = document.getElementById('shapExplanation');
const shapBars = document.getElementById('shapBars');

const FIELD_RULES = {
    age: { min: 18, max: 119, label: 'Age' },
    income: { min: 1, max: null, label: 'Income' },
    creditScore: { min: 300, max: 850, label: 'Credit Score' },
    missedPayments: { min: 0, max: null, label: 'Missed Payments' },
    debtToIncomeRatio: { min: 0, max: 1, label: 'DTI Ratio' },
};

function validateField(id) {
    const el = document.getElementById(id);
    const errorEl = document.getElementById(`${id}-error`);
    const val = parseFloat(el.value);
    const rules = FIELD_RULES[id];

    if (!el.value || isNaN(val)) {
        errorEl.textContent = 'Required';
        el.classList.add('error');
        return false;
    }
    if (rules.min !== null && val < rules.min) {
        errorEl.textContent = `Minimum ${rules.min}`;
        el.classList.add('error');
        return false;
    }
    if (rules.max !== null && val > rules.max) {
        errorEl.textContent = `Maximum ${rules.max}`;
        el.classList.add('error');
        return false;
    }
    errorEl.textContent = '';
    el.classList.remove('error');
    return true;
}

Object.keys(FIELD_RULES).forEach(id => {
    const el = document.getElementById(id);
    el.addEventListener('blur', () => validateField(id));
    el.addEventListener('input', () => {
        if (el.classList.contains('error')) validateField(id);
    });
});

form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const valid = Object.keys(FIELD_RULES).every(id => validateField(id));
    if (!valid) {
        showToast('Please fix the errors in the form.', 'error');
        return;
    }

    const data = {
        age: parseFloat(document.getElementById('age').value),
        income: parseFloat(document.getElementById('income').value),
        credit_score: parseFloat(document.getElementById('creditScore').value),
        missed_payments: parseInt(document.getElementById('missedPayments').value),
        debt_to_income_ratio: parseFloat(document.getElementById('debtToIncomeRatio').value),
    };

    assessBtn.disabled = true;
    btnText.textContent = 'Analyzing...';
    btnSpinner.classList.remove('hidden');

    try {
        const result = await api.predict(data);
        updatePredictionResult(result);
        showToast('Prediction complete!', 'success');
    } catch (err) {
        showToast(`Prediction failed: ${err.message}`, 'error');
    } finally {
        assessBtn.disabled = false;
        btnText.textContent = 'Assess Risk';
        btnSpinner.classList.add('hidden');
    }
});

function updatePredictionResult(result) {
    resultBox.classList.remove('high-risk', 'low-risk');
    resultBox.classList.add('visible');

    if (result.is_delinquent) {
        resultBox.classList.add('high-risk');
        resultIcon.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="60" height="60"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
        resultText.textContent = 'High Risk';
    } else {
        resultBox.classList.add('low-risk');
        resultIcon.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="60" height="60"><path d="M22 11.08V12a10 10 0 1 1-5.93-8.64"/><path d="M22 4L12 14.01l-3-3"/></svg>`;
        resultText.textContent = 'Low Risk';
    }

    const pct = (result.risk_probability * 100).toFixed(1);
    resultMessage.textContent = `${result.message} | Risk: ${pct}%`;

    // SHAP Explanation
    if (result.shap_explanation && result.shap_explanation.contributions) {
        shapExplanation.classList.remove('hidden');
        shapBars.innerHTML = '<h3>Why this prediction?</h3>';
        const contribs = result.shap_explanation.contributions;
        const maxAbs = Math.max(...Object.values(contribs).map(Math.abs), 0.01);

        Object.entries(contribs).forEach(([feature, value]) => {
            const bar = document.createElement('div');
            bar.className = 'shap-bar';
            const isPos = value >= 0;
            const pctWidth = Math.abs(value) / maxAbs * 100;

            bar.innerHTML = `
                <span class="shap-bar-label">${feature}</span>
                <div class="shap-bar-track">
                    <div class="shap-bar-fill ${isPos ? 'positive' : 'negative'}" style="width:${pctWidth}%"></div>
                </div>
                <span class="shap-bar-value">${isPos ? '+' : ''}${value.toFixed(4)}</span>
            `;
            shapBars.appendChild(bar);
        });
    } else {
        shapExplanation.classList.add('hidden');
    }
}

// ─── BATCH UPLOAD PAGE ──────────────────────────────────────────
const uploadArea = document.getElementById('uploadArea');
const csvFileInput = document.getElementById('csvFile');
const browseLink = document.getElementById('browseLink');
const batchResults = document.getElementById('batchResults');
const batchTableBody = document.getElementById('batchTableBody');
const batchSummary = document.getElementById('batchSummary');
const exportCsvBtn = document.getElementById('exportCsvBtn');
let lastBatchResults = [];

function openFilePicker(e) {
    if (e) e.stopPropagation();
    csvFileInput.click();
}

uploadArea.addEventListener('click', openFilePicker);
if (browseLink) browseLink.addEventListener('click', openFilePicker);

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    e.stopPropagation();
    uploadArea.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) handleBatchFile(file);
});

csvFileInput.addEventListener('change', () => {
    const file = csvFileInput.files[0];
    csvFileInput.value = '';
    if (file) handleBatchFile(file);
});

async function handleBatchFile(file) {
    const isCsv = file.name.endsWith('.csv') || file.type === 'text/csv' || file.type === 'text/plain';
    if (!isCsv) {
        showToast('Please upload a CSV file.', 'error');
        return;
    }

    showToast(`Processing ${file.name}...`, 'info');

    try {
        const data = await api.predictBatch(file);
        displayBatchResults(data);
        showToast(`Processed ${data.count} records!`, 'success');
    } catch (err) {
        showToast(`Batch failed: ${err.message}`, 'error');
    }
}

function displayBatchResults(data) {
    lastBatchResults = data.results || [];
    batchResults.classList.remove('hidden');

    let highCount = 0;
    batchTableBody.innerHTML = '';

    data.results.forEach((r, i) => {
        if (r.is_delinquent) highCount++;
        const pct = (r.risk_probability * 100).toFixed(1);
        const tr = document.createElement('tr');
        tr.innerHTML = [
            `<td>${i + 1}</td>`,
            `<td><span class="risk-badge ${r.is_delinquent ? 'high' : 'low'}">${r.is_delinquent ? 'HIGH' : 'LOW'}</span></td>`,
            `<td>${pct}%</td>`,
            `<td>${r.shap_explanation?.top_factor || '--'}</td>`,
        ].join('');
        batchTableBody.appendChild(tr);
    });

    batchSummary.innerHTML = [
        '<div class="stat">Total: <strong>' + data.count + '</strong></div>',
        '<div class="stat" style="color:var(--danger)">High Risk: <strong>' + highCount + '</strong></div>',
        '<div class="stat" style="color:var(--success)">Low Risk: <strong>' + (data.count - highCount) + '</strong></div>',
    ].join('');
}

exportCsvBtn.addEventListener('click', () => {
    if (lastBatchResults.length) {
        exportPredictionsToCsv(lastBatchResults);
        showToast('CSV exported!', 'success');
    }
});

// ─── DASHBOARD PAGE ─────────────────────────────────────────────
let riskChart = null;
let trendChart = null;

async function loadDashboard() {
    try {
        const [stats, history] = await Promise.all([
            api.dashboard.stats(),
            api.dashboard.history(50),
        ]);

        document.getElementById('statTotal').textContent = stats.total_predictions;
        document.getElementById('statHighRisk').textContent = stats.high_risk_count;
        document.getElementById('statRiskPct').textContent = `${stats.high_risk_pct}%`;

        const statusRes = await api.train.status();
        document.getElementById('statModelStatus').textContent = statusRes.is_trained ? 'Active' : 'Not Trained';
        document.getElementById('statModelStatus').style.color = statusRes.is_trained ? 'var(--success)' : 'var(--danger)';

        // Pie chart
        const pieCtx = document.getElementById('riskPieChart').getContext('2d');
        if (riskChart) riskChart.destroy();
        riskChart = new Chart(pieCtx, {
            type: 'doughnut',
            data: {
                labels: ['Low Risk', 'High Risk'],
                datasets: [{
                    data: [
                        stats.total_predictions - stats.high_risk_count,
                        stats.high_risk_count,
                    ],
                    backgroundColor: ['rgba(56,189,248,0.6)', 'rgba(252,165,165,0.6)'],
                    borderColor: ['#38bdf8', '#fca5a5'],
                    borderWidth: 2,
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom', labels: { color: getComputedStyle(document.documentElement).getPropertyValue('--text') } }
                }
            }
        });

        // Trend chart
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        if (trendChart) trendChart.destroy();
        const sorted = [...history].reverse();
        trendChart = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: sorted.map((_, i) => i + 1),
                datasets: [{
                    label: 'Risk Probability',
                    data: sorted.map(r => r.risk_probability * 100),
                    borderColor: '#e94560',
                    backgroundColor: 'rgba(233,69,96,0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 3,
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                },
                plugins: {
                    legend: { labels: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary') } }
                }
            }
        });

        // History table
        const tbody = document.getElementById('historyTableBody');
        tbody.innerHTML = '';
        history.slice(0, 20).forEach(r => {
            const pct = (r.risk_probability * 100).toFixed(1);
            const date = new Date(r.created_at).toLocaleDateString();
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${date}</td>
                <td>${r.age}</td>
                <td>${r.credit_score}</td>
                <td><span class="risk-badge ${r.is_delinquent ? 'high' : 'low'}">${r.is_delinquent ? 'HIGH' : 'LOW'}</span></td>
                <td>${pct}%</td>
                <td>${r.top_risk_factor || '--'}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        showToast(`Failed to load dashboard: ${err.message}`, 'error');
    }
}

document.getElementById('exportHistoryBtn').addEventListener('click', async () => {
    try {
        const response = await api.dashboard.export();
        const csv = await response.text();
        downloadBlob(csv, `prediction_history_${new Date().toISOString().slice(0,10)}.csv`);
        showToast('History exported!', 'success');
    } catch (err) {
        showToast(`Export failed: ${err.message}`, 'error');
    }
});

// ─── WHAT-IF ANALYSIS ───────────────────────────────────────────
const WI_FIELDS = [
    { id: 'wiAgeSlider', display: 'wiAge', field: 'age', decimals: 0 },
    { id: 'wiIncomeSlider', display: 'wiIncome', field: 'income', decimals: 0 },
    { id: 'wiCreditScoreSlider', display: 'wiCreditScore', field: 'credit_score', decimals: 0 },
    { id: 'wiMissedPaymentsSlider', display: 'wiMissedPayments', field: 'missed_payments', decimals: 0 },
    { id: 'wiDTISlider', display: 'wiDTI', field: 'debt_to_income_ratio', decimals: 2 },
];

let whatIfTimeout;

WI_FIELDS.forEach(({ id, display, field, decimals }) => {
    const slider = document.getElementById(id);
    const displayEl = document.getElementById(display);
    slider.addEventListener('input', () => {
        const val = parseFloat(slider.value);
        displayEl.textContent = decimals === 0 ? val : val.toFixed(decimals);
        clearTimeout(whatIfTimeout);
        whatIfTimeout = setTimeout(runWhatIf, 300);
    });
});

async function runWhatIf() {
    const data = {};
    WI_FIELDS.forEach(({ id, field }) => {
        data[field] = parseFloat(document.getElementById(id).value);
    });

    try {
        const result = await api.predict(data);
        updateWhatIfResult(result);
    } catch {
        // Silently fail on what-if
    }
}

function updateWhatIfResult(result) {
    const pct = (result.risk_probability * 100).toFixed(1);
    const fill = document.getElementById('wiGaugeFill');
    const riskText = document.getElementById('wiRiskText');
    const probText = document.getElementById('wiProbability');
    const shapBox = document.getElementById('wiShapBars');

    const deg = result.risk_probability * 180;
    fill.textContent = `${pct}%`;
    riskText.textContent = result.is_delinquent ? 'High Risk' : 'Low Risk';
    riskText.style.color = result.is_delinquent ? 'var(--danger)' : 'var(--success)';
    probText.textContent = `Probability: ${pct}%`;

    // SHAP
    if (result.shap_explanation?.contributions) {
        shapBox.innerHTML = '<h3>Feature Contributions</h3>';
        const contribs = result.shap_explanation.contributions;
        const maxAbs = Math.max(...Object.values(contribs).map(Math.abs), 0.01);

        Object.entries(contribs).forEach(([feature, value]) => {
            const bar = document.createElement('div');
            bar.className = 'shap-bar';
            const isPos = value >= 0;
            const pctWidth = Math.abs(value) / maxAbs * 100;
            bar.innerHTML = `
                <span class="shap-bar-label">${feature}</span>
                <div class="shap-bar-track">
                    <div class="shap-bar-fill ${isPos ? 'positive' : 'negative'}" style="width:${pctWidth}%"></div>
                </div>
                <span class="shap-bar-value">${isPos ? '+' : ''}${value.toFixed(4)}</span>
            `;
            shapBox.appendChild(bar);
        });
    }
}

// Initial what-if load
setTimeout(runWhatIf, 500);
