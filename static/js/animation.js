function splitChars(el, startDelay = 0, step = 0.04) {
  let delay = startDelay;

  function wrap(node) {
    if (node.nodeType === Node.TEXT_NODE) {
      const frag = document.createDocumentFragment();
      [...node.textContent].forEach((ch) => {
        if (ch.trim() === "") {
          frag.appendChild(document.createTextNode(ch));
          return;
        }
        const span = document.createElement("span");
        span.className = "char";
        span.style.animationDelay = `${delay.toFixed(2)}s`;
        span.textContent = ch;
        frag.appendChild(span);
        delay += step;
      });
      node.replaceWith(frag);
    } else if (node.nodeType === Node.ELEMENT_NODE) {
      [...node.childNodes].forEach(wrap);
    }
  }

  [...el.childNodes].forEach(wrap);
  return delay;
}

const lines = document.querySelectorAll(".brand-wrap h1");
let delay = 0.2;
lines.forEach((line) => {
  delay = splitChars(line, delay) + 0.15;
});
