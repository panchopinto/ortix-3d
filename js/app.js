/* ORTIX 3D — comportamiento. Sin dependencias externas. Funciona también desde file://. */
(function () {
  "use strict";

  document.documentElement.classList.add("js");

  /* ---------- Navegación: marca la sección visible ---------- */
  function iniciarNavegacion() {
    var enlaces = Array.prototype.slice.call(document.querySelectorAll(".barra__nav a"));
    var contenedorNav = document.querySelector(".barra__nav");
    var porId = {};
    enlaces.forEach(function (a) { porId[a.getAttribute("href").slice(1)] = a; });

    // Secciones en orden de aparición; «portada» y «referencias» no tienen enlace y limpian el resaltado.
    var secciones = Array.prototype.slice.call(document.querySelectorAll("main > section[id]"));
    var actual = null;
    var pendiente = false;

    function actualizar() {
      pendiente = false;
      var linea = window.innerHeight * 0.35;
      var vigente = null;
      secciones.forEach(function (s) {
        if (s.getBoundingClientRect().top <= linea) { vigente = s.id; }
      });
      if (vigente === actual) { return; }
      actual = vigente;
      enlaces.forEach(function (a) { a.removeAttribute("aria-current"); });
      var enlace = vigente ? porId[vigente] : null;
      if (enlace) {
        enlace.setAttribute("aria-current", "true");
        // Desplaza solo la barra horizontal, sin mover la página.
        var centro = enlace.offsetLeft - (contenedorNav.clientWidth - enlace.offsetWidth) / 2;
        contenedorNav.scrollLeft = Math.max(0, centro);
      }
    }

    function programar() {
      if (!pendiente) { pendiente = true; window.setTimeout(actualizar, 80); }
    }

    window.addEventListener("scroll", programar, { passive: true });
    window.addEventListener("resize", programar);
    actualizar();
  }

  /* ---------- Explorador de la órtesis ---------- */
  function iniciarExplorador() {
    var puntos = Array.prototype.slice.call(document.querySelectorAll(".punto"));
    var botones = Array.prototype.slice.call(document.querySelectorAll(".zonas button"));
    var fichas = Array.prototype.slice.call(document.querySelectorAll(".ficha"));
    if (!fichas.length) { return; }

    function seleccionar(zona, moverFoco) {
      fichas.forEach(function (f) { f.classList.toggle("activa", f.getAttribute("data-zona") === zona); });
      puntos.forEach(function (p) {
        var activo = p.getAttribute("data-zona") === zona;
        p.classList.toggle("activo", activo);
        p.setAttribute("aria-pressed", activo ? "true" : "false");
      });
      botones.forEach(function (b) {
        b.setAttribute("aria-pressed", b.getAttribute("data-zona") === zona ? "true" : "false");
      });
      if (moverFoco) {
        var ficha = document.getElementById("ficha-" + zona);
        if (ficha && ficha.getBoundingClientRect().top > window.innerHeight * 0.85) {
          ficha.scrollIntoView({ block: "center", behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
        }
      }
    }

    puntos.concat(botones).forEach(function (el) {
      el.addEventListener("click", function () { seleccionar(el.getAttribute("data-zona"), true); });
    });
    puntos.forEach(function (p) { p.setAttribute("aria-controls", "ficha-" + p.getAttribute("data-zona")); });
    seleccionar("cadera", false);
  }

  /* ---------- Compartir QR ---------- */
  function urlValida(texto) {
    return typeof texto === "string" && /^https:\/\/[^\s]+$/.test(texto);
  }

  function copiarConSeleccion(texto) {
    return new Promise(function (resolve, reject) {
      var area = document.createElement("textarea");
      area.value = texto;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      area.setSelectionRange(0, texto.length);
      var copiado = false;
      try { copiado = document.execCommand("copy"); } catch (e) { copiado = false; }
      document.body.removeChild(area);
      if (copiado) { resolve(); } else { reject(new Error("copy")); }
    });
  }

  function copiarTexto(texto) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(texto).catch(function () {
        return copiarConSeleccion(texto);
      });
    }
    return copiarConSeleccion(texto);
  }

  function iniciarCompartir() {
    var caja = document.getElementById("compartir-caja");
    if (!caja) { return; }
    var url = (window.ORTIX_CONFIG && window.ORTIX_CONFIG.publicUrl) || "";
    if (!urlValida(url)) { return; } // estado "pendiente": se deja el texto por defecto

    var img = document.getElementById("qr-img");
    var pendiente = document.getElementById("qr-pendiente");
    var texto = document.getElementById("url-publica");
    var copiar = document.getElementById("btn-copiar");
    var estado = document.getElementById("estado-copia");

    caja.setAttribute("data-estado", "activo");
    texto.textContent = url;
    img.src = "qr/qr-ortix-3d.svg";
    img.hidden = false;
    pendiente.hidden = true;
    ["png", "svg"].forEach(function (ext) {
      var enlace = document.getElementById("dl-" + ext);
      enlace.href = "qr/qr-ortix-3d." + ext;
      enlace.hidden = false;
    });
    copiar.disabled = false;

    copiar.addEventListener("click", function () {
      estado.textContent = "";
      copiarTexto(url).then(function () {
        estado.textContent = "Enlace copiado.";
      }, function () {
        estado.textContent = "No se pudo copiar. Selecciona la dirección y cópiala manualmente.";
      });
    });
  }

  iniciarNavegacion();
  iniciarExplorador();
  iniciarCompartir();
})();
