(function () {
  "use strict";

  var SCHEMA_HINT =
    "ExerciseBatch shape (no data yet):\n" +
    "{\n" +
    '  "exercicios": [\n' +
    "    {\n" +
    '      "enunciado": string,\n' +
    '      "resposta": string,\n' +
    '      "explicacao": string\n' +
    "    }\n" +
    "  ]\n" +
    "}";

  var form = document.getElementById("gerar-form");
  var btn = document.getElementById("submit-btn");
  var errorRegion = document.getElementById("error-region");
  var errorBadge = document.getElementById("error-badge");
  var errorMsg = document.getElementById("error-msg");
  var errorKind = document.getElementById("error-kind");
  var tabExercicios = document.getElementById("tab-exercicios");
  var tabJson = document.getElementById("tab-json");
  var panelExercicios = document.getElementById("panel-exercicios");
  var panelJson = document.getElementById("panel-json");
  var exerciciosEmpty = document.getElementById("exercicios-empty");
  var exerciciosList = document.getElementById("exercicios-list");
  var jsonOut = document.getElementById("json-out");

  var lastSuccessBatch = null;
  var BANNER_KEY = "demo-throwaway-banner-dismissed";
  var banner = document.getElementById("throwaway-banner");
  var bannerDismiss = document.getElementById("banner-dismiss");

  // D-16: dismissible banner for browser session via sessionStorage
  try {
    if (sessionStorage.getItem(BANNER_KEY) === "1" && banner) {
      banner.hidden = true;
    }
  } catch (_) {
    /* private mode / blocked storage — leave banner visible */
  }
  if (bannerDismiss && banner) {
    bannerDismiss.addEventListener("click", function () {
      banner.hidden = true;
      try {
        sessionStorage.setItem(BANNER_KEY, "1");
      } catch (_) {
        /* ignore */
      }
    });
  }

  function showTab(which) {
    var isEx = which === "exercicios";
    tabExercicios.setAttribute("aria-selected", isEx ? "true" : "false");
    tabJson.setAttribute("aria-selected", isEx ? "false" : "true");
    panelExercicios.hidden = !isEx;
    panelJson.hidden = isEx;
  }

  function clearError() {
    errorRegion.hidden = true;
    errorBadge.textContent = "";
    errorMsg.textContent = "";
    errorKind.textContent = "";
  }

  function showError(cls, message, kind) {
    errorRegion.hidden = false;
    errorBadge.textContent = cls || "Error";
    errorMsg.textContent = message || "";
    if (kind != null && kind !== "") {
      errorKind.textContent = "kind: " + kind;
    } else {
      errorKind.textContent = "";
    }
  }

  function renderExercicios(batch) {
    exerciciosList.innerHTML = "";
    var items = (batch && batch.exercicios) || [];
    if (!items.length) {
      exerciciosEmpty.hidden = false;
      return;
    }
    exerciciosEmpty.hidden = true;
    items.forEach(function (ex, i) {
      var div = document.createElement("div");
      div.className = "exercise";
      var h = document.createElement("h3");
      h.textContent = "Exercício " + (i + 1);
      var p1 = document.createElement("p");
      var s1 = document.createElement("strong");
      s1.textContent = "Enunciado: ";
      p1.appendChild(s1);
      p1.appendChild(document.createTextNode(ex.enunciado || ""));
      var p2 = document.createElement("p");
      var s2 = document.createElement("strong");
      s2.textContent = "Resposta: ";
      p2.appendChild(s2);
      p2.appendChild(document.createTextNode(ex.resposta || ""));
      var p3 = document.createElement("p");
      var s3 = document.createElement("strong");
      s3.textContent = "Explicação: ";
      p3.appendChild(s3);
      p3.appendChild(document.createTextNode(ex.explicacao || ""));
      div.appendChild(h);
      div.appendChild(p1);
      div.appendChild(p2);
      div.appendChild(p3);
      exerciciosList.appendChild(div);
    });
  }

  function renderJson(batch) {
    if (batch) {
      jsonOut.textContent = JSON.stringify(batch, null, 2);
    } else {
      jsonOut.textContent = SCHEMA_HINT;
    }
  }

  // Before first success: Exercícios empty; JSON shows schema hint (D-03)
  renderJson(null);

  tabExercicios.addEventListener("click", function () {
    showTab("exercicios");
  });
  tabJson.addEventListener("click", function () {
    showTab("json");
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    clearError();
    // D-09: disable only submit; leave other fields editable
    btn.disabled = true;
    btn.textContent = "Gerando…";

    var fd = new FormData(form);
    var payload = {
      materia: fd.get("materia"),
      topico: fd.get("topico"),
      dificuldade: fd.get("dificuldade"),
      quantidade: Number(fd.get("quantidade")),
      provider: fd.get("provider") || "",
      reasoning: fd.get("reasoning") || "medium",
    };

    try {
      var res = await fetch("/gerar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      // D-11: HTTP 409 sequential-contract message must include substring HTTP 409
      if (res.status === 409) {
        var busyBody = null;
        try {
          busyBody = await res.json();
        } catch (_) {
          busyBody = null;
        }
        var busyMsg =
          (busyBody && busyBody.error && busyBody.error.message) ||
          "Geração já em andamento (contrato sequencial). HTTP 409 — aguarde e tente de novo.";
        if (busyMsg.indexOf("HTTP 409") === -1) {
          busyMsg = busyMsg + " (HTTP 409)";
        }
        showError(
          (busyBody && busyBody.error && busyBody.error.class) || "BusyError",
          busyMsg,
          busyBody && busyBody.error && busyBody.error.kind
        );
        // D-12: keep last success content
        return;
      }

      var data;
      try {
        data = await res.json();
      } catch (_) {
        showError("ParseError", "Resposta inválida do servidor (não JSON).", null);
        return;
      }

      if (!data.ok) {
        var eobj = data.error || {};
        // D-10: EN class badge + PT message + kind
        showError(eobj.class, eobj.message, eobj.kind);
        // D-12: keep last success Exercícios/JSON
        return;
      }

      lastSuccessBatch = data.batch || null;
      renderExercicios(lastSuccessBatch);
      renderJson(lastSuccessBatch);
      showTab("exercicios");
    } catch (ex) {
      showError("NetworkError", String(ex && ex.message ? ex.message : ex), null);
    } finally {
      btn.disabled = false;
      btn.textContent = "Gerar";
    }
  });
})();
