import { useStore } from '../store';
import { Search, Code, FileText, Settings, Terminal, Monitor, Play, Folder, Trash2, Clock as ClockIcon, Battery, Wifi, Activity } from 'lucide-react';
import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

const formatUptime = (seconds: number) => {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
};

const formatTime = (seconds: number) => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
};

const RightPanel = () => {
  const { systemStats, timers, isListening, isExecuting, sendCommand, currentSearchResults } = useStore();
  const [time, setTime] = useState(new Date());
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [recentFiles, setRecentFiles] = useState<any[]>([]);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/recent-files')
      .then(res => res.json())
      .then(data => {
        if (data && data.results) {
          setRecentFiles(data.results);
          setSearchResults(data.results);
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (currentSearchResults && currentSearchResults.length > 0) {
      setSearchResults(currentSearchResults);
    }
  }, [currentSearchResults]);

  const handleQuickAccess = (cmd: string) => {
    if (!isExecuting) sendCommand(cmd);
  };

  return (
    <div className="w-1/4 h-full flex flex-col gap-4 min-w-[300px] overflow-y-auto custom-scrollbar pr-2 pb-4">
      {/* Time & Date Widget */}
      <div className="glass-panel p-4 shrink-0 flex items-center justify-between">
        <div>
          <div className="text-3xl font-light tracking-widest">{time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
          <div className="text-[10px] text-white/50 uppercase tracking-widest mt-1">{time.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' })}</div>
        </div>
        <ClockIcon size={24} className="text-[#39ff14]/50" />
      </div>

      {/* Timers */}
      {timers && timers.filter(t => t.status === "running").length > 0 && (
        <div className="glass-panel p-4 shrink-0">
          <h2 className="text-xs text-white/50 tracking-wider font-semibold uppercase mb-3 px-2 flex items-center gap-2">
            <ClockIcon size={12} /> Active Timers
          </h2>
          <div className="space-y-2 px-2">
            {timers.filter(t => t.status === "running").map(t => (
              <div key={t.id} className="flex justify-between items-center bg-white/5 p-2 rounded border border-white/10">
                <span className="text-xs font-semibold">{t.name}</span>
                <span className="text-sm font-mono text-[#39ff14]">{formatTime(t.remaining_seconds)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Overview */}
      <div className="glass-panel p-4 shrink-0">
        <h2 className="text-xs text-white/50 tracking-wider font-semibold uppercase mb-4 px-2">System Overview</h2>
        
        {systemStats ? (
          <div className="space-y-4 px-2">
            <div className="flex items-center gap-4">
              <div className="relative w-12 h-12 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="24" cy="24" r="20" stroke="rgba(255,255,255,0.1)" strokeWidth="3" fill="none" />
                  <circle cx="24" cy="24" r="20" stroke="#39ff14" strokeWidth="3" fill="none" strokeDasharray={`${systemStats.cpu.percent * 1.25} 125`} strokeLinecap="round" />
                </svg>
                <span className="absolute text-[10px] font-semibold">{Math.round(systemStats.cpu.percent)}%</span>
              </div>
              <div>
                <p className="text-xs font-semibold text-white/90">CPU Usage</p>
                <p className="text-[9px] text-white/40 mt-0.5 truncate w-32">{systemStats.cpu.name}</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="relative w-12 h-12 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="24" cy="24" r="20" stroke="rgba(255,255,255,0.1)" strokeWidth="3" fill="none" />
                  <circle cx="24" cy="24" r="20" stroke="#39ff14" strokeWidth="3" fill="none" strokeDasharray={`${systemStats.ram.percent * 1.25} 125`} strokeLinecap="round" />
                </svg>
                <span className="absolute text-[10px] font-semibold">{Math.round(systemStats.ram.percent)}%</span>
              </div>
              <div>
                <p className="text-xs font-semibold text-white/90">RAM Usage</p>
                <p className="text-[9px] text-white/40 mt-0.5">{systemStats.ram.used_gb} GB / {systemStats.ram.total_gb} GB</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-2">
              <div className="bg-white/5 border border-white/10 rounded p-2 flex flex-col gap-1">
                <div className="flex items-center gap-1 text-white/50">
                  <Battery size={12} className={systemStats.battery.is_plugged ? "text-[#39ff14]" : ""} />
                  <span className="text-[9px] uppercase tracking-wider">Battery</span>
                </div>
                <span className="text-sm font-semibold">{Math.round(systemStats.battery.percent)}%</span>
              </div>
              <div className="bg-white/5 border border-white/10 rounded p-2 flex flex-col gap-1">
                <div className="flex items-center gap-1 text-white/50">
                  <Activity size={12} />
                  <span className="text-[9px] uppercase tracking-wider">Uptime</span>
                </div>
                <span className="text-sm font-semibold">{formatUptime(systemStats.uptime)}</span>
              </div>
            </div>

            <div className="bg-white/5 border border-white/10 rounded p-3 flex flex-col gap-2">
               <div className="flex items-center gap-2 text-white/50 mb-1">
                 <Wifi size={14} />
                 <span className="text-[10px] uppercase tracking-wider">Network Speed</span>
               </div>
               <div className="flex justify-between items-center">
                 <div className="flex flex-col">
                   <span className="text-[9px] text-white/40 uppercase">Download</span>
                   <span className="text-xs font-semibold text-blue-400">{(systemStats.network.download_bps / 1024 / 1024).toFixed(2)} MB/s</span>
                 </div>
                 <div className="flex flex-col text-right">
                   <span className="text-[9px] text-white/40 uppercase">Upload</span>
                   <span className="text-xs font-semibold text-purple-400">{(systemStats.network.upload_bps / 1024 / 1024).toFixed(2)} MB/s</span>
                 </div>
               </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-white/30 text-xs py-10">Loading System Data...</div>
        )}
      </div>

      <div className="glass-panel p-4 flex-1 flex flex-col items-center justify-center min-h-[280px]">
        <h2 className="text-xs text-white/50 tracking-wider font-semibold uppercase mb-2 w-full text-left px-2">Maverik Status</h2>
        
        <div className="flex-1 flex flex-col items-center justify-center w-full">
          <div className="relative w-32 h-32 flex items-center justify-center mb-6">
            <motion.div 
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 10, ease: "linear" }}
              className="absolute inset-0 border border-dashed border-[#39ff14]/30 rounded-full"
            />
            <motion.div 
              animate={{ rotate: -360 }}
              transition={{ repeat: Infinity, duration: 15, ease: "linear" }}
              className="absolute inset-3 border border-white/10 rounded-full"
            />
            <motion.div 
              animate={isExecuting ? { scale: [1, 1.05, 1] } : {}}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className={`absolute inset-6 rounded-full border-2 ${isListening || isExecuting ? 'border-[#39ff14]/50' : 'border-[#39ff14]/20'}`}
            />
            <motion.div 
              animate={isListening ? { scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] } : {}}
              transition={{ repeat: Infinity, duration: 1 }}
              className={`w-10 h-10 rounded-full ${isListening ? 'bg-[#39ff14] glow-border' : 'bg-[#39ff14]/30'} blur-[1px]`}
            />
            <div className="absolute w-3 h-3 rounded-full bg-white shadow-[0_0_10px_#fff]" />
          </div>

          <div className="text-center">
            <p className={`text-sm font-semibold ${isListening ? 'text-[#39ff14]' : 'text-[#39ff14]'}`}>
              {isListening ? 'Listening...' : isExecuting ? 'Executing...' : 'Ready and Listening'}
            </p>
            <p className="text-[10px] text-white/40 mt-1 uppercase tracking-wider">All systems operational</p>
            <div className="flex justify-center gap-1 mt-4 h-2">
               {Array.from({ length: 20 }).map((_, i) => (
                 <motion.div 
                   key={i}
                   animate={isListening ? { height: [2, Math.random() * 8 + 2, 2] } : { height: 2 }}
                   transition={{ repeat: Infinity, duration: 0.3 + Math.random() * 0.2 }}
                   className="w-[2px] bg-[#39ff14]/50 rounded-full"
                 />
               ))}
            </div>
          </div>
        </div>
      </div>

      <div className="glass-panel p-4 shrink-0 flex flex-col gap-3 min-h-[300px]">
        <h2 className="text-xs text-white/50 tracking-wider font-semibold uppercase px-2 flex items-center gap-2">
          <Search size={12} /> Maverik Search
        </h2>
        
        <div className="px-2">
          <input 
            type="text" 
            placeholder="Search files..." 
            className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-[#39ff14]/50 transition-colors placeholder:text-white/30"
            onChange={async (e) => {
              const val = e.target.value;
              if (val.length > 2) {
                try {
                  const res = await fetch(`http://127.0.0.1:8000/api/search?query=${encodeURIComponent(val)}`);
                  if (res.ok) {
                    const data = await res.json();
                    setSearchResults(data.results);
                  }
                } catch(err) {}
              } else if (val.length === 0) {
                setSearchResults(recentFiles);
              }
            }}
          />
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar px-2 space-y-2 mt-2">
          {searchResults.length === 0 && (
            <div className="text-center text-white/30 text-[10px] mt-4">No recent files</div>
          )}
          {searchResults.map((file: any, i: number) => (
            <div key={i} className="bg-white/5 border border-white/10 rounded p-2 flex flex-col gap-2 group hover:bg-white/10 transition-colors">
              <div className="flex items-start gap-2">
                {file.is_folder ? <Folder size={14} className="text-yellow-400 mt-0.5" /> : <FileText size={14} className="text-blue-400 mt-0.5" />}
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold truncate" title={file.filename}>{file.filename}</p>
                  <p className="text-[9px] text-white/40 truncate" title={file.path}>{file.path}</p>
                </div>
              </div>
              <div className="flex items-center justify-between mt-1 pt-2 border-t border-white/5">
                <span className="text-[8px] text-white/30">
                  {file.size_bytes > 0 ? (file.size_bytes / 1024).toFixed(0) + ' KB' : ''}
                </span>
                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button 
                    onClick={async () => {
                       await fetch('http://127.0.0.1:8000/api/command', {
                         method: 'POST',
                         headers: {'Content-Type':'application/json'},
                         body: JSON.stringify({command: `Open file ${file.path}`})
                       });
                       // track open
                       fetch('http://127.0.0.1:8000/api/track-open', {
                         method: 'POST',
                         headers: {'Content-Type':'application/json'},
                         body: JSON.stringify({path: file.path})
                       });
                    }}
                    className="text-[9px] hover:text-[#39ff14]"
                  >
                    Open
                  </button>
                  <button 
                    onClick={async () => {
                       await fetch('http://127.0.0.1:8000/api/command', {
                         method: 'POST',
                         headers: {'Content-Type':'application/json'},
                         body: JSON.stringify({command: `Open folder ${file.path}`})
                       });
                    }}
                    className="text-[9px] hover:text-[#39ff14]"
                  >
                    Folder
                  </button>
                  <button 
                    onClick={() => navigator.clipboard.writeText(file.path)}
                    className="text-[9px] hover:text-[#39ff14]"
                  >
                    Copy
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass-panel p-4 shrink-0 mt-2">
        <h2 className="text-xs text-white/50 tracking-wider font-semibold uppercase mb-4 px-2">Quick Access</h2>
        <div className="grid grid-cols-4 gap-2">
          {/* Row 1 */}
          <button onClick={() => handleQuickAccess("Open Chrome")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Monitor size={16} className="text-red-400 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">Chrome</span>
          </button>
          <button onClick={() => handleQuickAccess("Open Edge")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Monitor size={16} className="text-blue-400 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">Edge</span>
          </button>
          <button onClick={() => handleQuickAccess("Open VS Code")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Code size={16} className="text-blue-500 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">VS Code</span>
          </button>
          <button onClick={() => handleQuickAccess("Open File Explorer")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Folder size={16} className="text-yellow-400 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">Files</span>
          </button>

          {/* Row 2 */}
          <button onClick={() => handleQuickAccess("Open Word")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <FileText size={16} className="text-blue-600 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">Word</span>
          </button>
          <button onClick={() => handleQuickAccess("Open Excel")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Activity size={16} className="text-green-500 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">Excel</span>
          </button>
          <button onClick={() => handleQuickAccess("Open PowerPoint")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Play size={16} className="text-orange-500 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">P-Point</span>
          </button>
          <button onClick={() => handleQuickAccess("Open Calculator")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Activity size={16} className="text-gray-300 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">Calc</span>
          </button>

          {/* Row 3 */}
          <button onClick={() => handleQuickAccess("Open YouTube")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Play size={16} className="text-red-500 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">YouTube</span>
          </button>
          <button onClick={() => handleQuickAccess("Open GitHub")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Code size={16} className="text-white group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">GitHub</span>
          </button>
          <button onClick={() => handleQuickAccess("Open Settings")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Settings size={16} className="text-gray-400 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">Settings</span>
          </button>
          <button onClick={() => handleQuickAccess("Open Microsoft Store")} className="glass-button aspect-square flex flex-col items-center justify-center gap-1 group">
            <Monitor size={16} className="text-cyan-400 group-hover:scale-110 transition-transform" />
            <span className="text-[8px] text-white/60">Store</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default RightPanel;
