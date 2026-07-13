const companyNameInput = document.getElementById("company-name-input");
const companySubmitButton = document.getElementById("btn-company-submit");

function updateCompanySubmitButton() {
  companySubmitButton.disabled = !companyNameInput.value.trim();
}

companyNameInput.addEventListener("input", updateCompanySubmitButton);
updateCompanySubmitButton();
