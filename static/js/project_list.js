const projectCard = document.querySelectorAll(".project-card");
const moreButton = document.querySelector(".more-button");

let visibleCount = 6;
let projectArr = Array.from(projectCard);

const viewMoreCards = () => {
  projectArr.forEach((card, index) => {
    card.classList.toggle("is-hidden", index >= visibleCount);
  });
};

moreButton.addEventListener("click", () => {
  visibleCount += 6;
  viewMoreCards();
});

viewMoreCards();
