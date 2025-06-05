import { useState } from 'react';
import MessageBubble from './MessageBubble';
import axios from 'axios';
import { FiPlus } from 'react-icons/fi';

function ChatWindow({ userId, messages, setMessages, activeTool, setActiveTool, uploadedDocs, setUploadedDocs }) {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() && activeTool !== "visualize") return;

    const newMessages = [...messages];
    const userMessage = input.trim() || "[Using Visualize Tool]";
    newMessages.push({ role: "user", message: userMessage });
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    try {
      let reply, result;

      if (!activeTool) {
        const res = await axios.post("http://localhost:8000/chat/message", {
          user_id: userId,
          message: userMessage,
        });
        reply = res.data.reply;
      } else {
        let toolInput = input;

        if (activeTool === "visualize" && !input.trim()) {
          const lastAssistant = [...messages].reverse().find(m => m.role === "assistant");
          if (lastAssistant) {
            toolInput = lastAssistant.message;
          }
        }

        const res = await axios.post("http://localhost:8000/tools/use", {
          tool_name: activeTool,
          input_text: toolInput,
          user_id: userId,
        });

        if (activeTool === "visualize" && Array.isArray(res.data.result)) {
          reply = "[VISUALIZE]";
          result = res.data.result;
        } else if (activeTool === "search" && Array.isArray(res.data.result)) {
          reply = res.data.result
            .map(
              (item) =>
                `🔗 ${item.title}\n${item.href}\n${item.body?.slice(0, 150)}...`
            )
            .join("\n\n");
        } else {
          reply = typeof res.data.result === "string"
            ? res.data.result
            : JSON.stringify(res.data.result, null, 2);
        }
      }

      setMessages([...newMessages, { role: "assistant", message: reply, data: result }]);
    } catch (err) {
      setMessages([
        ...newMessages,
        { role: "assistant", message: " Error connecting to backend." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);

    setUploading(true);

    try {
      const res = await axios.post("http://localhost:8000/tools/upload", formData);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          message: `📄 Uploaded **${res.data.filename}**\n\n📝 Summary:\n${res.data.summary}`
        }
      ]);
      setUploadedDocs((prev) => [...prev, file.name]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", message: " Failed to upload and summarize PDF." }
      ]);
    } finally {
      setUploading(false);
    }
  };

  const handleExport = async () => {
    const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant');
    if (!lastAssistant) return;

    const res = await axios.post("http://localhost:8000/tools/export", {
      tool_name: "export_pdf",
      input_text: lastAssistant.message
    });

    let filePath = res.data.result.file_path.replace(/\\/g, "/");
    const fileName = filePath.split("/").pop();

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        message: `📄 Export ready: [Download ${fileName}](http://localhost:8000/${filePath})`
      }
    ]);
  };


  return (
    <div className="flex flex-col h-full max-h-[90vh]">
      <div className="flex-1 overflow-y-auto p-4 space-y-3 scroll-smooth">
        {uploading && (
          <div className="text-sm text-blue-400 animate-pulse px-2">
            ⏳ Uploading and analyzing document...
          </div>
        )}
        {messages.map((msg, i) => (
          <MessageBubble key={i} role={msg.role} message={msg.message} data={msg.data} />
        ))}
      </div>

      <div className="shrink-0 border-t border-white/10 bg-white/5 px-4 py-3 backdrop-blur-lg">
        <div className="flex flex-col md:flex-row gap-2 items-center">

          {/* Upload PDF */}
          <label className="cursor-pointer">
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleUpload}
            />
            <FiPlus className="text-white text-xl hover:text-blue-500 transition mr-2" />
          </label>

          {/* Tool Dropdown */}
          <select
            className="bg-gray-800 text-white border border-white/20 px-3 py-2 rounded-lg"
            value={activeTool}
            onChange={(e) => setActiveTool(e.target.value)}
          >
            <option value="">Tools</option>
            <option value="summarize">Summarize</option>
            <option value="clarify">Clarify</option>
            <option value="search">Web Search</option>
            <option value="visualize">Visualize</option>
            <option value="react_agent">ReAct Agent</option>
            <option value="qa">Chain-of-Thought QA</option>
          </select>

          {/* Input Field */}
          <input
            className="flex-1 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white placeholder-white/60 focus:outline-none focus:ring focus:ring-blue-500"
            placeholder={activeTool ? `Use ${activeTool} on...` : 'Chat with SynthesisTalk...'}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          />

          {/* Export Button */}
          <button
            onClick={handleExport}
            className="bg-zinc-900 border border-zinc-700 text-white px-4 py-2 rounded-md hover:bg-zinc-800 hover:border-white transition duration-200 shadow-sm"
          >
            🧾 Export to PDF
          </button>

          

          {/* Send Button */}
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
