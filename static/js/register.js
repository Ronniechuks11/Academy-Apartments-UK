// ===== Prefill confirmation banner =====
// The server already pre-selects the right <option> based on ?type= — this
// just adds a friendly confirmation line above the form when that happened.
(function prefillBanner() {
  const params = new URLSearchParams(window.location.search);
  const type = params.get('type');
  const select = document.getElementById('apartmentType');
  if (!type || !select) return;

  const selectedOption = select.options[select.selectedIndex];
  if (!selectedOption) return;

  const banner = document.createElement('p');
  banner.className = 'reg-prefill-note';
  banner.textContent = `You're registering interest in: ${selectedOption.text}`;
  const fields = document.getElementById('regFields');
  if (fields) fields.prepend(banner);
})();

// ===== Client-side validation =====
// This is a first pass for instant feedback. The server (app.py) validates
// again on submit regardless, so this never has to be the only line of defense.
const regForm = document.getElementById('regForm');

if (regForm) {
  regForm.addEventListener('submit', (e) => {
    let valid = true;

    const nameInput = document.getElementById('fullName');
    const nameField = nameInput.closest('.field');
    if (!nameInput.value.trim()) {
      nameField.classList.add('has-error');
      valid = false;
    } else {
      nameField.classList.remove('has-error');
    }

    const emailInput = document.getElementById('email');
    const emailField = emailInput.closest('.field');
    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
    if (!emailValid) {
      emailField.classList.add('has-error');
      valid = false;
    } else {
      emailField.classList.remove('has-error');
    }

    if (!valid) e.preventDefault(); // let a valid form actually submit to the server
  });
}
