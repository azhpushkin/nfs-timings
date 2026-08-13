document.addEventListener('click', (event) => {
  const button = event.target.closest('.api-url-open');
  if (!button) return;

  const input = document.getElementById(button.dataset.urlInput);
  if (input && input.value) {
    window.open(input.value, '_blank', 'noopener');
  }
});

function setPrefillPanelVisibility(input, visible) {
  const panel = document.getElementById(input.dataset.prefillPanel);
  if (panel) panel.hidden = !visible;
}

function filterPrefillChoices(input) {
  const panel = document.getElementById(input.dataset.prefillPanel);
  if (!panel) return;

  const query = input.value.toLowerCase();
  panel.querySelectorAll('.prefill-choice').forEach((choice) => {
    const matches = choice.textContent.toLowerCase().includes(query)
      || choice.dataset.value.toLowerCase().includes(query);
    choice.hidden = !matches;
  });
}

document.addEventListener('focusin', (event) => {
  const input = event.target.closest('.prefill-input');
  if (!input) return;
  filterPrefillChoices(input);
  setPrefillPanelVisibility(input, true);
});

document.addEventListener('input', (event) => {
  const input = event.target.closest('.prefill-input');
  if (input) filterPrefillChoices(input);
});

document.addEventListener('click', (event) => {
  const choice = event.target.closest('.prefill-choice');
  if (choice) {
    const panel = choice.closest('.prefill-panel');
    const input = document.querySelector(`[data-prefill-panel="${panel.id}"]`);
    if (input) {
      input.value = choice.dataset.value;
      input.focus();
      setPrefillPanelVisibility(input, false);
    }
    return;
  }

  if (!event.target.closest('.prefill-combobox')) {
    document.querySelectorAll('.prefill-input').forEach((input) => {
      setPrefillPanelVisibility(input, false);
    });
  }
});
