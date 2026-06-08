import { useState, useRef, useEffect } from 'react';
import type { FormEvent } from 'react';
import { Mic, Send, Globe, Camera, Monitor, CheckCircle } from 'lucide-react';
import { useStore } from '../store';
import { motion } from 'framer-motion';

const CenterPanel = () => {
  const { chat, sendCommand, isExecuting, isListening, setListening, fetchChat, interimTranscript } = useStore();
  const [input, setInput] = useState('');
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chat]);

  useEffect(() => {
    fetchChat();
  }, [fetchChat]);

  useEffect(() => {
    const handleFocus = () => {
      inputRef.current?.focus();
    };
    window.addEventListener('focus-input', handleFocus);
    return () => window.removeEventListener('focus-input', handleFocus);
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isExecuting) {
      sendCommand(input);
      setInput('');
    }
  };

  const handleQuickAction = (cmd: string) => {
    if (!isExecuting) sendCommand(cmd);
  };

  return (
    <div className="flex-1 flex flex-col h-full gap-4 min-w-0">
      <div className="text-center pt-0 pb-3 shrink-0 -mt-2">
        <h1 className="text-[7.5rem] leading-none maverik-title pb-1">
          MAVERIK
        </h1>
        <div className="flex items-center justify-center gap-4 mt-2">
          <div className="h-px w-20 bg-gradient-to-r from-transparent to-[#39ff14]/70"></div>
          <p className="text-[#39ff14] text-[10px] tracking-[0.4em] font-bold">YOUR AI OPERATING SYSTEM</p>
          <div className="h-px w-20 bg-gradient-to-l from-transparent to-[#39ff14]/70"></div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4 px-4 custom-scrollbar">
        {chat.map((msg, idx) => (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            key={idx} 
            className="flex flex-col gap-1"
          >
            <div className={`p-4 rounded-xl max-w-[90%] glass-panel relative ${
              msg.role === 'user' ? 'ml-auto bg-black/40' : 'mr-auto bg-[#141414]/90'
            }`}>
              <div className="flex items-start gap-3 mb-2">
                <div className={`w-8 h-8 rounded-full flex shrink-0 items-center justify-center overflow-hidden border ${
                  msg.role === 'user' ? 'border-white/20 bg-gray-600' : 'border-[#39ff14]/30 bg-black'
                }`}>
                  {msg.role === 'user' ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white/50"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  ) : (
                    <div className="w-full h-full relative flex items-center justify-center">
                      <div className="absolute inset-1 rounded-full border border-dashed border-[#39ff14]/50 animate-spin-slow"></div>
                      <div className="w-2 h-2 rounded-full bg-[#39ff14] shadow-[0_0_8px_#39ff14]"></div>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-bold text-white/80 uppercase tracking-wider">
                      {msg.role === 'user' ? 'You' : 'MAVERIK'}
                    </span>
                    <span className="text-[10px] text-white/40">
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <p className="text-sm text-white/90 leading-relaxed break-words">{msg.content}</p>
                </div>
              </div>
              
              {msg.action_type && (
                <div className="mt-3 pt-3 border-t border-white/10 flex items-center justify-between text-[11px]">
                  <span className="text-white/50 flex items-center gap-1.5">
                    <Globe size={12} className="text-white/40" /> Action: {msg.action_type}
                  </span>
                  <span className="text-[#39ff14] flex items-center gap-1.5">
                    Status: {msg.status} <CheckCircle size={12} className="text-[#39ff14]" />
                  </span>
                </div>
              )}
            </div>
          </motion.div>
        ))}
        <div ref={endOfMessagesRef} />
      </div>

      <div className="flex justify-center gap-2 py-2 shrink-0">
        <button onClick={() => handleQuickAction("Open Chrome")} className="glass-button px-4 py-2 flex items-center gap-2 text-xs font-medium text-white/70 hover:text-white group">
          <div className="w-5 h-5 rounded-full bg-white flex items-center justify-center">
            <Globe size={12} className="text-red-500" />
          </div>
          Open Chrome
        </button>
        <button onClick={() => handleQuickAction("Take Screenshot")} className="glass-button px-4 py-2 flex items-center gap-2 text-xs font-medium text-white/70 hover:text-white group">
          <Camera size={16} className="text-gray-300 group-hover:text-white transition-colors" /> Take Screenshot
        </button>
        <button onClick={() => handleQuickAction("Search Google")} className="glass-button px-4 py-2 flex items-center gap-2 text-xs font-medium text-white/70 hover:text-white group">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
          </svg> Search Google
        </button>
        <button onClick={() => handleQuickAction("System Info")} className="glass-button px-4 py-2 flex items-center gap-2 text-xs font-medium text-white/70 hover:text-white group">
          <Monitor size={16} className="text-gray-300 group-hover:text-white transition-colors" /> System Info
        </button>
      </div>

      <div className="shrink-0">
        <form onSubmit={handleSubmit} className="glass-panel p-2 flex items-center gap-2 rounded-2xl bg-black/60 backdrop-blur-xl border-white/5">
          <input 
            type="text" 
            ref={inputRef}
            value={input || interimTranscript}
            onChange={(e) => setInput(e.target.value)}
            placeholder={isListening ? "Listening..." : "Type a command or ask anything..."}
            className={`flex-1 bg-transparent border-none outline-none text-sm px-4 placeholder-white/30 ${interimTranscript ? 'text-[#39ff14]' : 'text-white'}`}
            disabled={isExecuting}
          />
          <button 
            type="button"
            onClick={() => setListening(!isListening)}
            className={`w-10 h-10 rounded-full flex shrink-0 items-center justify-center transition-all ${
              isListening ? 'bg-[#39ff14]/20 text-[#39ff14] glow-border' : 'bg-[#39ff14]/20 text-[#39ff14] hover:bg-[#39ff14]/30'
            }`}
          >
            <Mic size={18} />
          </button>
          
          {useStore((state) => state.isPlayingAudio) ? (
            <button 
              type="button"
              onClick={() => useStore.getState().stopTTS()}
              className="w-10 h-10 rounded-full bg-red-500/20 hover:bg-red-500/30 text-red-500 flex shrink-0 items-center justify-center transition-all glow-border-red"
              title="Stop speaking"
            >
              <div className="w-3 h-3 bg-red-500 rounded-sm"></div>
            </button>
          ) : (
            <button 
              type="submit"
              disabled={!input.trim() || isExecuting}
              className="w-10 h-10 rounded-full bg-white/10 hover:bg-white/20 text-white flex shrink-0 items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <Send size={16} />
            </button>
          )}
        </form>
      </div>
    </div>
  );
};

export default CenterPanel;
