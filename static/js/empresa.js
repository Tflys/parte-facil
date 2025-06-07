// Inicializa animaciones AOS
AOS.init();

// --- Scroll suave a secciones ---
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if(target){
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth' });
    }
  });
});

// --- Contadores animados ---
function animateCounter(element, to) {
  let current = 0;
  const increment = Math.max(1, Math.ceil(to / 150));
  const interval = setInterval(() => {
    current += increment;
    if (current >= to) {
      element.textContent = '+' + to;
      clearInterval(interval);
    } else {
      element.textContent = current;
    }
  }, 40);
}


document.addEventListener('DOMContentLoaded', () => {
  // Animar todos los contadores cuando aparecen en pantalla
  const counters = document.querySelectorAll('.contador');
  if (counters.length) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const el = entry.target;
          animateCounter(el, parseInt(el.dataset.valor));
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.7 });
    counters.forEach(el => observer.observe(el));
  }
});

// --- Efecto Parallax en hero ---
const hero = document.querySelector('.hero');
if (hero) {
  hero.addEventListener('mousemove', function(e){
    const x = (e.clientX / window.innerWidth - 0.5) * 20;
    const y = (e.clientY / window.innerHeight - 0.5) * 20;
    this.style.backgroundPosition = `${50 + x}% ${50 + y}%`;
  });
  // Vuelve al centro si el ratón sale
  hero.addEventListener('mouseleave', function(){
    this.style.backgroundPosition = '50% 50%';
  });
}
// Validación JS personalizada del formulario de contacto
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-contacto');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    let valido = true;

    // Validación nombre
    const nombre = document.getElementById('nombre');
    if (!nombre.value.trim() || nombre.value.trim().length < 2) {
      nombre.classList.add('is-invalid');
      valido = false;
    } else {
      nombre.classList.remove('is-invalid');
      nombre.classList.add('is-valid');
    }

    // Validación teléfono (9 dígitos, sólo números)
    const telefono = document.getElementById('telefono');
    const telValido = /^[0-9]{9}$/.test(telefono.value.trim());
    if (!telValido) {
      telefono.classList.add('is-invalid');
      valido = false;
    } else {
      telefono.classList.remove('is-invalid');
      telefono.classList.add('is-valid');
    }

    // Validación mensaje (mínimo 10 caracteres)
    const mensaje = document.getElementById('mensaje');
    if (!mensaje.value.trim() || mensaje.value.trim().length < 10) {
      mensaje.classList.add('is-invalid');
      valido = false;
    } else {
      mensaje.classList.remove('is-invalid');
      mensaje.classList.add('is-valid');
    }

    // Si pasa la validación, muestra mensaje de éxito y resetea el form
    if (valido) {
      document.getElementById('mensaje-ok').classList.remove('d-none');
      form.reset();
      // Quita cualquier marca de validación
      campos.forEach(id => {
        const el = document.getElementById(id);
        el.classList.remove('is-valid', 'is-invalid');
    });
      actualizarProgreso();
      setTimeout(() => {
        mensajeOk.classList.add('d-none');
        mensajeOk.classList.remove('animate__fadeInDown');
    }, 3500);
    }
  });

  // Quitar error al escribir
  ['nombre', 'telefono', 'mensaje'].forEach(id => {
    const el = document.getElementById(id);
    el.addEventListener('input', () => {
      el.classList.remove('is-invalid');
    });
  });
});
// Tooltips Bootstrap
document.addEventListener('DOMContentLoaded', function () {
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Año actual en el pie de página
document.getElementById('year').textContent = new Date().getFullYear();

// Sugerencias de mensaje
document.querySelectorAll('.sugerencia').forEach(btn => {
  btn.addEventListener('click', function() {
    document.getElementById('mensaje').value = this.textContent;
    document.getElementById('mensaje').dispatchEvent(new Event('input')); // actualizar validación/progreso
  });
});

// Cambiar placeholder según servicio seleccionado
document.getElementById('servicio').addEventListener('change', function() {
  const mensaje = document.getElementById('mensaje');
  const opciones = {
    desatasco: "Ej: Tengo un atasco en el baño, necesito ayuda urgente.",
    fontaneria: "Ej: Tengo una fuga de agua en la cocina.",
    mantenimiento: "Ej: Solicito información para mantenimiento de mi comunidad.",
    presupuesto: "Ej: Quiero presupuesto para limpiar un pozo.",
    otros: "Ej: Consulta general..."
  };
  mensaje.placeholder = opciones[this.value] || "¿En qué podemos ayudarte?";
});

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('form-contacto');
  if (!form) return;

  const campos = ['nombre', 'telefono', 'email', 'servicio', 'mensaje'];
  const btnEnviar = document.getElementById('btn-enviar');
  const btnSpinner = document.getElementById('btn-spinner');
  const btnTexto = document.getElementById('btn-texto');
  const btnReset = document.getElementById('btn-reset');
  const barra = document.getElementById('progreso-form');
  const mensajeOk = document.getElementById('mensaje-ok');

  // ---- Barra de progreso ----
  function actualizarProgreso() {
    let completados = 0;
    if (document.getElementById('nombre').value.trim().length >= 2) completados++;
    if (/^[1-9][0-9]{8}$/.test(document.getElementById('telefono').value.trim())) completados++;
    const emailVal = document.getElementById('email').value.trim();
    if (emailVal === "" || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) completados++;
    if (document.getElementById('servicio').value) completados++;
    if (document.getElementById('mensaje').value.trim().length >= 10) completados++;

    const porcentaje = Math.round(completados * 100 / 5);
    barra.style.width = porcentaje + "%";
    barra.setAttribute('aria-valuenow', porcentaje);
    barra.textContent = porcentaje + "%";
    barra.classList.toggle('bg-success', porcentaje === 100);
    barra.classList.toggle('bg-warning', porcentaje < 100);
  }

  campos.forEach(id => {
    const el = document.getElementById(id);
    el.addEventListener('input', actualizarProgreso);
    el.addEventListener('change', actualizarProgreso);

    // Quitar error en cuanto escribe
    el.addEventListener('input', () => {
      el.classList.remove('is-invalid', 'is-valid');
    });
  });
  actualizarProgreso();

  // ---- SUBMIT ----
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    let valido = true;

    // Validar nombre
    const nombre = document.getElementById('nombre');
    if (!nombre.value.trim() || nombre.value.trim().length < 2) {
      nombre.classList.add('is-invalid');
      valido = false;
    } else {
      nombre.classList.remove('is-invalid');
    }

    // Validar teléfono
    const telefono = document.getElementById('telefono');
    const telValido = /^[1-9][0-9]{8}$/.test(telefono.value.trim());
    if (!telValido) {
      telefono.classList.add('is-invalid');
      valido = false;
    } else {
      telefono.classList.remove('is-invalid');
    }

    // Validar email (opcional)
    const email = document.getElementById('email');
    const emailVal = email.value.trim();
    if (emailVal && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) {
      email.classList.add('is-invalid');
      valido = false;
    } else {
      email.classList.remove('is-invalid');
    }

    // Validar servicio
    const servicio = document.getElementById('servicio');
    if (!servicio.value) {
      servicio.classList.add('is-invalid');
      valido = false;
    } else {
      servicio.classList.remove('is-invalid');
    }

    // Validar mensaje
    const mensaje = document.getElementById('mensaje');
    if (!mensaje.value.trim() || mensaje.value.trim().length < 10) {
      mensaje.classList.add('is-invalid');
      valido = false;
    } else {
      mensaje.classList.remove('is-invalid');
    }

    actualizarProgreso();

    if (valido) {
      // Loader animado
      btnTexto.textContent = "Enviando...";
      btnSpinner.classList.remove('d-none');
      btnEnviar.setAttribute('disabled', 'disabled');

      setTimeout(() => {
        // Reset todo: campos, marcas y progreso
        form.reset();
        // Quitar cualquier marca de validación tras reset
        setTimeout(() => {
          campos.forEach(id => {
            const el = document.getElementById(id);
            el.classList.remove('is-valid', 'is-invalid');
          });
          actualizarProgreso();
        }, 0);

        btnTexto.textContent = "Enviar mensaje";
        btnSpinner.classList.add('d-none');
        btnEnviar.removeAttribute('disabled');
        // Mensaje de éxito animado
        mensajeOk.classList.remove('d-none');
        mensajeOk.classList.add('animate__fadeInDown');
        setTimeout(() => {
          mensajeOk.classList.add('d-none');
          mensajeOk.classList.remove('animate__fadeInDown');
        }, 3500);
      }, 1200);
    }
  });

  // ---- Botón borrar ----
  btnReset.addEventListener('click', () => {
    form.reset();
    setTimeout(() => {
      campos.forEach(id => {
        const el = document.getElementById(id);
        el.classList.remove('is-invalid', 'is-valid');
      });
      actualizarProgreso();
    }, 0);
  });
});

