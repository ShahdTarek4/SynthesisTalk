import { useState } from 'react';
import MessageBubble from './MessageBubble';
import axios from 'axios';

function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [tool, setTool] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { role: 'user', message: input }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      let reply, result;

      if (!tool) {
        // Default chat mode
        const res = await axios.post('http://localhost:8000/chat/message', {
          user_id: 'user123',
          message: input,
        });
        reply = res.data.reply;
      } else {
        const res = await axios.post('http://localhost:8000/tools/use', {
          tool_name: tool,
          input_text: input,
          user_id: 'user123'
        });

        if (tool === 'visualize' && Array.isArray(res.data.result)) {
          reply = '[VISUALIZE]';
          result = res.data.result;
          setMessages([
            ...newMessages,
            { role: 'assistant', message: reply, data: result }
          ]);
        } else if (tool === 'search' && Array.isArray(res.data.result)) {
          reply = res.data.result.map((item) =>
            `🔗 ${item.title}\n${item.href}\n${item.body.slice(0, 150)}...`
          ).join('\n\n');
        } else {
          reply = typeof res.data.result === 'string'
            ? res.data.result
            : JSON.stringify(res.data.result, null, 2);
        }
      }

      setMessages([...newMessages, { role: 'assistant', message: reply, data: result }]);
    } catch (err) {
      setMessages([...newMessages, { role: 'assistant', message: ' Error connecting to backend.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-h-[90vh]">
      <div className="flex-1 overflow-y-auto p-4 space-y-3 scroll-smooth">
        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} message={msg.message} data={msg.data} />
        ))}
      </div>

      <div className="shrink-0 border-t border-white/10 bg-white/5 px-4 py-3 backdrop-blur-lg">
        <div className="flex flex-col md:flex-row gap-2">
          <select
            className="bg-gray-800 text-white border border-white/20 px-3 py-2 rounded-lg"
            value={tool}
            onChange={(e) => setTool(e.target.value)}
          >
            <option value="">-- Select Tool (optional) --</option>
            <option value="summarize">Summarize</option>
            <option value="clarify">Clarify</option>
            <option value="search">Web Search</option>
            <option value="visualize">Visualize</option>
            <option value="react_agent">ReAct Agent</option>
          </select>

          <input
            className="flex-1 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/60 focus:outline-none focus:ring focus:ring-blue-500"
            placeholder={tool ? `Use ${tool} on...` : 'Chat with SynthesisTalk...'}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          />
          <button
            onClick={sendMessage}
            className="bg-blue-600 hover:bg-blue-700 transition text-white px-4 py-2 rounded-lg font-semibold"
            disabled={loading}
          >
            {loading ? '...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;
