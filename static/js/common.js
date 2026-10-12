// 几个页面都会用到的小函数，统一放这
function toast(msg, type = 'ok', ms = 2200) {
  const box = document.getElementById('toast');
  const el = document.createElement('div');
  el.className = `toast-item ${type}`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(() => el.remove(), ms);
}

async function postJSON(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return res.json();
}

async function getJSON(url) {
  const res = await fetch(url);
  return res.json();
}

// 传 excel 用的，extraFields 是顺带带上的字段
async function uploadExcel(url, file, extraFields = {}) {
  const fd = new FormData();
  fd.append('file', file);
  Object.entries(extraFields).forEach(([k, v]) => fd.append(k, v));
  const res = await fetch(url, { method: 'POST', body: fd });
  return res.json();
}

function showImportResult(r, okText) {
  if (!r.ok) { toast(r.msg || '导入失败', 'err'); return; }
  let msg = `${okText} ${r.count} 条`;
  toast(msg, r.errors && r.errors.length ? 'info' : 'ok', 3500);
  if (r.errors && r.errors.length) {
    alert('以下数据未导入：\n' + r.errors.slice(0, 50).join('\n') +
      (r.errors.length > 50 ? `\n...共${r.errors.length}条` : ''));
  }
}
