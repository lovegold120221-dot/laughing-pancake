(() => {
  async function runTextTranslate() {
    const text = document.getElementById("translateTextInput").value.trim();
    const source = document.getElementById("translateSource").value || "auto";
    const target = document.getElementById("translateTarget").value || "es";

    if (!text) throw new Error("Translation text is required.");

    const data = await EburonPlayground.apiPost("/v1/eburon/translate/text", {
      model: "translatehuman-3.1",
      source_language: source,
      target_language: target,
      text,
      format: "text",
      preserve_tone: true,
    });

    document.getElementById("translateTextOutput").textContent = data.translated_text;
    return data;
  }

  async function runImageTranslate() {
    const fileInput = document.getElementById("imageTranslateFile");
    const file = fileInput.files[0];
    if (!file) throw new Error("Please select an image file.");

    const reader = new FileReader();
    reader.onload = async () => {
      const base64 = reader.result.split(",")[1];
      const data = await EburonPlayground.apiPost("/v1/eburon/translate/images", {
        model: "translatehuman-3.1",
        source_language: "auto",
        target_language: document.getElementById("translateTarget").value || "es",
        image: {
          mime_type: file.type,
          data: base64,
        },
        output_mode: "text_blocks",
      });
      document.getElementById("imageTranslateOutput").textContent = JSON.stringify(data, null, 2);
    };
    reader.readAsDataURL(file);
  }

  async function runDocumentTranslate() {
    const fileInput = document.getElementById("documentTranslateFile");
    const file = fileInput.files[0];
    if (!file) throw new Error("Please select a document file.");

    const reader = new FileReader();
    reader.onload = async () => {
      const base64 = reader.result.split(",")[1];
      const data = await EburonPlayground.apiPost("/v1/eburon/translate/documents", {
        model: "translatehuman-3.1",
        source_language: "auto",
        target_language: document.getElementById("translateTarget").value || "es",
        document: {
          filename: file.name,
          mime_type: file.type,
          data: base64,
        },
        preserve_layout: true,
      });
      document.getElementById("documentTranslateOutput").textContent = JSON.stringify(data, null, 2);
    };
    reader.readAsDataURL(file);
  }

  async function runWebsiteTranslate() {
    const url = document.getElementById("websiteTranslateUrl").value.trim();
    if (!url) throw new Error("Website URL is required.");

    const data = await EburonPlayground.apiPost("/v1/eburon/translate/websites", {
      model: "translatehuman-3.1",
      source_language: "auto",
      target_language: document.getElementById("translateTarget").value || "es",
      url,
      mode: "single_page",
      preserve_links: true,
      preserve_html_structure: true,
    });
    document.getElementById("websiteTranslateOutput").textContent = JSON.stringify(data, null, 2);
  }

  window.EburonTranslate = {
    runTextTranslate,
    runImageTranslate,
    runDocumentTranslate,
    runWebsiteTranslate,
  };
})();
