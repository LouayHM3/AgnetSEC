const $ = (selector) => document.querySelector(selector);

function renderStats(data) {
  $('#metric-total').textContent = data.total_scans;
  $('#metric-score').textContent = data.total_scans ? `${data.average_score}` : '--';
  $('#signal-score').textContent = data.total_scans ? Math.round(data.average_score) : '--';
  $('#signal-total').textContent = `${data.total_scans} completed audit${data.total_scans === 1 ? '' : 's'}`;
}

async function refreshDashboard() {
  const [stats, history] = await Promise.all([fetch('/api/stats').then((r) => r.json()), fetch('/api/history').then((r) => r.json())]);
  renderStats(stats);
  $('#history-body').innerHTML = history.length ? history.map((item) => `<tr><td class="target-cell">${item.target}</td><td>${new Date(item.created_at + 'Z').toLocaleString()}</td><td>${item.score}/100</td><td class="risk-cell">${item.risk}</td></tr>`).join('') : '<tr><td colspan="4" class="empty-cell">No completed audits yet.</td></tr>';
}

function addLogs(messages) {
  const log = $('#activity-log');
  if (log.querySelector('.empty-state')) log.innerHTML = '';
  messages.forEach((message) => { const line = document.createElement('div'); line.className = 'log-entry'; line.textContent = message; log.appendChild(line); log.scrollTop = log.scrollHeight; });
}

function renderResult(result) {
  $('#risk-badge').textContent = result.risk;
  $('#risk-badge').style.color = result.risk === 'LOW' ? 'var(--green)' : 'var(--orange)';
  $('#results-content').innerHTML = `<div class="results-layout"><div><div class="result-score">${result.score}</div><div class="signal-caption">security score / 100</div></div><div><p class="result-summary">${result.summary}</p><div>${result.findings.map((finding) => `<div class="finding"><div><span class="finding-title">${finding.title}</span><span class="finding-evidence">${finding.tool} · ${finding.evidence}</span></div><span class="severity">${finding.severity.toUpperCase()}</span></div>`).join('')}</div></div></div>`;
}

$('#scan-form').addEventListener('submit', async (event) => {
  event.preventDefault();
  const form = new FormData(event.target);
  const response = await fetch('/api/scans', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(Object.fromEntries(form)) });
  if (!response.ok) return;
  const { scan_id: scanId } = await response.json();
  $('#run-status').textContent = 'RUNNING';
  $('#run-status').style.color = 'var(--cyan)';
  $('#activity-log').innerHTML = '';
  let lastLogMessage = '';
  const poll = setInterval(async () => {
    const scan = await fetch(`/api/scans/${scanId}`).then((r) => r.json());
    $('#progress-bar').style.width = `${scan.progress || 0}%`;
    if (scan.logs) {
      const newMessages = scan.logs.filter((message) => message !== lastLogMessage);
      if (newMessages.length) {
        addLogs(newMessages);
        lastLogMessage = newMessages[newMessages.length - 1];
      }
    }
    if (scan.status === 'completed') { clearInterval(poll); $('#run-status').textContent = 'COMPLETE'; $('#run-status').style.color = 'var(--green)'; renderResult(scan.result); refreshDashboard(); }
  }, 500);
});

$('#refresh-history').addEventListener('click', refreshDashboard);
$('#today').textContent = new Date().toLocaleDateString(undefined, {month: 'short', day: '2-digit', year: 'numeric'});
refreshDashboard();
