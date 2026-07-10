// 탭 네비게이션 설정
const tabBtns = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    const target = btn.dataset.tab; // profile, apply, offer, condition

    // 모든 버튼의 active 해제
    tabBtns.forEach((b) => b.classList.remove("active"));
    // 클릭한 버튼 active 설정
    btn.classList.add("active");

    // 모든 탭 active 해제
    tabContents.forEach((content) => content.classList.remove("active"));
    // 클릭한 메뉴의 탭 active 설정
    const targetContent = document.getElementById(`tab-${target}`);
    targetContent.classList.add("active");
  });
});
