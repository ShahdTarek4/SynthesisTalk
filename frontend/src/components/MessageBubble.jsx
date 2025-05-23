import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const CustomTick = ({ x, y, payload }) => {
  return (
    <foreignObject x={x - 50} y={y + 5} width={100} height={100}>
      <div
        xmlns="http://www.w3.org/1999/xhtml"
        style={{
          fontSize: '11px',
          color: '#444',
          textAlign: 'center',
          lineHeight: '1.2',
          wordBreak: 'break-word',
        }}
      >
        {payload.value}
      </div>
    </foreignObject>
  );
};


function MessageBubble({ role, message, data }) {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`p-3 rounded-lg text-sm whitespace-pre-wrap max-w-[95%] ${
          isUser
            ? 'bg-blue-600 text-white self-end'
            : 'bg-white text-black self-start'
        }`}
      >
        {message === '[VISUALIZE]' && data ? (
          <div className="bg-white rounded-lg p-4 mt-2 w-full max-w-xl">
            <h3 className="text-lg font-bold mb-2">📊 Research Insights</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data}>
                <XAxis
               dataKey="label"
               height={100}
              interval={0}
              tick={<CustomTick />}
              />

                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          message
        )}
      </div>
    </div>
  );
}

export default MessageBubble;
