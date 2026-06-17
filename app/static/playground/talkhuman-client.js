(() => {
  async function createTalkhumanSession() {
    const voiceName = document.getElementById("talkhumanVoice")?.value || "Phoenix";

    const data = await EburonPlayground.apiPost(
      "/v1/eburon/talkhuman/sessions",
      {
        model: "talkhuman-3.1",
        voice_name: voiceName,
        personality: "normal_human",
        expression: {
            allow_laughs: true,
            allow_giggles: true,
            allow_sighs: true,
            allow_soft_pauses: true,
            allow_backchanneling: true,
            allow_emotional_reflection: true,
            expression_style: "normal_human"
        },
        voice_profile: {
            warmth: 0.75,
            emotional_range: 0.8,
            laughter_frequency: 0.25,
            giggle_frequency: 0.15,
            breathiness: 0.25,
            hesitation_naturalness: 0.35,
            empathy_level: 0.85,
            conversational_energy: 0.65,
            interruption_sensitivity: 0.75
        }
      }
    );

    EburonPlayground.state.talkhumanSessionId = data.session_id;
    EburonPlayground.setStatus(`TalkHuman session: ${data.session_id}`, "connected");
    return data;
  }

  async function sendTalkhumanMessage() {
    let sessionId = EburonPlayground.state.talkhumanSessionId;

    if (!sessionId) {
      const session = await createTalkhumanSession();
      sessionId = session.session_id;
    }

    const text = document.getElementById("talkhumanMessage").value.trim();
    if (!text) throw new Error("Message text is required.");

    return EburonPlayground.apiPost(
      `/v1/eburon/talkhuman/sessions/${sessionId}/message`,
      {
        text,
        end_of_turn: true,
        emotional_intent: "neutral",
        humanize: true
      }
    );
  }

  function connectTalkhumanWs() {
    if (EburonPlayground.state.talkhumanWs) {
      EburonPlayground.state.talkhumanWs.close();
    }

    const wsUrl = EburonPlayground.toWsUrl(
      EburonPlayground.getBaseEndpoint(),
      "/v1/eburon/talkhuman/ws"
    );

    const ws = new WebSocket(wsUrl);
    EburonPlayground.state.talkhumanWs = ws;

    ws.onopen = () => {
      EburonPlayground.setStatus("TalkHuman WS connected", "connected");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      EburonPlayground.logApi({
        transport: "websocket",
        path: "/v1/eburon/talkhuman/ws",
        event: data,
      });
    };

    ws.onclose = () => {
      EburonPlayground.setStatus("TalkHuman WS closed", "idle");
    };

    ws.onerror = () => {
      EburonPlayground.setStatus("TalkHuman WS error", "error");
    };
  }

  function closeTalkhumanWs() {
    if (EburonPlayground.state.talkhumanWs) {
      EburonPlayground.state.talkhumanWs.close();
      EburonPlayground.state.talkhumanWs = null;
    }
  }

  window.EburonTalkhuman = {
    createTalkhumanSession,
    sendTalkhumanMessage,
    connectTalkhumanWs,
    closeTalkhumanWs,
  };
})();
