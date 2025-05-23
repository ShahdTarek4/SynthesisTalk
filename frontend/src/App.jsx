import ChatWindow from './components/ChatWindow';

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-gray-900 to-gray-800 text-white font-sans">
      <header className="p-4 backdrop-blur-md bg-white/10 shadow-md border-b border-white/20">
        <h1 className="text-2xl font-bold tracking-wide">🧠 SynthesisTalk</h1>
        <p className="text-sm opacity-70">Your AI research assistant</p>
      </header>

      <main className="flex-1 flex flex-col items-center px-4 md:px-10 py-6 gap-6">
        <div className="w-full max-w-4xl h-[85vh] bg-white/5 rounded-xl shadow-lg border border-white/10 overflow-hidden">
          <ChatWindow />
        </div>

      </main>
    </div>
  );
}

export default App;
