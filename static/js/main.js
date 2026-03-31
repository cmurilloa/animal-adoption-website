// ===================================
//  ANIMAL LIBRE - JavaScript principal
// ===================================

document.addEventListener('DOMContentLoaded', () => {
  lucide.createIcons();
  initMobileMenu();
  initCarousel();
  initTabs();
  initAdopciones();
  initFormulario();
});

// ===================================
//  MOBILE MENU
// ===================================
function initMobileMenu() {
  const btn = document.getElementById('menuBtn');
  const nav = document.getElementById('mobileNav');
  if (!btn || !nav) return;

  let isOpen = false;

  btn.addEventListener('click', () => {
    isOpen = !isOpen;
    nav.classList.toggle('open', isOpen);
    // Swap icon
    btn.innerHTML = isOpen
      ? '<i data-lucide="x" style="width:24px;height:24px;"></i>'
      : '<i data-lucide="menu" style="width:24px;height:24px;"></i>';
    lucide.createIcons();
  });
}

// ===================================
//  CAROUSEL INFINITO (Home page)
// ===================================
function initCarousel() {
  const track = document.getElementById('carouselTrack');
  const prevBtn = document.getElementById('carouselPrev');
  const nextBtn = document.getElementById('carouselNext');
  const dotsContainer = document.getElementById('carouselDots');

  if (!track) return;

  const originals = Array.from(track.querySelectorAll('.carousel-slide'));
  const n = originals.length;
  if (!n) return;

  let visible = getVisible();
  let extCurrent = visible; // posición en el array extendido (con clones)
  let animating = false;
  let autoTimer = null;

  function getVisible() {
    const w = window.innerWidth;
    if (w >= 1024) return 3;
    if (w >= 640) return 2;
    return 1;
  }

  // Construye clones: antepone los últimos `v` slides, agrega los primeros `v` al final
  function buildClones() {
    track.querySelectorAll('.carousel-clone').forEach(c => c.remove());
    const v = getVisible();

    // Clonar los últimos v y prepend (en orden)
    const firstReal = track.querySelector('.carousel-slide:not(.carousel-clone)');
    for (let i = n - v; i < n; i++) {
      const clone = originals[i].cloneNode(true);
      clone.classList.add('carousel-clone');
      track.insertBefore(clone, firstReal);
    }

    // Clonar los primeros v y append
    for (let i = 0; i < v; i++) {
      const clone = originals[i].cloneNode(true);
      clone.classList.add('carousel-clone');
      track.appendChild(clone);
    }
  }

  function getSlideWidth() {
    const s = track.querySelector('.carousel-slide');
    return s ? s.offsetWidth + 24 : 0; // 24px = gap 1.5rem
  }

  function moveTo(index, animate) {
    const sw = getSlideWidth();
    track.style.transition = animate ? 'transform 0.5s ease' : 'none';
    track.style.transform = `translateX(-${index * sw}px)`;
  }

  // Al terminar la animación, hacer snap silencioso si estamos en zona de clones
  // (filtramos el evento para que solo reaccione al track, no a elementos hijos)
  track.addEventListener('transitionend', (e) => {
    if (e.target !== track) return;
    const v = getVisible();
    if (extCurrent >= v + n) {
      extCurrent -= n;
      moveTo(extCurrent, false);
    } else if (extCurrent < v) {
      extCurrent += n;
      moveTo(extCurrent, false);
    }
    animating = false;
    updateDots();
  });

  function step(dir) {
    if (animating) return;
    animating = true;
    extCurrent += dir;
    moveTo(extCurrent, true);
  }

  function updateDots() {
    if (!dotsContainer) return;
    const v = getVisible();
    const dotIdx = (extCurrent - v + n) % n;
    dotsContainer.querySelectorAll('.carousel-dot').forEach((d, i) => {
      d.classList.toggle('active', i === dotIdx);
    });
  }

  function buildDots() {
    if (!dotsContainer) return;
    dotsContainer.innerHTML = '';
    for (let i = 0; i < n; i++) {
      const dot = document.createElement('button');
      dot.className = 'carousel-dot';
      dot.setAttribute('aria-label', `Ir a diapositiva ${i + 1}`);
      dot.addEventListener('click', () => {
        if (animating) return;
        animating = true;
        extCurrent = getVisible() + i;
        moveTo(extCurrent, true);
        resetAutoplay();
      });
      dotsContainer.appendChild(dot);
    }
    updateDots();
  }

  function startAutoplay() { autoTimer = setInterval(() => step(1), 3000); }
  function resetAutoplay() { clearInterval(autoTimer); startAutoplay(); }

  if (prevBtn) prevBtn.addEventListener('click', () => { step(-1); resetAutoplay(); });
  if (nextBtn) nextBtn.addEventListener('click', () => { step(1); resetAutoplay(); });

  function init() {
    visible = getVisible();
    buildClones();
    extCurrent = visible;
    moveTo(extCurrent, false);
    buildDots();
    startAutoplay();
    lucide.createIcons();
  }

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      clearInterval(autoTimer);
      init();
    }, 150);
  });

  init();
}

