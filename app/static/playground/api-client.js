(() => {
  const state = {
    talkhumanSessionId: null,
    roleplaySessionId: null,
    talkhumanWs: null,
    roleplayWs: null,
  };

  function getBaseEndpoint() {
    return document.getElementById("baseEndpoint")?.value?.trim() || window.location.origin;
  }

  function getAuthHeaders() {
    const token = document.getElementById("authToken")?.value?.trim();

    const headers = {
      "Content-Type": "application/json",
    };

    if (token) {
      headers.Authorization = token.startsWith("Bearer ") ? token : `Bearer ${token}`;
    }

    return headers;
  }

  function toWsUrl(httpUrl, path) {
    const base = httpUrl.replace(/^http/, "ws").replace(/\/$/, "");
    return `${base}${path}`;
  }

  async function apiPost(path, body) {
    const res = await fetch(`${getBaseEndpoint()}${path}`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(body),
    });

    const data = await res.json().catch(() => ({}));

    logApi({
      method: "POST",
      path,
      status: res.status,
      response: data,
    });

    if (!res.ok) {
      throw new Error(data?.error?.message || `Request failed: ${res.status}`);
    }

    return data;
  }

  async function apiGet(path) {
    const res = await fetch(`${getBaseEndpoint()}${path}`, {
      method: "GET",
      headers: getAuthHeaders(),
    });

    const data = await res.json().catch(() => ({}));

    logApi({
      method: "GET",
      path,
      status: res.status,
      response: data,
    });

    if (!res.ok) {
      throw new Error(data?.error?.message || `Request failed: ${res.status}`);
    }

    return data;
  }

  async function apiDelete(path) {
    const res = await fetch(`${getBaseEndpoint()}${path}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    });

    const data = await res.json().catch(() => ({}));

    logApi({
      method: "DELETE",
      path,
      status: res.status,
      response: data,
    });

    return data;
  }

  function logApi(entry) {
    const logs = document.getElementById("apiLogs");
    if (!logs) return;

    logs.textContent =
      `${new Date().toISOString()}\n${JSON.stringify(entry, null, 2)}\n\n` +
      logs.textContent;
  }

  function setStatus(text, mode = "idle") {
    const status = document.getElementById("connectionStatus");
    if (!status) return;
    status.textContent = text;
    status.className = `status ${mode}`;
  }

  window.EburonPlayground = {
    state,
    getBaseEndpoint,
    getAuthHeaders,
    toWsUrl,
    apiGet,
    apiPost,
    apiDelete,
    logApi,
    setStatus,
  };
})();
