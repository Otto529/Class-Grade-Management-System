function reload() {
  const e = document.getElementById('examSel').value;
  const c = document.getElementById('classSel').value;
  location.href = `/scores?exam_id=${e}&class_id=${c}`;
}

function openExamModal() { document.getElementById('examModal').classList.add('show'); }
function closeExamModal() { document.getElementById('examModal').classList.remove('show'); }

async function createExam() {
  const name = document.getElementById('e_name').value.trim();
  if (!name) { toast('请填写考试名称', 'err'); return; }
  const r = await postJSON('/api/exams/save', {
    name,
    exam_date: document.getElementById('e_date').value,
    remark: document.getElementById('e_remark').value
  });
  if (r.ok) { toast('考试已创建'); setTimeout(() => location.reload(), 600); }
}

async function saveAll() {
  const exam_id = document.getElementById('examSel').value;
  const items = [];
  document.querySelectorAll('tbody tr[data-student]').forEach(tr => {
    const rows = [];
    tr.querySelectorAll('input[data-subject]').forEach(inp => {
      rows.push({ subject_id: inp.dataset.subject, score: inp.value === '' ? null : inp.value });
    });
    items.push({ student_id: tr.dataset.student, rows });
  });
  const r = await postJSON('/api/scores/save', { exam_id, items });
  if (r.ok) toast(`保存成功，共写入 ${r.count} 条成绩`);
  else toast(r.msg || '保存失败', 'err');
}

async function importScore(input) {
  if (!input.files[0]) return;
  const exam_id = document.getElementById('examSel').value;
  const r = await uploadExcel('/import/scores', input.files[0], { exam_id });
  showImportResult(r, '成功导入成绩');
  input.value = '';
  setTimeout(() => location.reload(), 1500);
}