// ===================================
//  ADOPCIONES PAGE
// ===================================
let allPets = [];
const likedPets = new Set();

function renderPets(list) {
  const grid = document.getElementById('petsGrid');
  const count = document.getElementById('petsCount');
  const noResults = document.getElementById('noResults');

  if (list.length === 0) {
    grid.innerHTML = '';
    count.textContent = '';
    noResults.style.display = 'block';
    return;
  }

  noResults.style.display = 'none';
  count.textContent = `Mostrando ${list.length} ${list.length === 1 ? 'animal' : 'animales'}`;

  grid.innerHTML = list.map(pet => {
    const imgs = (pet.images && pet.images.length > 0) ? pet.images : [pet.image];
    const multi = imgs.length > 1;
    return `
    <div class="pet-card" data-pet-id="${pet.id}" data-img-index="0" data-imgs='${JSON.stringify(imgs)}'>
      <div class="pet-image">
        <img src="${imgs[0]}" alt="${pet.name}" onerror="this.src='https://placehold.co/400x220/f0f7f3/093825?text=${pet.name}'" />
        <span class="pet-badge">🐾 ${pet.breed || ''}</span>
        ${pet.nuevo ? '<span class="pet-age-badge">¡Nuevo!</span>' : ''}
        <button class="pet-favorite-btn${likedPets.has(pet.id) ? ' liked' : ''}" onclick="toggleFavorite(this, ${pet.id})" aria-label="Guardar en favoritos">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="${likedPets.has(pet.id) ? '#ef4444' : 'none'}" stroke="${likedPets.has(pet.id) ? '#ef4444' : 'currentColor'}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
        </button>
        ${multi ? `
        <button class="pet-slide-btn pet-slide-prev" onclick="slideCard(event, ${pet.id}, -1)" aria-label="Foto anterior">&#8249;</button>
        <button class="pet-slide-btn pet-slide-next" onclick="slideCard(event, ${pet.id}, 1)" aria-label="Foto siguiente">&#8250;</button>
        <div class="pet-slide-dots">${imgs.map((_, i) => `<span class="pet-slide-dot${i === 0 ? ' active' : ''}"></span>`).join('')}</div>
        ` : ''}
      </div>
      <div class="pet-info">
        <h3>${pet.name} · ${pet.gender || ''} · ${pet.edad_label}</h3>
        <p class="pet-tagline">${pet.descripcion.replace(/\n/g, '<br>')}</p>
        <button class="btn-adopt" onclick="openModal(${pet.id})">Conóceme</button>
      </div>
    </div>
  `}).join('');
}

function slideCard(e, petId, dir) {
  e.stopPropagation();
  const card = document.querySelector(`.pet-card[data-pet-id="${petId}"]`);
  const imgs = JSON.parse(card.dataset.imgs);
  let idx = (parseInt(card.dataset.imgIndex) + dir + imgs.length) % imgs.length;
  card.dataset.imgIndex = idx;
  card.querySelector('.pet-image img').src = imgs[idx];
  card.querySelectorAll('.pet-slide-dot').forEach((dot, i) => dot.classList.toggle('active', i === idx));
}

function toggleFavorite(btn, id) {
  if (likedPets.has(id)) {
    likedPets.delete(id);
    btn.classList.remove('liked');
    btn.querySelector('svg').setAttribute('fill', 'none');
    btn.querySelector('svg').setAttribute('stroke', 'currentColor');
  } else {
    likedPets.add(id);
    btn.classList.add('liked');
    btn.querySelector('svg').setAttribute('fill', '#ef4444');
    btn.querySelector('svg').setAttribute('stroke', '#ef4444');
  }
}

function getChipValue(group) {
  const active = document.querySelector(`.chip-btn.active[data-group="${group}"]`);
  return active ? active.dataset.value : 'todos';
}

