document.addEventListener("DOMContentLoaded", () => {
  const projectNameInput =
    document.getElementById("project-name");

  const projectDetailTextarea =
    document.getElementById("project-detail");

  const submitButton =
    document.querySelector(".create-project-btn");

  const projectEditForm =
    document.getElementById("project-create-form");

  function validateEditForm() {
    if (
      !projectNameInput ||
      !projectDetailTextarea ||
      !submitButton
    ) {
      return;
    }

    const titleFilled =
      projectNameInput.value.trim() !== "";

    const descriptionFilled =
      projectDetailTextarea.value.trim() !== "";

    submitButton.disabled = !(
      titleFilled &&
      descriptionFilled
    );
  }

  projectNameInput?.addEventListener(
    "input",
    validateEditForm,
  );

  projectDetailTextarea?.addEventListener(
    "input",
    validateEditForm,
  );

  projectEditForm?.addEventListener(
    "submit",
    (event) => {
      const title =
        projectNameInput?.value.trim() || "";

      const description =
        projectDetailTextarea?.value.trim() || "";

      if (!title || !description) {
        event.preventDefault();
        validateEditForm();
      }
    },
  );

  // 기존 제목과 상세 내용이 채워져 있으므로
  // 페이지 로드 시 활성화 여부를 한 번 검사
  validateEditForm();
});
