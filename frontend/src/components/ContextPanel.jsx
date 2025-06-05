import { useEffect, useState } from 'react';
import axios from 'axios';

function ContextPanel({ messages, activeTool, uploadedDocs }) {
  const [topic, setTopic] = useState('New Conversation');
  const [sources, setSources] = useState([]);
  const [isGeneratingTopic, setIsGeneratingTopic] = useState(false);

  // Generate intelligent topic title
  const generateTopicTitle = async (conversationHistory) => {
    if (conversationHistory.length < 2) return 'New Conversation';
    
    setIsGeneratingTopic(true);
    
    try {
      // Take first few exchanges to understand the topic
      const relevantMessages = conversationHistory.slice(0, 6);
      const conversationText = relevantMessages
        .map(msg => `${msg.role}: ${msg.message}`)
        .join('\n');

      const response = await axios.post('http://localhost:8000/tools/generate_topic', {
        conversation_text: conversationText
      });

      let generatedTitle = response.data.topic;
      
      // Clean up the response - remove quotes, extra text, etc.
      generatedTitle = generatedTitle
        .replace(/^["']|["']$/g, '') // Remove quotes
        .replace(/^Title:\s*/i, '') // Remove "Title:" prefix
        .replace(/^\d+\.\s*/, '') // Remove numbered list format
        .trim();

      // Fallback if generation fails or is too long
      if (!generatedTitle || generatedTitle.length > 50) {
        generatedTitle = extractSimpleTopic(conversationHistory);
      }

      setTopic(generatedTitle);
    } catch (error) {
      console.error('Topic generation failed:', error);
      setTopic(extractSimpleTopic(conversationHistory));
    } finally {
      setIsGeneratingTopic(false);
    }
  };

  // Fallback method to extract topic from keywords
  const extractSimpleTopic = (conversationHistory) => {
    const firstUserMessage = conversationHistory.find(m => m.role === 'user')?.message || '';
    
    // Extract key terms from first substantial message
    const words = firstUserMessage.toLowerCase().split(' ');
    const stopWords = ['what', 'how', 'why', 'when', 'where', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'can', 'could', 'would', 'should', 'tell', 'me', 'you', 'i', 'we', 'they'];
    
    const keyWords = words
      .filter(word => word.length > 3 && !stopWords.includes(word))
      .slice(0, 3);
    
    if (keyWords.length > 0) {
      return keyWords.map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }
    
    return 'Research Discussion';
  };

  useEffect(() => {
    if (messages.length >= 2 && messages.length % 4 === 0) {
      // Generate topic every 4 messages (2 exchanges)
      generateTopicTitle(messages);
    } else if (messages.length === 2) {
      // Generate initial topic after first exchange
      generateTopicTitle(messages);
    }

    // Extract sources from assistant messages
    const searchResults = messages
      .filter(m => m.role === 'assistant' && m.message.includes("http"))
      .flatMap(m =>
        [...m.message.matchAll(/https?:\/\/[^\s)]+/g)].map(match => match[0])
      );

    setSources([...new Set(searchResults)].slice(0, 5)); // Remove duplicates and limit to 5
  }, [messages]);

  return (
    <div className="text-white text-sm space-y-3">
      <div>
        <p className="text-white/60 mb-1">Current Topic:</p>
        <div className="bg-white/10 p-2 rounded-md relative">
          {isGeneratingTopic && (
            <div className="absolute right-2 top-2">
              <div className="animate-spin h-3 w-3 border border-white/30 border-t-white rounded-full"></div>
            </div>
          )}
          <span className={isGeneratingTopic ? 'opacity-50' : ''}>
            {topic}
          </span>
        </div>
      </div>

      <div>
        <p className="text-white/60 mb-1">Last Used Tool:</p>
        <div className="bg-white/10 p-2 rounded-md">
          {activeTool || '---'}
        </div>
      </div>

      <div>
        <p className="text-white/60 mb-1">Message Count:</p>
        <div className="bg-white/10 p-2 rounded-md">
          {messages.length} messages
        </div>
      </div>

      <div>
        <p className="text-white/60 mb-1">Uploaded Documents:</p>
        {uploadedDocs.length > 0 ? (
          <div className="space-y-1">
            {uploadedDocs.map((doc, i) => (
              <div key={i} className="bg-white/10 p-2 rounded-md text-xs">
                📄 {doc}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white/10 p-2 rounded-md">None</div>
        )}
      </div>

      <div>
        <p className="text-white/60 mb-1">Sources Found:</p>
        {sources.length > 0 ? (
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {sources.map((url, i) => (
              <a
                key={i}
                href={url}
                target="_blank"
                rel="noreferrer"
                className="block text-blue-400 hover:text-blue-300 underline text-xs truncate p-1 bg-white/5 rounded"
                title={url}
              >
                {url.replace(/https?:\/\/(www\.)?/, '').split('/')[0]}
              </a>
            ))}
          </div>
        ) : (
          <div className="bg-white/10 p-2 rounded-md">No sources found</div>
        )}
      </div>
    </div>
  );
}

export default ContextPanel;