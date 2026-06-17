(() => {
  function bindTabs() {
    const buttons = document.querySelectorAll("[data-tab]");
    const panels = document.querySelectorAll(".panel");

    function activateTab(tab, activeButton) {
      buttons.forEach((b) => b.classList.remove("active"));
      panels.forEach((p) => p.classList.remove("active"));

      const navButton = document.querySelector(`.tab-nav button[data-tab="${tab}"]`);
      (navButton || activeButton)?.classList.add("active");
      document.getElementById(`tab-${tab}`)?.classList.add("active");
    }

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        activateTab(button.dataset.tab, button);
      });
    });
  }

  function bindTalkhuman() {
    document.getElementById("createTalkhumanSession")?.addEventListener("click", async () => {
      try {
        await EburonTalkhuman.createTalkhumanSession();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("sendTalkhumanMessage")?.addEventListener("click", async () => {
      try {
        await EburonTalkhuman.sendTalkhumanMessage();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("connectTalkhumanWs")?.addEventListener("click", () => {
      EburonTalkhuman.connectTalkhumanWs();
    });

    document.getElementById("closeTalkhumanWs")?.addEventListener("click", () => {
      EburonTalkhuman.closeTalkhumanWs();
    });
  }

  function bindRoleplay() {
    document.getElementById("createRoleplaySession")?.addEventListener("click", async () => {
      try {
        await EburonRoleplay.createRoleplaySession();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("performRoleplay")?.addEventListener("click", async () => {
      try {
        await EburonRoleplay.performRoleplay();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("continueRoleplay")?.addEventListener("click", async () => {
      try {
        await EburonRoleplay.continueRoleplay();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("interruptRoleplay")?.addEventListener("click", async () => {
      try {
        await EburonRoleplay.interruptRoleplay();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("connectRoleplayWs")?.addEventListener("click", () => {
      EburonRoleplay.connectRoleplayWs();
    });

    document.getElementById("closeRoleplayWs")?.addEventListener("click", () => {
      EburonRoleplay.closeRoleplayWs();
    });
  }

  function bindTranslate() {
    document.getElementById("runTextTranslate")?.addEventListener("click", async () => {
      try {
        await EburonTranslate.runTextTranslate();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("runImageTranslate")?.addEventListener("click", async () => {
      try {
        await EburonTranslate.runImageTranslate();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("runDocumentTranslate")?.addEventListener("click", async () => {
      try {
        await EburonTranslate.runDocumentTranslate();
      } catch (err) {
        alert(err.message);
      }
    });

    document.getElementById("runWebsiteTranslate")?.addEventListener("click", async () => {
      try {
        await EburonTranslate.runWebsiteTranslate();
      } catch (err) {
        alert(err.message);
      }
    });
  }

  function replaceSelectOptions(select, options, selectedValue) {
    if (!select) return;

    if (!options.length) {
      const option = document.createElement("option");
      option.textContent = "No mappings available";
      option.disabled = true;
      select.replaceChildren(option);
      return;
    }

    select.replaceChildren(
      ...options.map((option) => {
        const item = document.createElement("option");
        item.value = option.value;
        item.textContent = option.label;
        item.selected = option.value === selectedValue;
        return item;
      })
    );
  }

  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  function formatCount(value, label) {
    const count = Number(value || 0).toLocaleString();
    return `${count} ${label}`;
  }

  function populateVoiceCatalog(voices) {
    const catalog = document.getElementById("voiceCatalog");
    if (!catalog) return;

    catalog.replaceChildren(
      ...voices.map((voice) => {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = voice.alias;
        chip.title = voice.description || voice.style || voice.alias;
        return chip;
      })
    );
  }

  async function loadVoices() {
    const data = await EburonPlayground.apiGet("/v1/eburon/talkhuman/voices");
    const voices = Array.isArray(data.voices) ? data.voices : [];
    const options = voices.map((voice) => ({
      value: voice.alias,
      label: `${voice.alias} - ${voice.style}${voice.description ? ` - ${voice.description}` : ""}`,
    }));
    const voiceCount = data.count || voices.length;

    replaceSelectOptions(document.getElementById("talkhumanVoice"), options, "Phoenix");
    replaceSelectOptions(document.getElementById("roleplayVoice"), options, "Batman");
    populateVoiceCatalog(voices);
    setText("voiceCount", formatCount(voiceCount, "aliases"));
    setText("voiceMetric", formatCount(voiceCount, "voices"));
    setText("voiceMappingCount", voiceCount.toLocaleString());
  }

  async function loadLanguages() {
    const data = await EburonPlayground.apiGet("/v1/eburon/translate/languages");
    const sourceLanguages = Array.isArray(data.source_languages) ? data.source_languages : [];
    const targetLanguages = Array.isArray(data.target_languages) ? data.target_languages : [];
    const sourceOptions = sourceLanguages.map((language) => ({
      value: language.code,
      label: `${language.name} (${language.code})`,
    }));
    const targetOptions = targetLanguages.map((language) => ({
      value: language.code,
      label: `${language.name} (${language.code})`,
    }));
    const sourceCount = data.source_count || sourceLanguages.length;
    const targetCount = data.target_count || targetLanguages.length;

    replaceSelectOptions(document.getElementById("translateSource"), sourceOptions, "auto");
    replaceSelectOptions(document.getElementById("translateTarget"), targetOptions, "es");
    setText("languageCount", `${sourceCount.toLocaleString()} source / ${targetCount.toLocaleString()} target`);
    setText("languageMetric", formatCount(targetCount, "targets"));
    setText("sourceLanguageCount", sourceCount.toLocaleString());
    setText("targetLanguageCount", targetCount.toLocaleString());
  }

  async function loadDropdownMetadata() {
    try {
      EburonPlayground.setStatus("Loading mappings", "idle");
      await Promise.all([loadVoices(), loadLanguages()]);
      EburonPlayground.setStatus("Mappings ready", "connected");
    } catch (err) {
      EburonPlayground.setStatus("Mapping load failed", "error");
      setText("voiceCount", "Unavailable");
      setText("voiceMetric", "Unavailable");
      setText("voiceMappingCount", "Unavailable");
      setText("languageCount", "Unavailable");
      setText("languageMetric", "Unavailable");
      setText("sourceLanguageCount", "Unavailable");
      setText("targetLanguageCount", "Unavailable");
      EburonPlayground.logApi({
        type: "metadata_load_error",
        message: err.message,
      });
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindTabs();
    bindTalkhuman();
    bindRoleplay();
    bindTranslate();
    loadDropdownMetadata();
  });
})();
