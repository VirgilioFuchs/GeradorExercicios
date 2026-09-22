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
  var providerSelect = document.getElementById("provider-select");
  var modelSelect = document.getElementById("model-select");
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
  var modelsCatalog = null;
  var BANNER_KEY = "demo-throwaway-banner-dismissed";
  var banner = document.getElementById("throwaway-banner");
  var bannerDismiss = document.getElementById("banner-dismiss");

  function fillModelOptions(provider) {
    if (!modelSelect) return;
    var prev = modelSelect.value;
    modelSelect.innerHTML = "";
    var empty = document.createElement("option");
    empty.value = "";
    empty.textContent = "default (auto)";
    modelSelect.appendChild(empty);
    if (!modelsCatalog) return;
    var key = provider || "openai";
    if (key === "") key = "openai";
    var list = modelsCatalog[key] || [];
    var defaults = modelsCatalog.defaults || {};
    list.forEach(function (id) {
      var opt = document.createElement("option");
      opt.value = id;
      opt.textContent = id === defaults[key] ? id + " (default)" : id;
      modelSelect.appendChild(opt);
    });
    if (prev && list.indexOf(prev) !== -1) {
      modelSelect.value = prev;
    }
  }

  function loadModels() {
    return fetch("/models")
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        modelsCatalog = data;
        fillModelOptions(providerSelect ? providerSelect.value : "");
      })
      .catch(function () {
        modelsCatalog = null;
      });
  }

  if (providerSelect) {
    providerSelect.addEventListener("change", function () {
      fillModelOptions(providerSelect.value);
    });
  }
  loadModels();

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

  var softWarn = document.getElementById("band-soft-warn");
  var bandInputs = ["facil", "medio", "dificil"].map(function (name) {
    return form.querySelector('[name="' + name + '"]');
  });
  var qtyInput = form.querySelector('[name="quantidade"]');

  function parseBandCount(fd, name) {
    var n = Number(fd.get(name));
    if (!Number.isFinite(n) || n < 0) return 0;
    return Math.floor(n);
  }

  function syncBandAvailability() {
    var qty = qtyInput ? Number(qtyInput.value) : 0;
    var unlocked = Number.isFinite(qty) && qty > 0;
    bandInputs.forEach(function (el) {
      if (!el) return;
      el.disabled = !unlocked;
      if (!unlocked) el.value = "0";
    });
  }

  function updateSoftWarn() {
    if (!softWarn) return;
    var fd = new FormData(form);
    var facil = parseBandCount(fd, "facil");
    var medio = parseBandCount(fd, "medio");
    var dificil = parseBandCount(fd, "dificil");
    var qty = Number(fd.get("quantidade"));
    var sum = facil + medio + dificil;
    var lines = [];
    if (!Number.isFinite(qty) || qty <= 0) {
      lines.push(
        "Aviso: defina quantidade > 0 para liberar fácil / médio / difícil."
      );
    }
    if (sum === 0 && qty > 0) {
      lines.push(
        "Aviso: a soma das dificuldades é 0. O servidor pode rejeitar o pedido."
      );
    }
    if (sum > 40) {
      lines.push(
        "Aviso: a soma das dificuldades é maior que 40. O servidor pode rejeitar o pedido."
      );
    }
    if (qty > 0 && Number(qty) !== sum) {
      lines.push(
        "Aviso: quantidade (" +
          qty +
          ") é diferente da soma das bandas (" +
          sum +
          "). No modo uniforme o POST usa a contagem da banda; no misto o servidor valida."
      );
    }
    if (lines.length) {
      softWarn.hidden = false;
      softWarn.textContent = lines.join("\n");
    } else {
      softWarn.hidden = true;
      softWarn.textContent = "";
    }
  }

  function buildGerarPayload(fd) {
    var facil = parseBandCount(fd, "facil");
    var medio = parseBandCount(fd, "medio");
    var dificil = parseBandCount(fd, "dificil");
    var qty = Number(fd.get("quantidade"));
    var active = [];
    if (facil > 0) active.push({ band: "facil", count: facil });
    if (medio > 0) active.push({ band: "medio", count: medio });
    if (dificil > 0) active.push({ band: "dificil", count: dificil });

    var payload = {
      materia: fd.get("materia"),
      topico: fd.get("topico"),
      quantidade: qty,
      provider: fd.get("provider") || "",
      model: fd.get("model") || "",
      reasoning: fd.get("reasoning") || "medium",
    };

    if (active.length >= 2) {
      // Mixed (D-12): plano only; omit top-level dificuldade
      payload.plano = { facil: facil, medio: medio, dificil: dificil };
    } else if (active.length === 1) {
      // Uniform (D-13, D-14): legacy shape; quantidade = band count
      payload.dificuldade = active[0].band;
      payload.quantidade = active[0].count;
    }
    // Zero bands: editable quantidade only; soft-warn visible (D-11)
    return payload;
  }

  if (qtyInput) {
    qtyInput.addEventListener("input", function () {
      syncBandAvailability();
      updateSoftWarn();
    });
    qtyInput.addEventListener("change", function () {
      syncBandAvailability();
      updateSoftWarn();
    });
  }
  ["facil", "medio", "dificil"].forEach(function (name) {
    var el = form.querySelector('[name="' + name + '"]');
    if (el) {
      el.addEventListener("input", updateSoftWarn);
      el.addEventListener("change", updateSoftWarn);
    }
  });
  syncBandAvailability();
  updateSoftWarn();

  tabExercicios.addEventListener("click", function () {
    showTab("exercicios");
  });
  tabJson.addEventListener("click", function () {
    showTab("json");
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    clearError();
    updateSoftWarn();
    // Disable only submit; leave other fields editable (soft-warn never blocks)
    btn.disabled = true;
    btn.textContent = "Gerando…";

    var fd = new FormData(form);
    var payload = buildGerarPayload(fd);

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
