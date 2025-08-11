document.addEventListener('DOMContentLoaded', () => {
  const year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();

  const form = document.getElementById('contact-form');
  const toast = document.getElementById('form-toast');

  async function submitForm(event){
    event.preventDefault();
    if (!form) return;

    const data = Object.fromEntries(new FormData(form).entries());
    const button = form.querySelector('button[type="submit"]');

    try{
      button && (button.disabled = true);
      toast && (toast.textContent = '发送中...');

      const res = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      const json = await res.json().catch(() => ({}));

      if (!res.ok || !json.ok){
        const msg = (json && (json.error || json.message)) || '发送失败，请稍后重试';
        throw new Error(msg);
      }

      toast && (toast.className = 'toast success');
      toast && (toast.textContent = '发送成功，我们会尽快联系您！');
      form.reset();
    }catch(err){
      toast && (toast.className = 'toast error');
      toast && (toast.textContent = err.message || '发送失败，请稍后重试');
    }finally{
      button && (button.disabled = false);
    }
  }

  form && form.addEventListener('submit', submitForm);

  // Modal logic for the secret question
  const modalElement = document.getElementById('secretModal');
  const answerInput = document.getElementById('secretAnswer');
  const submitBtn = document.getElementById('secretSubmit');

  if (modalElement && typeof bootstrap !== 'undefined'){
    const modal = new bootstrap.Modal(modalElement);

    // Focus input when modal shown
    modalElement.addEventListener('shown.bs.modal', () => {
      answerInput && answerInput.focus();
    });

    function handleSecretSubmit(){
      const value = (answerInput && answerInput.value || '').trim();
      if (value === '2'){
        window.location.href = '/insider';
      }else{
        alert('不是自己人，再见！');
        modal.hide();
        if (answerInput) answerInput.value = '';
      }
    }

    submitBtn && submitBtn.addEventListener('click', handleSecretSubmit);
    answerInput && answerInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter'){
        e.preventDefault();
        handleSecretSubmit();
      }
    });
  }
}); 