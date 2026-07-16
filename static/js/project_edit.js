const projectNameInput = document.getElementById("project-name");
const projectDetailTextarea = document.getElementById("project-detail");
const submitBtn = document.querySelector(".create-project-btn");

const checkValidity = () => {
  const isValid =
    projectNameInput.value.trim() !== "" &&
    projectDetailTextarea.value.trim() !== "";

  submitBtn.disabled = !isValid;
};

// 수정 화면은 기존 값이 이미 채워져 있으니, 로드 시점에 한 번 체크해서
// 버튼을 활성화 상태로 시작해야 함
checkValidity();

// 이후 사용자가 지우면 다시 비활성화
[projectNameInput, projectDetailTextarea].forEach((el) => {
  el.addEventListener("input", checkValidity);
});
