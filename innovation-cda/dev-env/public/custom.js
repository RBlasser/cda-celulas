/**
 * Asesor Virtual de Auto - Caja de Ahorros
 * Formulario Obligatorio de Registro Previo (Pre-Chat Gate)
 */

(function () {
  "use strict";

  const STORAGE_KEY = "cda_client_registered";

  function createModal() {
    // Si ya existe en el DOM, no duplicar
    if (document.getElementById("cda-registration-overlay")) return;

    const overlay = document.createElement("div");
    overlay.id = "cda-registration-overlay";
    overlay.className = "cda-overlay";

    overlay.innerHTML = `
      <div class="cda-modal-card" role="dialog" aria-modal="true" aria-labelledby="cda-title">
        <div class="cda-modal-header">
          <div class="cda-modal-badge">🚗 Feria de Préstamos • Caja de Ahorros</div>
          <h2 id="cda-title" class="cda-modal-title">Registro de Precalificación</h2>
          <p class="cda-modal-subtitle">Ingrese sus datos para activar el <strong>Asesor Virtual de Auto</strong> y habilitar la emisión de su Pase Digital oficial.</p>
          <p class="cda-modal-desc">
            📋 Todos los campos son obligatorios para asignarle un código de turno prioritario en stand.
          </p>
        </div>

        <form id="cda-registration-form" novalidate autocomplete="on">
          <div class="cda-form-group">
            <label for="cda-reg-nombre">Nombre Completo <span class="req">*</span></label>
            <div class="cda-input-wrapper">
              <input type="text" id="cda-reg-nombre" placeholder="Ej: Juan Carlos Pérez" required autocomplete="name" />
            </div>
          </div>

          <div class="cda-form-group">
            <label for="cda-reg-cedula">Cédula de Identidad Personal <span class="req">*</span></label>
            <div class="cda-input-wrapper">
              <input type="text" id="cda-reg-cedula" placeholder="Ej: 8-765-4321 o PE-12-345" required />
            </div>
          </div>

          <div class="cda-form-group">
            <label for="cda-reg-celular">Número de Celular <span class="req">*</span></label>
            <div class="cda-input-wrapper">
              <input type="tel" id="cda-reg-celular" placeholder="Ej: 6123-4567" required autocomplete="tel" />
            </div>
          </div>

          <div class="cda-form-group">
            <label for="cda-reg-correo">Correo Electrónico <span class="req">*</span></label>
            <div class="cda-input-wrapper">
              <input type="email" id="cda-reg-correo" placeholder="Ej: juan.perez@correo.com" required autocomplete="email" />
            </div>
          </div>

          <div id="cda-form-error" class="cda-form-error"></div>

          <div class="cda-form-security">
            <span>🔒</span>
            <span>Sus datos están protegidos y serán utilizados únicamente para su asesoría crediticia y cotización de feria por Caja de Ahorros.</span>
          </div>

          <button type="submit" id="cda-btn-submit" class="cda-btn-submit">
            <span>Acceder al Asesor Virtual</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </button>
        </form>
      </div>
    `;

    document.body.appendChild(overlay);

    const form = document.getElementById("cda-registration-form");
    const errorBox = document.getElementById("cda-form-error");

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const nombre = document.getElementById("cda-reg-nombre").value.trim();
      const cedula = document.getElementById("cda-reg-cedula").value.trim();
      const celular = document.getElementById("cda-reg-celular").value.trim();
      const correo = document.getElementById("cda-reg-correo").value.trim();

      // Validaciones
      if (!nombre || !cedula || !celular || !correo) {
        showError("Por favor complete todos los campos obligatorios.");
        return;
      }

      if (nombre.length < 3) {
        showError("Por favor ingrese su nombre y apellido completos.");
        return;
      }

      if (cedula.length < 4) {
        showError("Por favor ingrese un número de cédula o pasaporte válido.");
        return;
      }

      const digitsOnly = celular.replace(/\D/g, "");
      if (digitsOnly.length < 7) {
        showError("Por favor ingrese un número de celular de al menos 7 u 8 dígitos.");
        return;
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(correo)) {
        showError("Por favor ingrese un correo electrónico válido (ej: usuario@dominio.com).");
        return;
      }

      // Datos válidos
      errorBox.style.display = "none";
      const clientData = { nombre, cedula, celular, correo };
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(clientData));

      // Animación de salida y envío a Chainlit
      overlay.style.transition = "opacity 0.25s ease-out";
      overlay.style.opacity = "0";

      setTimeout(() => {
        if (overlay.parentNode) {
          overlay.parentNode.removeChild(overlay);
        }
        sendClientDataToChat(clientData);
      }, 250);
    });

    function showError(msg) {
      errorBox.textContent = msg;
      errorBox.style.display = "block";
    }
  }

  function sendClientDataToChat(clientData) {
    const formattedMsg = `📋 Registro de Precalificación: Nombre: ${clientData.nombre} | Cédula: ${clientData.cedula} | Celular: ${clientData.celular} | Correo: ${clientData.correo}`;

    let attempts = 0;
    const interval = setInterval(() => {
      attempts++;
      const textarea = document.getElementById("chat-input") || document.querySelector("textarea");
      const submitBtn = document.getElementById("chat-submit");

      if (textarea && submitBtn) {
        clearInterval(interval);
        
        // Asignar valor compatible con el estado de React
        const nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
        if (nativeSetter) {
          nativeSetter.call(textarea, formattedMsg);
        } else {
          textarea.value = formattedMsg;
        }

        textarea.dispatchEvent(new Event("input", { bubbles: true }));
        textarea.dispatchEvent(new Event("change", { bubbles: true }));

        setTimeout(() => {
          submitBtn.click();
        }, 150);
      } else if (attempts > 50) {
        clearInterval(interval);
      }
    }, 120);
  }

  // Inicialización cuando el DOM esté listo
  function init() {
    const isRegistered = sessionStorage.getItem(STORAGE_KEY);
    if (!isRegistered) {
      createModal();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // Exponer función para volver a abrir el formulario si el usuario lo desea
  window.cdaOpenRegistrationModal = function () {
    createModal();
  };
})();
