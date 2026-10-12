function closeModal(id) { document.getElementById(id).classList.remove('show'); }

function openStuModal(s) {
  document.getElementById('stuModalTitle').textContent = s ? '编辑学生' : '新增学生';
  document.getElementById('f_id').value = s ? s.id : '';
  document.getElementById('f_no').value = s ? s.student_no : '';
  document.getElementById('f_name').value = s ? s.name : '';
  document.getElementById('f_gender').value = s ? s.gender : '男';
  document.getElementById('f_class').value = s ? s.class_id : '';
  document.getElementById('stuModal').classList.add('show');
}
function openClassModal() { document.getElementById('classModal').classList.add('show'); }

async function saveStu() {
  const payload = {
    id: document.getElementById('f_id').value || null,
    student_no: document.getElementById('f_no').value.trim(),
    name: document.getElementById('f_name').value.trim(),
    gender: document.getElementById('f_gender').value,
    class_id: document.getElementById('f_class').value
  };
  if (!payload.student_no || !payload.name) { toast('学号和姓名不能为空', 'err'); return; }
  const r = await postJSON('/api/students/save', payload);
  if (r.ok) { toast('保存成功'); closeModal('stuModal'); setTimeout(() => location.reload(), 600); }
  else toast(r.msg, 'err');
}

async function delStu(id) {
  if (!confirm('确定删除该学生？其历史成绩也将一并删除。')) return;
  const r = await postJSON('/api/students/delete', { id });
  if (r.ok) { toast('已删除'); setTimeout(() => location.reload(), 600); }
}

async function addClass() {
  const class_name = document.getElementById('cf_name').value.trim();
  const grade = document.getElementById('cf_grade').value.trim();
  if (!class_name) { toast('请填写班级名称', 'err'); return; }
  const r = await postJSON('/api/classes/save', { class_name, grade });
  if (r.ok) { toast('已添加'); setTimeout(() => location.reload(), 600); }
}

async function delClass(id) {
  if (!confirm('确定删除该班级？')) return;
  const r = await postJSON('/api/classes/delete', { id });
  if (r.ok) { toast('已删除'); setTimeout(() => location.reload(), 600); }
  else toast(r.msg, 'err');
}

async function doImport(input, url) {
  if (!input.files[0]) return;
  const r = await uploadExcel(url, input.files[0]);
  showImportResult(r, '成功导入学生');
  input.value = '';
  setTimeout(() => location.reload(), 1500);
}
