const projectNameInput =
  document.getElementById("project-name");

const projectDetailTextarea =
  document.getElementById("project-detail");

const submitBtn = document.querySelector(
  ".create-project-btn",
);

function checkValidity() {
  const isValid =
    projectNameInput.value.trim() !== "" &&
    projectDetailTextarea.value.trim() !== "";

  submitBtn.disabled = !isValid;
}

checkValidity();

projectNameInput.addEventListener(
  "input",
  checkValidity,
);

projectDetailTextarea.addEventListener(
  "input",
  checkValidity,
);

document
  .querySelectorAll(
    "input[readonly], textarea[readonly]",
  )
  .forEach((element) => {
    element.addEventListener("keydown", (event) => {
      event.preventDefault();
    });
  });
