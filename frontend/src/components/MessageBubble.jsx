import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

// Color palette for better visual appeal
const COLORS = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22'];

// Custom tooltip for better data display
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-800 p-3 rounded-lg border border-white/20 shadow-lg">
        <p className="text-white font-medium">{label}</p>
        <p className="text-blue-400">
          Count: <span className="font-bold">{payload[0].value}</span>
        </p>
      </div>
    );
  }
  return null;
};

// Custom label for pie chart
const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, label }) => {
  if (percent < 0.05) return null; // Hide labels for very small slices
  
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text 
      x={x} 
      y={y} 
      fill="white" 
      textAnchor={x > cx ? 'start' : 'end'} 
      dominantBaseline="central"
      fontSize="12"
      fontWeight="bold"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

function MessageBubble({ role, message, data }) {
  const isUser = role === 'user';
  
  // Check if message contains a Markdown-style link: [text](url)
  const isMarkdownLink = /\[.*?\]\(.*?\)/.test(message);
  const linkText = message.match(/\[([^\]]+)\]/)?.[1]; // Extracts the [text]
  const linkHref = message.match(/\((.*?)\)/)?.[1];     // Extracts the (url)

  // Enhanced visualization rendering
  const renderVisualization = (chartData) => {
    if (!chartData || !Array.isArray(chartData) || chartData.length === 0) {
      return (
        <div className="w-full p-4 bg-gray-800/30 rounded-lg border border-white/10">
          <h3 className="text-lg font-bold mb-2 text-white">📊 Research Insights</h3>
          <p className="text-gray-400">No data available for visualization</p>
        </div>
      );
    }

    // Sort data by count for better visual hierarchy
    const sortedData = [...chartData].sort((a, b) => (b.count || 0) - (a.count || 0));
    
    // Process labels to prevent overflow
    const processedData = sortedData.map(item => ({
      ...item,
      label: item.label && item.label.length > 12 
        ? item.label.substring(0, 12) + '...' 
        : item.label,
      originalLabel: item.label
    }));

    // Determine chart type based on data size and characteristics
    const shouldUsePieChart = chartData.length <= 5 && chartData.every(item => item.count > 0);
    const maxCount = Math.max(...chartData.map(item => item.count || 0));

    return (
      <div className="w-full max-w-3xl">
        <h3 className="text-lg font-bold mb-4 text-white flex items-center gap-2">
          📊 Research Insights
          <span className="text-sm font-normal text-gray-400">
            ({chartData.length} topics)
          </span>
        </h3>
        
        <div className="bg-gray-800/30 rounded-lg border border-white/10 p-4">
          {shouldUsePieChart ? (
            // Pie Chart Layout for smaller datasets
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={processedData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={renderCustomLabel}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {processedData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-white mb-2">Details</h4>
                {processedData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-700/30 rounded">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      ></div>
                      <span className="text-white text-xs" title={item.originalLabel}>
                        {item.originalLabel}
                      </span>
                    </div>
                    <span className="text-blue-400 font-bold text-sm">{item.count}</span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            // Bar Chart for larger datasets
            <div>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart
                  data={processedData}
                  margin={{ top: 20, right: 5, left: 5, bottom: 90 }}
                >
                  <XAxis 
                    dataKey="label" 
                    angle={-45}
                    textAnchor="end"
                    height={90}
                    interval={0}
                    tick={{ fontSize: 11, fill: '#cbd5e1', wordBreak: 'break-word' }}
                  />
                  <YAxis 
                    tick={{ fontSize: 12, fill: '#cbd5e1' }}
                    domain={[0, Math.ceil(maxCount * 1.1)]}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar 
                    dataKey="count" 
                    radius={[3, 3, 0, 0]}
                  >
                    {processedData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              
              {/* Quick stats */}
              <div className="mt-3 flex justify-center space-x-4 text-xs">
                <div className="text-center">
                  <div className="text-blue-400 font-bold">{chartData.length}</div>
                  <div className="text-gray-400">Topics</div>
                </div>
                <div className="text-center">
                  <div className="text-green-400 font-bold">{Math.max(...chartData.map(i => i.count))}</div>
                  <div className="text-gray-400">Max</div>
                </div>
                <div className="text-center">
                  <div className="text-yellow-400 font-bold">
                    {Math.round(chartData.reduce((sum, i) => sum + i.count, 0) / chartData.length)}
                  </div>
                  <div className="text-gray-400">Avg</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`p-3 rounded-lg text-sm whitespace-pre-wrap max-w-[95%] border ${
          isUser
            ? 'bg-blue-600 text-white self-end border-blue-800'   // User message style
            : 'bg-gray-700 text-white self-start border-white/10' // Assistant message style
        }`}
      >
        {/* Special case: Visualize data */}
        {message === '[VISUALIZE]' && data ? (
          renderVisualization(data)
        ) : isMarkdownLink ? (
          // Render clickable link if message is markdown-formatted
          <a
            href={linkHref}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 underline hover:text-blue-300"
          >
            {linkText}
          </a>
        ) : (
          // Default: Render message as plain text
          message
        )}
      </div>
    </div>
  );
}

export default MessageBubble;