(() => {
  function bindTabs() {
    const buttons = document.querySelectorAll("[data-tab]");
    const panels = document.querySelectorAll(".panel");

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const tab = button.dataset.tab;

        buttons.forEach((b) => b.classList.remove("active"));
        panels.forEach((p) => p.classList.remove("active"));

        button.classList.add("active");
        document.getElementById(`tab-${tab}`)?.classList.add("active");
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

  async function loadVoices() {
    const data = await EburonPlayground.apiGet("/v1/eburon/talkhuman/voices");
    const options = data.voices.map((voice) => ({
      value: voice.alias,
      label: `${voice.display_name} · ${voice.style}`,
    }));

    replaceSelectOptions(document.getElementById("talkhumanVoice"), options, "Phoenix");
    replaceSelectOptions(document.getElementById("roleplayVoice"), options, "Batman");
  }

  async function loadLanguages() {
    const data = await EburonPlayground.apiGet("/v1/eburon/translate/languages");
    const sourceOptions = data.source_languages.map((language) => ({
      value: language.code,
      label: `${language.name} (${language.code})`,
    }));
    const targetOptions = data.target_languages.map((language) => ({
      value: language.code,
      label: `${language.name} (${language.code})`,
    }));

    replaceSelectOptions(document.getElementById("translateSource"), sourceOptions, "auto");
    replaceSelectOptions(document.getElementById("translateTarget"), targetOptions, "es");
  }

  async function loadDropdownMetadata() {
    try {
      await Promise.all([loadVoices(), loadLanguages()]);
    } catch (err) {
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