function filterPets() {
  const search = document.getElementById('searchInput').value.toLowerCase();
  const breed = document.getElementById('breedInput')?.value || '';
  const ageMin = parseFloat(document.getElementById('ageMin')?.value) || null;
  const ageMax = parseFloat(document.getElementById('ageMax')?.value) || null;
  const gender = getChipValue('gender');
  const showFavorites = document.getElementById('favoritesFilter')?.classList.contains('active');

  const filtered = allPets.filter(p => {
    const matchSearch = !search || p.name.toLowerCase().includes(search);
    const matchBreed = !breed || p.breed === breed;
    const matchAgeMin = ageMin === null || p.age_years >= ageMin;
    const matchAgeMax = ageMax === null || p.age_years <= ageMax;
    const matchGender = gender === 'todos' || p.gender === gender;
    const matchFavorites = !showFavorites || likedPets.has(p.id);
    return matchSearch && matchBreed && matchAgeMin && matchAgeMax && matchGender && matchFavorites;
  });

  renderPets(filtered);
}

function clearFilters() {
  document.getElementById('searchInput').value = '';
  const breedInput = document.getElementById('breedInput');
  if (breedInput) breedInput.value = '';
  const ageMin = document.getElementById('ageMin');
  const ageMax = document.getElementById('ageMax');
  if (ageMin) ageMin.value = '';
  if (ageMax) ageMax.value = '';
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.value === 'todos');
  });
  renderPets(allPets);
}

function openModal(id) {
  const pet = allPets.find(p => p.id === id);
  if (!pet) return;

  const images = pet.images || [pet.image];
  const mainImg = document.getElementById('modalMainImg');
  const thumbsContainer = document.getElementById('modalThumbs');
  const info = document.getElementById('modalInfo');

  mainImg.src = images[0];
  mainImg.alt = pet.name;

  thumbsContainer.innerHTML = images.map((src, i) => `
    <img
      src="${src}"
      alt="${pet.name} foto ${i + 1}"
      class="pet-modal-thumb${i === 0 ? ' active' : ''}"
      onclick="selectThumb(this, '${src}')"
      onerror="this.src='https://placehold.co/72x72/e2e8f0/64748b?text=📷'"
    />
  `).join('');

  info.innerHTML = `
    <div class="pet-modal-badges">
      <span class="pet-badge" style="position:static;display:inline-block">🐾 ${pet.breed || ''}</span>
      ${pet.nuevo ? '<span class="pet-age-badge" style="position:static;display:inline-block">¡Nuevo!</span>' : ''}
    </div>
    <div>
      <h2 class="pet-modal-title">${pet.name}</h2>
      <p class="pet-modal-subtitle">${pet.gender || ''} · ${pet.edad_label}</p>
    </div>
    <p class="pet-modal-desc">${pet.descripcion.replace(/\n/g, '<br>')}</p>
    <div class="pet-modal-adopt">
      <button class="btn-adopt" onclick="window.location.href='/formulario-de-adopcion?pet=${pet.id}'">
        Iniciar adopción
      </button>
    </div>
  `;

  document.getElementById('petModal').style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('petModal').style.display = 'none';
  document.body.style.overflow = '';
}

function selectThumb(thumb, src) {
  document.getElementById('modalMainImg').src = src;
  document.querySelectorAll('.pet-modal-thumb').forEach(t => t.classList.remove('active'));
  thumb.classList.add('active');
}

function initAdopciones() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;

  searchInput.addEventListener('input', filterPets);

  const breedInput = document.getElementById('breedInput');
  if (breedInput) breedInput.addEventListener('change', filterPets);

  const ageMin = document.getElementById('ageMin');
  const ageMax = document.getElementById('ageMax');
  if (ageMin) ageMin.addEventListener('input', filterPets);
  if (ageMax) ageMax.addEventListener('input', filterPets);

  document.getElementById('petModal').addEventListener('click', e => {
    if (e.target === e.currentTarget) closeModal();
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeModal();
  });

  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      if (btn.classList.contains('chip-btn-favorite')) {
        btn.classList.toggle('active');
      } else {
        const group = btn.dataset.group;
        document.querySelectorAll(`.chip-btn[data-group="${group}"]`).forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      }
      filterPets();
    });
  });

  fetch('/api/pets')
    .then(res => res.json())
    .then(data => {
      allPets = data.filter(p => !p.adoptado);

      // Poblar el select de razas con valores únicos
      const breedSelect = document.getElementById('breedInput');
      if (breedSelect) {
        const breeds = [...new Set(allPets.map(p => p.breed).filter(Boolean))].sort();
        breeds.forEach(breed => {
          const opt = document.createElement('option');
          opt.value = breed;
          opt.textContent = breed;
          breedSelect.appendChild(opt);
        });
      }

      renderPets(allPets);
    })
    .catch(() => {
      document.getElementById('petsGrid').innerHTML = '<p>Error al cargar las mascotas. Intenta de nuevo más tarde.</p>';
    });
}

