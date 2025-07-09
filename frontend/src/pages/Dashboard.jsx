import { useEffect, useState } from 'react';
import API from '../api';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [docs, setDocs] = useState([]);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [search, setSearch] = useState('');
  const [editId, setEditId] = useState(null);
  const [isPublic, setIsPublic] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  const token = localStorage.getItem('token');
  const navigate = useNavigate();

  const fetchDocs = async () => {
    try {
      const res = await API.get('/documents', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocs(res.data);
    } catch (err) {
      console.error('Fetch error:', err.response?.data || err.message);
    }
  };

  const handleCreateOrUpdate = async (e) => {
    e.preventDefault();
    if (!title.trim() || !content.trim()) {
      alert('Title and content are required');
      return;
    }

    try {
      const payload = {
        title,
        content,
        is_public: isPublic
      };

      if (editId) {
        await API.put(`/document/${editId}`, payload, {
          headers: { Authorization: `Bearer ${token}` }
        });
        alert('Document updated');
        setEditId(null);
      } else {
        await API.post('/document', payload, {
          headers: { Authorization: `Bearer ${token}` }
        });
        alert('Document created');
      }

      setTitle('');
      setContent('');
      setIsPublic(false);
      fetchDocs();
    } catch (err) {
      alert('Failed to create/update document.');
      console.error(err.response?.data || err.message);
    }
  };

  const handleEdit = (doc) => {
    setEditId(doc.id);
    setTitle(doc.title);
    setContent(doc.content);
    setIsPublic(doc.is_public);
  };

  const handleDelete = async (id) => {
    const confirmed = window.confirm('Delete this document?');
    if (!confirmed) return;

    try {
      await API.delete(`/document/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      fetchDocs();
    } catch (err) {
      alert('Failed to delete.');
      console.error(err);
    }
  };

  const handleSearch = async () => {
    try {
      const res = await API.get(`/search?q=${search}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDocs(res.data);
    } catch (err) {
      console.error('Search error:', err.response?.data || err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  return (
    <div className={`${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-100 text-black'} min-h-screen p-6`}>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="flex gap-3">
          <button
            className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded"
            onClick={() => setDarkMode(!darkMode)}
          >
            {darkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
          <button
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      </div>

      <form onSubmit={handleCreateOrUpdate} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md max-w-2xl mx-auto space-y-4">
        <input
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded h-24 bg-white dark:bg-gray-900"
          placeholder="Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="isPublic"
            checked={isPublic}
            onChange={(e) => setIsPublic(e.target.checked)}
            className="accent-blue-500"
          />
          <label htmlFor="isPublic" className="text-sm">Make this document public</label>
        </div>
        <button
          type="submit"
          className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded"
        >
          {editId ? 'Update Document' : 'Create Document'}
        </button>
      </form>

      <div className="max-w-2xl mx-auto mt-6 flex gap-2">
        <input
          className="flex-1 p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-900"
          placeholder="Search documents..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button
          onClick={handleSearch}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        >
          Search
        </button>
      </div>

      <div className="max-w-2xl mx-auto mt-8 space-y-4">
        {docs.length === 0 ? (
          <p className="text-center text-gray-500 dark:text-gray-400 italic">No documents found.</p>
        ) : (
          docs.map((doc) => (
            <div key={doc.id} className="bg-white dark:bg-gray-800 border p-4 rounded shadow space-y-2">
              <h3 className="text-xl font-semibold text-indigo-700 dark:text-indigo-300">{doc.title}</h3>
              <p>{doc.content}</p>
              <p className="text-sm text-gray-500 dark:text-gray-400 italic">By: {doc.author}</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Created: {new Date(doc.created_at).toLocaleString()}</p>
              <p className="text-xs text-gray-400 dark:text-gray-500">Updated: {new Date(doc.updated_at).toLocaleString()}</p>
              <p className="text-xs font-medium text-blue-600 dark:text-blue-300">
                Visibility: {doc.is_public ? 'Public' : 'Private'}
              </p>
              <div className="flex gap-2 mt-2">
                <button
                  onClick={() => handleEdit(doc)}
                  className="bg-yellow-400 hover:bg-yellow-500 text-white px-3 py-1 rounded"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
