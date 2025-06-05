// src/components/DocumentUploader.jsx
import { useState } from 'react';
import axios from 'axios';

function DocumentUploader({ onResult }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setError(null);

    try {
      const res = await axios.post('http://localhost:8000/tools/upload', formData);
      onResult(res.data);
    } catch (err) {
      setError('Upload failed.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-white/10 p-4 rounded-lg border border-white/20 mb-4">
      <label className="block text-white mb-2 font-medium">📄 Upload Document</label>
      <input
        type="file"
        accept=".pdf"
        className="mb-2 text-white"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button
        onClick={handleUpload}
        className="bg-blue-500 hover:bg-blue-600 px-4 py-2 rounded-lg text-white font-semibold"
        disabled={uploading}
      >
        {uploading ? 'Uploading...' : 'Upload & Analyze'}
      </button>
      {error && <p className="text-red-400 mt-2">{error}</p>}
    </div>
  );
}

export default DocumentUploader;