// ===================================
//  FORMULARIO DE ADOPCIÓN
// ===================================
function initFormulario() {
  const acuerdoCheckbox = document.getElementById('acuerdo-checkbox');
  const formSection = document.getElementById('form-section');

  console.log('initFormulario -> acuerdoCheckbox:', acuerdoCheckbox, 'formSection:', formSection);

  if (!acuerdoCheckbox) {
    console.warn('initFormulario: no se encontró #acuerdo-checkbox en el DOM');
  }
  if (!formSection) {
    console.warn('initFormulario: no se encontró #form-section en el DOM');
  }

  
  if (formSection) {
    formSection.classList.add('hidden');
  }

  if (acuerdoCheckbox) {
    acuerdoCheckbox.checked = false;
    acuerdoCheckbox.addEventListener('change', function () {
      if (!formSection) return;
      formSection.classList.toggle('hidden', !this.checked);
      formSection.hidden = !this.checked;
    });
  }

  const select = document.getElementById('mascota');
  const selectSegunda = document.getElementById('mascotaSegunda');
  if (!select) return;

  fetch('/api/pets')
    .then(r => r.json())
    .then(pets => {
      const available = pets.filter(p => !p.adoptado);

      available.forEach(p => {
        const opt = document.createElement('option');
        opt.value = p.name;
        opt.textContent = `${p.name} · ${p.type} · ${p.edad_label}`;
        select.appendChild(opt);
      });

      if (selectSegunda) {
        const populateSegunda = () => {
          const selected = select.value;
          selectSegunda.innerHTML = '<option value="">Selecciona una mascota</option>';
          available
            .filter(p => p.name !== selected)
            .forEach(p => {
              const opt2 = document.createElement('option');
              opt2.value = p.name;
              opt2.textContent = `${p.name} · ${p.type} · ${p.edad_label}`;
              selectSegunda.appendChild(opt2);
            });
        };

        populateSegunda();
        select.addEventListener('change', populateSegunda);
      }
    });

  const ninosInput = document.getElementById('ninos-hogar');
  const edadesGroup = document.getElementById('edades-ninos-group');
  const edadesInput = document.getElementById('edades-ninos');
  if (ninosInput && edadesGroup && edadesInput) {
    ninosInput.addEventListener('input', function () {
      const mostrar = parseInt(this.value, 10) >= 1;
      edadesGroup.classList.toggle('hidden', !mostrar);
      edadesInput.required = mostrar;
    });
  }

  const acuerdoRadios = document.querySelectorAll('input[name="acuerdo"]');
  const acuerdoDetalles = document.getElementById('acuerdo-detalles');
  if (acuerdoRadios.length && acuerdoDetalles) {
    acuerdoRadios.forEach(radio => {
      radio.addEventListener('change', function () {
        const mostrar = this.value === 'no';
        acuerdoDetalles.style.visibility = mostrar ? 'visible' : 'hidden';
        acuerdoDetalles.style.pointerEvents = mostrar ? 'auto' : 'none';
        acuerdoDetalles.required = mostrar;
        if (!mostrar) acuerdoDetalles.value = '';
      });
    });
  }

  const permitirVisitaRadios = document.querySelectorAll('input[name="permitir-visita"]');
  const permitirVisitaDetalles = document.getElementById('permitir-visita-detalles');
  if (permitirVisitaRadios.length && permitirVisitaDetalles) {
    permitirVisitaRadios.forEach(radio => {
      radio.addEventListener('change', function () {
        const mostrar = this.value === 'no';
        permitirVisitaDetalles.style.visibility = mostrar ? 'visible' : 'hidden';
        permitirVisitaDetalles.style.pointerEvents = mostrar ? 'auto' : 'none';
        permitirVisitaDetalles.required = mostrar;
        if (!mostrar) permitirVisitaDetalles.value = '';
      });
    });
  }

  const esterilizacionRadios = document.querySelectorAll('input[name="esterilizacion"]');
  const esterilizacionDetalles = document.getElementById('esterilizacion-detalles');
  if (esterilizacionRadios.length && esterilizacionDetalles) {
    esterilizacionRadios.forEach(radio => {
      radio.addEventListener('change', function () {
        const mostrar = this.value === 'no';
        esterilizacionDetalles.style.visibility = mostrar ? 'visible' : 'hidden';
        esterilizacionDetalles.style.pointerEvents = mostrar ? 'auto' : 'none';
        esterilizacionDetalles.required = mostrar;
        if (!mostrar) esterilizacionDetalles.value = '';
      });
    });
  }


  const primeraAdopcionRadios = document.querySelectorAll('input[name="primera-adopcion"]');
  const primeraAdopcionDetalles = document.getElementById('primera-adopcion-detalles');
  const adopcionPreviaDetalles = document.getElementById('adopcion-previa-detalles');
  if (primeraAdopcionRadios.length && primeraAdopcionDetalles) {
    primeraAdopcionRadios.forEach(radio => {
      radio.addEventListener('change', function () {
        const esNo = this.value === 'no';
        primeraAdopcionDetalles.style.visibility = esNo ? 'visible' : 'hidden';
        primeraAdopcionDetalles.style.pointerEvents = esNo ? 'auto' : 'none';
        primeraAdopcionDetalles.required = esNo;
        if (!esNo) primeraAdopcionDetalles.value = '';
        if (adopcionPreviaDetalles) {
          adopcionPreviaDetalles.classList.toggle('hidden', !( this.value === 'si'));
        }
      });
    });
  }

  const sobrepasarRadios = document.querySelectorAll('input[name="sobrepasar-presupuesto"]');
  const sobrepasarPorque = document.getElementById('sobrepasar-presupuesto-porque');
  if (sobrepasarRadios.length && sobrepasarPorque) {
    sobrepasarRadios.forEach(radio => {
      radio.addEventListener('change', function () {
        const mostrar = this.value === 'no';
        sobrepasarPorque.classList.toggle('input-invisible', !mostrar);
        sobrepasarPorque.style.pointerEvents = mostrar ? 'auto' : 'none';
        sobrepasarPorque.required = mostrar;
        if (!mostrar) sobrepasarPorque.value = '';
      });
    });
  }

  const seguroAdopcionRadios = document.querySelectorAll('input[name="seguro-adopcion"]');
  const seguroAdopcionPorque = document.getElementById('seguro-adopcion-porque');
  const seccionReferencias = document.getElementById('seccion-referencias');
  const seccionAnimales = document.getElementById('seccion-animales');
  const btnEnviarFin = document.getElementById('btn-enviar-fin');

  function actualizarVisibilidadFinal() {
    const seguroVal = document.querySelector('input[name="seguro-adopcion"]:checked')?.value;
    const primerAnimalVal = document.querySelector('input[name="primer-mascota"]:checked')?.value;

    if (btnEnviarFin) btnEnviarFin.classList.toggle('hidden', seguroVal !== 'no');
    if (seccionReferencias) seccionReferencias.classList.toggle('hidden', seguroVal !== 'si');
    if (seccionAnimales) seccionAnimales.classList.toggle('hidden', !(seguroVal === 'si' && primerAnimalVal === 'no'));
  }

  if (seguroAdopcionRadios.length && seguroAdopcionPorque) {
    seguroAdopcionRadios.forEach(radio => {
      radio.addEventListener('change', function () {
        const esNo = this.value === 'no';
        seguroAdopcionPorque.classList.toggle('input-invisible', !esNo);
        seguroAdopcionPorque.style.pointerEvents = esNo ? 'auto' : 'none';
        seguroAdopcionPorque.required = esNo;
        if (!esNo) seguroAdopcionPorque.value = '';
        actualizarVisibilidadFinal();
      });
    });
  }

  document.querySelectorAll('input[name="primer-mascota"]').forEach(radio => {
    radio.addEventListener('change', actualizarVisibilidadFinal);
  });

  const submitBtn = document.querySelector('#form-section button[type="submit"]');
  if (submitBtn) {
    submitBtn.addEventListener('click', function () {
      const cuidados = Array.from(
        document.querySelectorAll('.checkbox-cuidados input[type="checkbox"]:checked')
      ).map(cb => document.querySelector(`label[for="${cb.id}"]`).textContent.trim());

      console.log('Cuidados seleccionados:', cuidados);
    });
  }

  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', function (e) {
      e.preventDefault();

      const requiredFields = contactForm.querySelectorAll('[required]');
      let hasErrors = false;

      requiredFields.forEach(field => {
        const visible = field.offsetParent !== null;
        const empty = field.value.trim() === '' || (field.tagName === 'SELECT' && field.value === '');
        if (visible && empty) {
          field.classList.add('input-error');
          hasErrors = true;
        } else {
          field.classList.remove('input-error');
        }
      });

      if (hasErrors) return;

      const payload = {
        firstName: document.getElementById('firstName')?.value.trim() || '',
        lastName: document.getElementById('lastName')?.value.trim() || '',
        email: document.getElementById('email')?.value.trim() || '',
        phone: document.getElementById('phone')?.value.trim() || '',
        subject: document.getElementById('subject')?.value.trim() || '',
        message: document.getElementById('message')?.value.trim() || '',
      };

      fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
        .then(res => res.json())
        .then(() => {
          e.target.reset();
          alert('¡Mensaje enviado! Te contactaremos pronto.');
        })
        .catch(() => alert('Hubo un error al enviar. Intenta de nuevo.'));
    });

    contactForm.addEventListener('input', function (e) {
      if (e.target.classList.contains('input-error') && e.target.value.trim() !== '') {
        e.target.classList.remove('input-error');
      }
    });
    contactForm.addEventListener('change', function (e) {
      if (e.target.classList.contains('input-error') && e.target.value !== '') {
        e.target.classList.remove('input-error');
      }
    });
  }

  const adopcionModalOverlay = document.getElementById('adopcion-modal-overlay');
  const adopcionModalClose  = document.getElementById('adopcion-modal-close');
  if (adopcionModalOverlay) {
    adopcionModalClose.addEventListener('click', function () {
      adopcionModalOverlay.style.display = 'none';
    });
    adopcionModalOverlay.addEventListener('click', function (e) {
      if (e.target === adopcionModalOverlay) adopcionModalOverlay.style.display = 'none';
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') adopcionModalOverlay.style.display = 'none';
    });
  }

  const ingresosInput = document.getElementById('ingresos');
  if (ingresosInput) {
    ingresosInput.addEventListener('input', function () {
      let raw = this.value.replace(/\D/g, '');
      if (raw === '') { this.value = ''; return; }
      this.value = '$' + parseInt(raw, 10).toLocaleString('es-CO');
    });
  }
 const montoMensualInput = document.getElementById('monto-mensual');
  if (montoMensualInput) {
    montoMensualInput.addEventListener('input', function () {
      let raw = this.value.replace(/\D/g, '');
      if (raw === '') { this.value = ''; return; }
      this.value = '$' + parseInt(raw, 10).toLocaleString('es-CO');
    });
  }
  
  const arriendoRadios = document.querySelectorAll('input[name="vivienda"]');
  const acuerdoInline = document.getElementById('acuerdo-arrendatario-inline');
  const arrendatarioInfo = document.getElementById('arrendatario-info');
  const arrendatarioNombre = document.getElementById('arrendatario-nombre');
  const arrendatarioTelefono = document.getElementById('arrendatario-telefono');
  if (arriendoRadios.length && acuerdoInline) {
    arriendoRadios.forEach(radio => {
      radio.addEventListener('change', function () {
        const mostrar = this.value === 'Arriendo';
        acuerdoInline.style.display = mostrar ? 'flex' : 'none';
        arrendatarioInfo.style.display = mostrar ? '' : 'none';
        arrendatarioNombre.required = mostrar;
        arrendatarioTelefono.required = mostrar;
        if (!mostrar) {
          arrendatarioNombre.value = '';
          arrendatarioTelefono.value = '';
          document.querySelectorAll('input[name="acuerdo-arrendatario"]').forEach(r => r.checked = false);
        }
      });
    });
  }
}

// ===================================
//  TABS (Como Ayudar page)
// ===================================
function initTabs() {
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabPanels = document.querySelectorAll('.tab-panel');

  if (tabBtns.length === 0) return;

  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.tab;

      // Update buttons
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Update panels
      tabPanels.forEach(panel => {
        panel.classList.toggle('active', panel.id === `tab-${target}`);
      });

      lucide.createIcons();
    });
  });
}
