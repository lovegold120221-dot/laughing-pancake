(() => {
  async function createRoleplaySession() {
    const voiceName = document.getElementById("roleplayVoice").value || "Batman";

    const data = await EburonPlayground.apiPost(
      "/v1/eburon/talkhuman/roleplay/sessions",
      {
        model: "talkhuman-3.1",
        voice_name: voiceName,
        roleplay_mode: "cinematic_live_monologue",
        output_mode: "audio_with_text_events",
        performance_profile: {
          duration_minutes: 5,
          target_words_min: 650,
          target_words_max: 800,
          emotional_intensity: 0.75,
          cinematic_detail: 0.85,
          human_pause_level: 0.55,
          performance_cue_level: 0.35,
          character_commitment: 0.95
        }
      }
    );

    EburonPlayground.state.roleplaySessionId = data.session_id;
    EburonPlayground.setStatus(`RolePlay session: ${data.session_id}`, "connected");
    return data;
  }

  async function performRoleplay() {
    let sessionId = EburonPlayground.state.roleplaySessionId;

    if (!sessionId) {
      const session = await createRoleplaySession();
      sessionId = session.session_id;
    }

    const prompt = document.getElementById("roleplayPrompt").value.trim();
    const tone = document.getElementById("roleplayTone").value || "auto";

    if (!prompt) {
      throw new Error("RolePlay prompt is required.");
    }

    return EburonPlayground.apiPost(
      `/v1/eburon/talkhuman/roleplay/sessions/${sessionId}/perform`,
      {
        topic_or_roleplay_request: prompt,
        tone,
        start_immediately_in_character: true,
        allow_performance_cues: true,
        end_of_turn: true
      }
    );
  }

  async function continueRoleplay() {
    const sessionId = EburonPlayground.state.roleplaySessionId;
    if (!sessionId) throw new Error("Create a RolePlay session first.");

    return EburonPlayground.apiPost(
      `/v1/eburon/talkhuman/roleplay/sessions/${sessionId}/continue`,
      {
        instruction: "continue",
        resume_from_last_emotional_point: true
      }
    );
  }

  async function interruptRoleplay() {
    const sessionId = EburonPlayground.state.roleplaySessionId;
    if (!sessionId) throw new Error("Create a RolePlay session first.");

    return EburonPlayground.apiPost(
      `/v1/eburon/talkhuman/roleplay/sessions/${sessionId}/interrupt`,
      {}
    );
  }

  function connectRoleplayWs() {
    if (EburonPlayground.state.roleplayWs) {
      EburonPlayground.state.roleplayWs.close();
    }

    const wsUrl = EburonPlayground.toWsUrl(
      EburonPlayground.getBaseEndpoint(),
      "/v1/eburon/talkhuman/roleplay/ws"
    );

    const ws = new WebSocket(wsUrl);
    EburonPlayground.state.roleplayWs = ws;

    ws.onopen = () => {
      EburonPlayground.setStatus("RolePlay WS connected", "connected");

      const prompt = document.getElementById("roleplayPrompt").value.trim();
      const tone = document.getElementById("roleplayTone").value || "auto";
      const voiceName = document.getElementById("roleplayVoice").value || "Batman";

      if (prompt) {
        ws.send(JSON.stringify({
          type: "start_roleplay",
          model: "talkhuman-3.1",
          topic_or_roleplay_request: prompt,
          tone,
          voice_name: voiceName,
          allow_performance_cues: true
        }));
      }
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      EburonPlayground.logApi({
        transport: "websocket",
        path: "/v1/eburon/talkhuman/roleplay/ws",
        event: data,
      });

      if (data.type === "roleplay_text") {
        const output = document.getElementById("roleplayTextOutput");
        output.textContent += data.text;
      }

      if (data.type === "roleplay_audio") {
        // TODO:
        // Decode base64 PCM and play using pcm-player.js.
      }
    };

    ws.onclose = () => {
      EburonPlayground.setStatus("RolePlay WS closed", "idle");
    };

    ws.onerror = () => {
      EburonPlayground.setStatus("RolePlay WS error", "error");
    };
  }

  function closeRoleplayWs() {
    if (EburonPlayground.state.roleplayWs) {
      EburonPlayground.state.roleplayWs.close();
      EburonPlayground.state.roleplayWs = null;
    }
  }

  window.EburonRoleplay = {
    createRoleplaySession,
    performRoleplay,
    continueRoleplay,
    interruptRoleplay,
    connectRoleplayWs,
    closeRoleplayWs,
  };
})();
