window.addEventListener("DOMContentLoaded", () => {
  // 선택 탭 메뉴에 따라 탭 표시/숨김 (모집중, 진행중, 완료)
  const params = new URLSearchParams(window.location.search);
  const initialTab = params.get("tab") || "recruiting"; // 값 없으면 기본값

  document
    .querySelectorAll(".nav-tab")
    .forEach((t) => t.classList.remove("active"));
  document
    .querySelector(`.nav-tab[data-tab="${initialTab}"]`)
    .classList.add("active");

  document.querySelectorAll(".tab-content").forEach((tab) => {
    tab.style.display = "none";
  });
  document.querySelector(`.tab-content[id="tab-${initialTab}"]`).style.display =
    "flex";

  const returnshipModal = document.getElementById("returnship-modal");
  const closeModalBtn = document.querySelector(".close-modal-btn");
  const submitBtn = document.querySelector(".submit-returnship-btn");

  const titleInput = document.getElementById("returnship-title");
  const detailTextarea = document.getElementById("returnship-detail");

  // 리턴십 제안하기 버튼 클릭 시 모달 열기
  document.querySelectorAll(".open-returnship-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      returnshipModal.style.display = "flex";
    });
  });

  // 입력할 때마다 재검사해야 disabled가 풀림
  const checkValidity = () => {
    const textFilled =
      titleInput.value.trim() !== "" && detailTextarea.value.trim() !== "";
    submitBtn.disabled = !textFilled;
  };

  [titleInput, detailTextarea].forEach((el) => {
    el.addEventListener("input", checkValidity);
  });

  // 제안 보내기 버튼 클릭 시 모달 닫기
  submitBtn.addEventListener("click", () => {
    returnshipModal.style.display = "none";
  });

  // 모달 닫기 버튼 클릭 시 모달 닫기
  closeModalBtn.addEventListener("click", () => {
    returnshipModal.style.display = "none";
  });

  // 모달 배경 클릭 시 모달 닫기
  returnshipModal.addEventListener("click", (e) => {
    if (e.target === returnshipModal) {
      returnshipModal.style.display = "none";
    }
  });
});
