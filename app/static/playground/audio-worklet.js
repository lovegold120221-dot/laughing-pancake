// app/static/playground/audio-worklet.js
// Placeholder for PCM audio processing worklet
class AudioWorklet extends AudioWorkletProcessor {
    process(inputs, outputs, parameters) {
        return true;
    }
}
registerProcessor('pcm-processor', AudioWorklet);
