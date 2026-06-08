import { create } from 'zustand';

interface SystemStats {
  cpu: { percent: number; name: string };
  ram: { percent: number; used_gb: number; total_gb: number };
  disk: { percent: number; used_gb: number; total_gb: number };
  network: { bytes_sent: number; bytes_recv: number };
  battery: { percent: number; is_plugged: boolean };
  uptime: number;
}

export interface Timer {
  id: string;
  name: string;
  remaining_seconds: number;
  status: string;
}

interface CommandHistory {
  id: number;
  command: string;
  action_type: string;
  status: string;
  execution_time: number;
  timestamp: string;
}

interface ChatMessage {
  id: number;
  role: string;
  content: string;
  action_type: string;
  status: string;
  timestamp: string;
}

interface AppState {
  systemStats: SystemStats | null;
  history: CommandHistory[];
  chat: ChatMessage[];
  timers: Timer[];
  isListening: boolean;
  isExecuting: boolean;
  isPlayingAudio: boolean;
  currentAudio: HTMLAudioElement | null;
  
  setListening: (val: boolean) => void;
  setExecuting: (val: boolean) => void;
  fetchSystemStats: () => Promise<void>;
  fetchTimers: () => Promise<void>;
  fetchHistory: () => Promise<void>;
  fetchChat: () => Promise<void>;
  sendCommand: (command: string) => Promise<void>;
  clearHistory: () => Promise<void>;
  analyzeScreenshot: () => Promise<void>;
  playTTS: (text: string) => Promise<void>;
  stopTTS: () => void;
  currentSearchResults: any[];
  setCurrentSearchResults: (results: any[]) => void;
  interimTranscript: string;
  setInterimTranscript: (text: string) => void;
}

const API_URL = "http://127.0.0.1:8000/api";

export const useStore = create<AppState>((set, get) => ({
  systemStats: null,
  history: [],
  chat: [],
  timers: [],
  isListening: false,
  isExecuting: false,
  isPlayingAudio: false,
  currentAudio: null,
  currentSearchResults: [],
  interimTranscript: '',

  setCurrentSearchResults: (results) => set({ currentSearchResults: results }),
  setListening: (val) => set({ isListening: val }),
  setExecuting: (val) => set({ isExecuting: val }),
  setInterimTranscript: (val) => set({ interimTranscript: val }),

  fetchSystemStats: async () => {
    try {
      const res = await fetch(`${API_URL}/system-stats`);
      if (res.ok) {
        const data = await res.json();
        set({ systemStats: data });
      }
    } catch (e) {
      console.error("Backend not reachable");
    }
  },

  fetchTimers: async () => {
    try {
      const res = await fetch(`${API_URL}/timers`);
      if (res.ok) {
        const data = await res.json();
        const currentTimers = get().timers;
        data.forEach((t: Timer) => {
           if (t.status === "finished") {
             const existing = currentTimers.find(x => x.id === t.id);
             if (!existing || existing.status === "running") {
               get().playTTS(`Your ${t.name} has finished.`);
             }
           }
        });
        set({ timers: data });
      }
    } catch (e) {
      console.error("Failed to fetch timers");
    }
  },

  fetchHistory: async () => {
    try {
      const res = await fetch(`${API_URL}/history`);
      if (res.ok) {
        const data = await res.json();
        set({ history: data });
      }
    } catch (e) {
      console.error(e);
    }
  },

  fetchChat: async () => {
    try {
      const res = await fetch(`${API_URL}/chat`);
      if (res.ok) {
        const data = await res.json();
        set({ chat: data });
      }
    } catch (e) {
      console.error(e);
    }
  },

  sendCommand: async (command: string) => {
    get().stopTTS(); // Stop any currently playing audio
    set({ isExecuting: true });
    // Optimistic UI for user message
    const tempMsg: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: command,
      action_type: '',
      status: '',
      timestamp: new Date().toISOString()
    };
    set((state) => ({ chat: [...state.chat, tempMsg] }));
    
    try {
      const res = await fetch(`${API_URL}/command`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command }),
      });
      const data = await res.json();
      await get().fetchHistory();
      await get().fetchChat();
      
      if (data && data.response) {
        get().playTTS(data.response);
      }
      if (data && (data.intent === 'search_file' || data.intent === 'search_folder') && data.details) {
        try {
          const results = JSON.parse(data.details);
          get().setCurrentSearchResults(results);
        } catch(e) {}
      }
    } catch (e) {
      console.error(e);
    } finally {
      set({ isExecuting: false });
    }
  },

  clearHistory: async () => {
    get().stopTTS();
    try {
      await fetch(`${API_URL}/history`, { method: "DELETE" });
      await fetch(`${API_URL}/chat`, { method: "DELETE" });
      await get().fetchHistory();
      await get().fetchChat();
    } catch (e) {
      console.error(e);
    }
  },

  analyzeClipboard: async () => {
    get().stopTTS();
    set({ isExecuting: true });
    try {
      const res = await fetch(`${API_URL}/analyze-clipboard`, { method: "POST" });
      const data = await res.json();
      await get().fetchHistory();
      await get().fetchChat();
      if (data && data.analysis) {
        get().playTTS(data.analysis);
      }
    } catch (e) {
      console.error(e);
    } finally {
      set({ isExecuting: false });
    }
  },

  analyzeScreenshot: async () => {
    get().stopTTS();
    set({ isExecuting: true });
    try {
      const res = await fetch(`${API_URL}/analyze-screenshot`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ region: false }) });
      const data = await res.json();
      await get().fetchHistory();
      await get().fetchChat();
      if (data && data.analysis) {
        get().playTTS(data.analysis);
      }
    } catch (e) {
      console.error(e);
    } finally {
      set({ isExecuting: false });
    }
  },

  stopTTS: () => {
    const { currentAudio } = get();
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
    }
    window.speechSynthesis.cancel();
    set({ isPlayingAudio: false, currentAudio: null });
  },

  playTTS: async (text: string) => {
    get().stopTTS(); // Ensure any previous audio is stopped
    set({ isPlayingAudio: true });
    
    try {
      const res = await fetch(`${API_URL}/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: text }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.status === "success" && data.audioContent) {
          const audio = new Audio("data:audio/mp3;base64," + data.audioContent);
          
          audio.onended = () => {
            set({ isPlayingAudio: false, currentAudio: null });
          };
          audio.onerror = () => {
            set({ isPlayingAudio: false, currentAudio: null });
          };
          
          set({ currentAudio: audio });
          audio.play();
          return;
        }
      }
    } catch (e) {
      console.error("TTS API failed, falling back to browser TTS", e);
    }
    
    // Fallback to browser synthesis
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.onend = () => set({ isPlayingAudio: false });
    utterance.onerror = () => set({ isPlayingAudio: false });
    window.speechSynthesis.speak(utterance);
  }
}));
