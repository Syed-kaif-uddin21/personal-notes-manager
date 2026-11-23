import { useState, useEffect } from "react";
import Login from "./components/login.jsx";
import NoteCard from "./components/NoteCard.jsx";
import "./App.css";

const API_URL = "http://127.0.0.1:8001";

function App() {
  const [token, setToken] = useState("");
  const [notes, setNotes] = useState([]);

  const handleLogin = (newToken) => {
    setToken(newToken);
  };

  const handleLogout = () => {
    setToken("");
    setNotes([]);
  };

  function loadNotes() {
    if (!token) return;
    fetch(`${API_URL}/notes`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setNotes(data);
        } else {
          setNotes([]);
        }
      });
  }

  useEffect(() => {
    loadNotes();
  }, [token]);

  if (!token) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <>
      <div className="app-header">
        <h1>Personal Notes</h1>
        <button onClick={handleLogout}>Logout</button>
      </div>

      {notes.length === 0 ? (
        <p>No notes found</p>
      ) : (
        <ul className="equipment-list">
          {notes.map((item) => (
            <NoteCard key={item.id} item={item} apiUrl={API_URL} />
          ))}
        </ul>
      )}
    </>
  );
}

export default App;
