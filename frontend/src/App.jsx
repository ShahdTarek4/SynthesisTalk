import ChatWindow from './components/ChatWindow';
import NotesPanel from './components/NotesPanel';
import ContextPanel from './components/ContextPanel';
import { useEffect, useState } from 'react';
import axios from 'axios';

function App() {
  const [messages, setMessages] = useState([]);
  const [activeTool, setActiveTool] = useState('');
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [showContext, setShowContext] = useState(true);
  const [showNotes, setShowNotes] = useState(false);
  const [userId, setUserId] = useState('');

  useEffect(() => {
    let uid = localStorage.getItem('synthesis_user_id');
    if (!uid) {
      uid = crypto.randomUUID();
      localStorage.setItem('synthesis_user_id', uid);
    }
    setUserId(uid);
  }, []);

const handleReset = async () => {
  try {
    setMessages([]);
    await axios.post("http://localhost:8000/tools/convo/reset", {
      user_id: userId
    });
  } catch (err) {
    console.error("Reset failed", err);
  }
};



  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-950 to-gray-800 text-white font-sans">
      <header className="p-4 bg-gray-950 border-b border-white/10 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-wide text-white">SynthesisTalk</h1>
          <p className="text-sm text-white/60">Your AI research assistant</p>
        </div>
        <button
          onClick={handleReset}
          className="group relative flex items-center gap-2 text-sm text-white/70 hover:text-white px-3 py-2 rounded-md border border-white/20 hover:border-white/40 transition"

        >
          <div title="Clear Chat" className="flex items-center gap-2">
            <span className="text-lg">↺</span>
            <span>Clear Chat</span>
          </div>
        </button>
      </header>

      <main className="flex-1 flex flex-col items-center px-4 md:px-10 py-6 gap-4">
        <div className="w-full max-w-7xl h-[85vh] flex gap-4 relative">
          {/* Chat Panel */}
          <div className="flex-1 bg-white/5 rounded-xl shadow-lg border border-white/10 overflow-hidden">
            <ChatWindow
              userId={userId}
              messages={messages}
              setMessages={setMessages}
              activeTool={activeTool}
              setActiveTool={setActiveTool}
              uploadedDocs={uploadedDocs}
              setUploadedDocs={setUploadedDocs}
            />
          </div>

          {/* Side Panel Tabs */}
          <div className="w-56 bg-gray-900 rounded-xl shadow-md border border-white/10 overflow-hidden">
            <div className="flex text-sm font-medium">
              <button
                className={`flex-1 px-3 py-2 transition ${showContext ? 'bg-gray-800' : 'bg-gray-700'}`}
                onClick={() => { setShowContext(true); setShowNotes(false); }}
              >
                Context
              </button>
              <button
                className={`flex-1 px-3 py-2 transition ${showNotes ? 'bg-gray-800' : 'bg-gray-700'}`}
                onClick={() => { setShowNotes(true); setShowContext(false); }}
              >
                Notes
              </button>
            </div>
            <div className="p-3">
              {showContext && <ContextPanel messages={messages} activeTool={activeTool} uploadedDocs={uploadedDocs} />}
              {showNotes && <NotesPanel userId={userId} />}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
