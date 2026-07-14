const openBtn = document.querySelector(".openModalBtn");
const closeBtn = document.querySelectorAll(".closeModalBtn");
const modal = document.getElementById("modal");

openBtn.addEventListener("click", () => {
  modal.classList.remove("hidden");
});

closeBtn.forEach((btn) => {
  btn.addEventListener("click", () => {
    modal.classList.add("hidden");
  });
});
// 배경(오버레이) 클릭하면 닫기
modal.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.classList.add("hidden");
  }
});
