// Opens gallery tiles in a full-screen viewer. Without JavaScript (or without
// <dialog> support) each tile is a normal link to its artwork page.
(() => {
  const dialog = document.querySelector("[data-lightbox]");
  const gallery = document.querySelector("[data-gallery]");
  if (!dialog || !gallery || typeof dialog.showModal !== "function") return;

  const tiles = Array.from(gallery.querySelectorAll("a.tile"));
  if (!tiles.length) return;

  const image = dialog.querySelector("[data-lightbox-image]");
  const title = dialog.querySelector("[data-lightbox-title]");
  const caption = dialog.querySelector("[data-lightbox-caption]");
  const count = dialog.querySelector("[data-lightbox-count]");
  const link = dialog.querySelector("[data-lightbox-link]");
  const prev = dialog.querySelector("[data-lightbox-prev]");
  const next = dialog.querySelector("[data-lightbox-next]");
  const close = dialog.querySelector("[data-lightbox-close]");

  let index = 0;
  let opener = null;

  if (tiles.length < 2) {
    prev.hidden = true;
    next.hidden = true;
  }

  const wrap = (i) => (i + tiles.length) % tiles.length;

  function preload(i) {
    const src = tiles[wrap(i)].dataset.large;
    if (src) new Image().src = src;
  }

  function show(i) {
    index = wrap(i);
    const tile = tiles[index];
    const thumb = tile.querySelector("img");
    image.src = tile.dataset.large || thumb.currentSrc || thumb.src;
    image.alt = thumb.alt;
    title.textContent = tile.dataset.title || "";
    caption.textContent = tile.dataset.caption || "";
    count.textContent = tiles.length > 1 ? `${index + 1} of ${tiles.length}` : "";
    link.href = tile.href;
    if (tiles.length > 1) {
      preload(index - 1);
      preload(index + 1);
    }
  }

  gallery.addEventListener("click", (event) => {
    const tile = event.target.closest("a.tile");
    if (!tile) return;
    // Let modified clicks open the artwork page in a new tab as usual.
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = tile;
    show(tiles.indexOf(tile));
    dialog.showModal();
    close.focus();
  });

  prev.addEventListener("click", () => show(index - 1));
  next.addEventListener("click", () => show(index + 1));
  close.addEventListener("click", () => dialog.close());

  dialog.addEventListener("keydown", (event) => {
    if (tiles.length < 2) return;
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      show(index - 1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      show(index + 1);
    }
  });

  // A click on the dark area around the artwork closes the viewer.
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });

  dialog.addEventListener("close", () => {
    if (opener) opener.focus();
    opener = null;
  });

  // Horizontal swipe on touch screens moves between artworks.
  let startX = null;
  let startY = null;
  image.addEventListener("pointerdown", (event) => {
    if (event.pointerType !== "touch") return;
    startX = event.clientX;
    startY = event.clientY;
  });
  image.addEventListener("pointerup", (event) => {
    if (startX === null || tiles.length < 2) return;
    const dx = event.clientX - startX;
    const dy = event.clientY - startY;
    startX = null;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) show(index + (dx < 0 ? 1 : -1));
  });
  image.addEventListener("pointercancel", () => {
    startX = null;
  });
})();
