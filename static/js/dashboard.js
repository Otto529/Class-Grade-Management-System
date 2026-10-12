function openExamModal(e) {
  document.getElementById('examModalTitle').textContent = e ? '编辑考试资料' : '新增考试';
  document.getElementById('e_id').value = e ? e.id : '';
  document.getElementById('e_name').value = e ? e.name : '';
  document.getElementById('e_date').value = e && e.exam_date ? String(e.exam_date).slice(0, 10) : '';
  document.getElementById('e_remark').value = e ? (e.remark || '') : '';
  document.getElementById('examModal').classList.add('show');
}

function closeExamModal() {
  document.getElementById('examModal').classList.remove('show');
}

async function saveExam() {
  const payload = {
    id: document.getElementById('e_id').value || null,
    name: document.getElementById('e_name').value.trim(),
    exam_date: document.getElementById('e_date').value,
    remark: document.getElementById('e_remark').value.trim()
  };
  if (!payload.name) { toast('请填写考试名称', 'err'); return; }
  const r = await postJSON('/api/exams/save', payload);
  if (r.ok) {
    toast(payload.id ? '考试资料已更新' : '考试已新增');
    closeExamModal();
    setTimeout(() => location.reload(), 600);
  } else {
    toast(r.msg || '保存失败', 'err');
  }
}
