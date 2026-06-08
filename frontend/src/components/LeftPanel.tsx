import { useEffect } from 'react';
import { Plus, Trash2, Clock, Play, Code, Search, Folder, Calculator, Camera, MessageSquare, Filter, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useStore } from '../store';

const LeftPanel = () => {
  const { history, fetchHistory, clearHistory } = useStore();

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  const handleNewCommand = () => {
    window.dispatchEvent(new Event('focus-input'));
  };

  const handleClearHistory = () => {
    clearHistory();
  };

  const getCommandIcon = (cmd: string) => {
    const lowerCmd = cmd.toLowerCase();
    if (lowerCmd.includes('youtube')) return <Play className="w-5 h-5 text-red-500" />;
    if (lowerCmd.includes('vs code')) return <Code className="w-5 h-5 text-blue-500" />;
    if (lowerCmd.includes('folder') || lowerCmd.includes('file')) return <Folder className="w-5 h-5 text-yellow-400" />;
    if (lowerCmd.includes('google') || lowerCmd.includes('search')) return <Search className="w-5 h-5 text-blue-400" />;
    if (lowerCmd.includes('screenshot') || lowerCmd.includes('camera')) return <Camera className="w-5 h-5 text-gray-300" />;
    if (lowerCmd.includes('calculat')) return <Calculator className="w-5 h-5 text-gray-400" />;
    if (lowerCmd.includes('explain') || lowerCmd.includes('tell')) return <MessageSquare className="w-5 h-5 text-green-400" />;
    return <Clock className="w-5 h-5 text-gray-400" />;
  };

  return (
    <motion.div 
      initial={{ x: -50, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className="w-72 h-full bg-[#0a0a0a]/90 backdrop-blur-xl border border-white/10 rounded-2xl p-4 flex flex-col shrink-0"
    >
      <button 
        onClick={handleNewCommand}
        className="w-full flex items-center justify-center gap-2 bg-transparent hover:bg-white/5 border border-white/20 rounded-xl py-3 mb-6 transition-all mt-2"
      >
        <Plus className="w-4 h-4 text-white/70" />
        <span className="text-sm font-medium text-white/90">New Command</span>
      </button>

      <div className="flex items-center justify-between mb-4 px-2">
        <h2 className="text-[10px] font-bold text-white/90 uppercase tracking-wider">COMMAND HISTORY</h2>
        <Filter className="w-4 h-4 text-white/50 cursor-pointer hover:text-white transition-colors" />
      </div>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        <div className="space-y-2">
          {history.map((item) => (
            <div key={item.id} className="p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors cursor-pointer group flex items-center gap-3 border border-transparent hover:border-white/10">
              <div className="shrink-0">
                {getCommandIcon(item.command)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-semibold text-white/90 truncate pr-2">{item.command}</span>
                  <span className="text-[9px] text-white/40 shrink-0">10:45 AM</span>
                </div>
                <div className="flex justify-between items-center mt-0.5">
                  <span className="text-[10px] text-white/50 truncate pr-2">
                    {item.status === 'Completed' ? 'Opened successfully' : item.status}
                  </span>
                  <CheckCircle className="w-3 h-3 text-[#39ff14] shrink-0" />
                </div>
              </div>
            </div>
          ))}
          {history.length === 0 && (
            <div className="text-xs text-white/40 px-2 italic text-center py-4">No recent history</div>
          )}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-white/10 shrink-0">
        <button 
          onClick={handleClearHistory}
          className="w-full flex items-center justify-center gap-2 px-3 py-3 text-sm font-medium text-white/60 hover:text-white hover:bg-white/5 rounded-xl transition-colors"
        >
          <Trash2 className="w-4 h-4" />
          Clear History
        </button>
      </div>
    </motion.div>
  );
};

export default LeftPanel;
