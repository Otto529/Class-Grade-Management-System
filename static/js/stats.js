const COLORS = ['#ef5b5b', '#f0a03b', '#e8d24b', '#7bc47f', '#22b07d'];

function params() {
  return new URLSearchParams({
    exam_id: document.getElementById('examSel').value,
    class_id: document.getElementById('classSel').value
  });
}

async function loadStats() {
  const p = params();
  document.getElementById('exportBtn').href = '/export/report?' + p.toString();
  const data = await getJSON('/api/stats?' + p.toString());

  // ---- 平均分柱状图 ----
  const chart = document.getElementById('avgChart');
  chart.innerHTML = '';
  const maxFull = Math.max(...data.subjects.map(s => Number(s.full_score)), 1);
  data.subjects.forEach(s => {
    const h = (Number(s.avg_score) / maxFull) * 100;
    const col = document.createElement('div');
    col.className = 'bar-col';
    col.innerHTML = `<div class="bar" style="height:${h}%">
        <span class="bar-val">${s.avg_score}</span></div>
      <div class="bar-label">${s.name}<br>(${s.full_score})</div>`;
    chart.appendChild(col);
  });

  // ---- 分数段堆叠条 ----
  const box = document.getElementById('distBox');
  box.innerHTML = '';
  data.distribution.forEach(d => {
    const vals = [d.d0, d.d1, d.d2, d.d3, d.d4].map(Number);
    const total = vals.reduce((a, b) => a + b, 0) || 1;
    const row = document.createElement('div');
    row.style.cssText = 'display:flex;align-items:center;gap:10px;margin:10px 0';
    const bar = document.createElement('div');
    bar.style.cssText = 'flex:1;display:flex;height:22px;border-radius:4px;overflow:hidden;background:#f0f2f6';
    vals.forEach((v, i) => {
      const seg = document.createElement('div');
      seg.style.cssText = `width:${v / total * 100}%;background:${COLORS[i]};
        display:flex;align-items:center;justify-content:center;font-size:11px;color:#fff`;
      if (v > 0) seg.textContent = v;
      bar.appendChild(seg);
    });
    row.innerHTML = `<div style="width:42px" class="muted">${d.subject}</div>`;
    row.appendChild(bar);
    box.appendChild(row);
  });

  // ---- 明细表 ----
  const body = document.getElementById('statsBody');
  body.innerHTML = '';
  data.subjects.forEach(s => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${s.name}</td><td>${s.full_score}</td><td>${s.cnt}</td>
      <td><b>${s.avg_score}</b></td><td class="rank-1">${s.max_score}</td>
      <td class="muted">${s.min_score}</td>
      <td>${s.pass_rate}%</td><td>${s.excellent_rate}%</td>`;
    body.appendChild(tr);
  });
}

// 支持 URL 带 exam_id 进入
(function init() {
  const q = new URLSearchParams(location.search);
  if (q.get('exam_id')) document.getElementById('examSel').value = q.get('exam_id');
  if (q.get('class_id')) document.getElementById('classSel').value = q.get('class_id');
  loadStats();
})();
