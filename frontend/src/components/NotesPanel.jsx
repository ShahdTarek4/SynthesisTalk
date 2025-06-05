import { useEffect, useState } from 'react';
import axios from 'axios';

function NotesPanel({ userId }) {
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState('');
  const [saving, setSaving] = useState(false);

  const loadNotes = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/tools/note/list?user_id=${userId}`);
      setNotes(res.data.notes || []);
    } catch (err) {
      console.error("Failed to load notes.");
    }
  };

  const saveNote = async () => {
    if (!newNote.trim()) return;
    setSaving(true);
    try {
      const formData = new FormData();
      formData.append("user_id", userId);
      formData.append("note", newNote);

      await axios.post("http://localhost:8000/tools/note/save", formData);
      setNewNote('');
      loadNotes();
    } catch (err) {
      console.error("Failed to save note.");
    } finally {
      setSaving(false);
    }
  };

  const deleteNote = async (index) => {
    const formData = new FormData();
    formData.append("user_id", userId);
    formData.append("index", index);
    await axios.post("http://localhost:8000/tools/note/delete", formData);
    loadNotes();
  };

  const clearNotes = async () => {
    const formData = new FormData();
    formData.append("user_id", userId);
    await axios.post("http://localhost:8000/tools/note/clear", formData);
    loadNotes();
  };

  useEffect(() => {
    loadNotes();
  }, []);

  return (
    <div className="text-white text-sm space-y-3">
      <div className="space-y-2">
        {notes.map((note, i) => (
          <div key={i} className="bg-white/10 p-2 rounded-md flex justify-between items-center">
            <span>{note}</span>
            <button
              className="text-red-400 text-xs ml-2 hover:text-red-500"
              onClick={() => deleteNote(i)}
            >✖</button>
          </div>
        ))}
      </div>

      <textarea
        value={newNote}
        onChange={(e) => setNewNote(e.target.value)}
        placeholder="Write a new note..."
        className="w-full bg-white/10 border border-white/20 rounded-md p-2 text-sm placeholder-white/50 resize-none"
        rows={3}
      />

      <button
        onClick={saveNote}
        disabled={saving}
        className="mt-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded-md text-sm w-full"
      >
        {saving ? 'Saving...' : 'Save Note'}
      </button>

      <button
        onClick={clearNotes}
        className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded-md text-sm w-full"
      >
        Clear All Notes
      </button>
    </div>
  );
}

export default NotesPanel;
