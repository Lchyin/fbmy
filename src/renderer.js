const actions = {
  back: () => window.fbmy.back(),
  forward: () => window.fbmy.forward(),
  home: () => window.fbmy.goHome(),
  reload: () => window.fbmy.reload(),
  fit: () => window.fbmy.fitWorkArea(),
  minimize: () => window.fbmy.minimize(),
  close: () => window.fbmy.close(),
};

const topButton = document.querySelector('#topButton');
const opacityRange = document.querySelector('#opacityRange');
const clickThrough = document.querySelector('#clickThrough');
const toolbar = document.querySelector('#toolbar');
let autoHideEnabled = true;

document.querySelectorAll('[data-action]').forEach((button) => {
  button.addEventListener('click', async () => {
    const action = button.dataset.action;
    if (action === 'top') {
      const enabled = await window.fbmy.toggleTop();
      topButton.classList.toggle('active', enabled);
      topButton.textContent = enabled ? '已置顶' : '置顶';
      return;
    }

    actions[action]?.();
  });
});

opacityRange.addEventListener('input', (event) => {
  window.fbmy.setOpacity(event.target.value);
});

clickThrough.addEventListener('change', async (event) => {
  autoHideEnabled = !event.target.checked;
  await window.fbmy.setClickThrough(event.target.checked);
});

toolbar.addEventListener('mouseenter', () => {
  if (autoHideEnabled) window.fbmy.mouseEntered();
});

document.body.addEventListener('mouseleave', () => {
  if (autoHideEnabled) window.fbmy.mouseLeft();
});
