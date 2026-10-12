let lastRows = [], lastSingle = false;

async function loadRank() {
  const p = new URLSearchParams({
    exam_id: document.getElementById('examSel').value,
    class_id: document.getElementById('classSel').value,
    subject_id: document.getElementById('subjectSel').value
  });
  lastSingle = document.getElementById('subjectSel').value !== '';
  const data = await getJSON('/api/ranking?' + p.toString());
  lastRows = data.rows;

  document.getElementById('rankHead').innerHTML = lastSingle
    ? '<tr><th>名次</th><th>学号</th><th>姓名</th><th>班级</th><th>单科成绩</th></tr>'
    : '<tr><th>名次</th><th>学号</th><th>姓名</th><th>班级</th><th>参考科目数</th><th>总分</th><th>平均分</th></tr>';

  const body = document.getElementById('rankBody');
  body.innerHTML = '';
  data.rows.forEach(r => {
    const tr = document.createElement('tr');
    const rankCls = r.rk <= 3 ? `rank-${r.rk}` : '';
    if (lastSingle) {
      tr.innerHTML = `<td class="${rankCls}">${r.rk}</td><td>${r.student_no}</td>
        <td>${r.name}</td><td><span class="tag blue">${r.class_name}</span></td>
        <td><b>${r.total}</b></td>`;
    } else {
      tr.innerHTML = `<td class="${rankCls}">${r.rk}</td><td>${r.student_no}</td>
        <td>${r.name}</td><td><span class="tag blue">${r.class_name}</span></td>
        <td>${r.subject_cnt}</td><td><b>${r.total}</b></td><td>${r.avg_score}</td>`;
    }
    body.appendChild(tr);
  });
  if (!data.rows.length) {
    body.innerHTML = '<tr><td colspan="7" class="muted">该条件下暂无成绩数据。</td></tr>';
  }
}

function exportCsv() {
  if (!lastRows.length) { toast('没有可导出的数据', 'err'); return; }
  const head = lastSingle
    ? ['名次', '学号', '姓名', '班级', '成绩']
    : ['名次', '学号', '姓名', '班级', '科目数', '总分', '平均分'];
  const lines = [head.join(',')];
  lastRows.forEach(r => {
    lines.push(lastSingle
      ? [r.rk, r.student_no, r.name, r.class_name, r.total].join(',')
      : [r.rk, r.student_no, r.name, r.class_name, r.subject_cnt, r.total, r.avg_score].join(','));
  });
  // 加 BOM，Excel 打开中文不乱码
  const blob = new Blob(['\ufeff' + lines.join('\n')], { type: 'text/csv;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = '排名导出.csv';
  a.click();
}

(function init() {
  const q = new URLSearchParams(location.search);
  if (q.get('exam_id')) document.getElementById('examSel').value = q.get('exam_id');
  loadRank();
})();
