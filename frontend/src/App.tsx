import { useEffect, useRef } from 'react';
import LeftPanel from './components/LeftPanel';
import CenterPanel from './components/CenterPanel';
import RightPanel from './components/RightPanel';
import { useStore } from './store';

function App() {
  const { fetchSystemStats, fetchTimers, fetchHistory, fetchChat, isListening, setListening, sendCommand } = useStore();
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    fetchSystemStats();
    fetchHistory();
    fetchChat();
    
    const interval = setInterval(() => {
      fetchSystemStats();
      fetchTimers();
    }, 2000);
    return () => clearInterval(interval);
  }, [fetchSystemStats, fetchTimers, fetchHistory, fetchChat]);

  // Web Speech API Setup
  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false; // Automatically stops when user stops speaking
      recognitionRef.current.interimResults = true; // Get interim results as they speak
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = '';
        let interim = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interim += event.results[i][0].transcript;
          }
        }
        
        useStore.getState().setInterimTranscript(interim);
        
        if (finalTranscript.trim()) {
          useStore.getState().setInterimTranscript('');
          sendCommand(finalTranscript.trim());
          setListening(false);
        }
      };
      
      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        useStore.getState().setInterimTranscript('');
        setListening(false);
      };
      
      recognitionRef.current.onend = () => {
        setListening(false);
      };
    }
  }, [sendCommand, setListening]);

  // Web Speech API Toggle
  useEffect(() => {
    if (isListening && recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch(e) {}
    } else if (!isListening && recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch(e) {}
    }
  }, [isListening]);

  return (
    <div className="flex flex-col h-screen w-screen font-sans overflow-hidden bg-transparent text-white relative">
      {/* Global Header */}
      <header className="h-16 flex items-center justify-between px-6 border-b border-white/5 bg-black/40 backdrop-blur-md z-10 shrink-0">
        <div className="flex items-center gap-4">
          <button className="text-white/60 hover:text-white transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
          </button>
          <span className="text-xl font-bold tracking-widest text-white">MAVERIK</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 border border-white/10 rounded-full px-3 py-1 bg-white/5">
            <div className="w-2 h-2 rounded-full bg-[#39ff14] shadow-[0_0_8px_#39ff14]"></div>
            <span className="text-[10px] font-semibold text-white/80 tracking-widest">ONLINE</span>
          </div>
          <div className="w-8 h-8 rounded-full border border-white/20 overflow-hidden flex items-center justify-center bg-white/5">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white/50"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          </div>
        </div>
      </header>

      {/* Main 3-Panel Content */}
      <div className="flex flex-1 p-6 gap-6 min-h-0">
        <LeftPanel />
        <CenterPanel />
        <RightPanel />
      </div>

      {/* Global Footer */}
      <footer className="h-10 flex items-center justify-between px-6 border-t border-white/5 bg-black/40 backdrop-blur-md z-10 shrink-0 text-[10px] text-white/40 tracking-wider">
        <span>MAVERIK v1.0.0</span>
        <span>© 2025 Maverik AI Systems • All Rights Reserved</span>
        <span>Engineered for Performance. Built for You.</span>
      </footer>
    </div>
  );
}

export default App;
