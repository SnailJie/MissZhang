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
}); 