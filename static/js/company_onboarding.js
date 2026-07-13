document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('company-onboarding-form');
  const companyNameInput = document.getElementById('company-name-input');
  const submitButton = document.getElementById('btn-company-submit');

  if (!form || !companyNameInput || !submitButton) {
    return;
  }

  function updateSubmitButton() {
    submitButton.disabled = companyNameInput.value.trim().length === 0;
  }

  companyNameInput.addEventListener('input', updateSubmitButton);

  form.addEventListener('submit', function (event) {
    if (!companyNameInput.value.trim()) {
      event.preventDefault();
      submitButton.disabled = true;
      companyNameInput.focus();
    }
  });

  updateSubmitButton();
});
