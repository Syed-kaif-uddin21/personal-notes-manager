import { useState } from "react";

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setMsg("");

    if (isRegister) {
      if (!username || !email || !password) {
        setError("All fields are required");
        return;
      }

      fetch("http://127.0.0.1:8001/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: username,
          email: email,
          password: password,
        }),
      })
        .then(async (res) => {
          const data = await res.json();
          if (!res.ok) {
            throw new Error(data.detail || "Registration failed");
          }
          return data;
        })
        .then(() => {
          setMsg("Registration successful! You can now log in.");
          setIsRegister(false);
          setPassword("");
        })
        .catch((err) => {
          setError(err.message);
        });

    } else {
      if (!email || !password) {
        setError("Email and password are required");
        return;
      }

      fetch("http://127.0.0.1:8001/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      })
        .then(async (res) => {
          const data = await res.json();
          if (!res.ok) {
            throw new Error(data.detail || "Login failed");
          }
          return data;
        })
        .then((data) => {
          const token = data.access_token || data.token?.access_token;
          onLogin(token);
        })
        .catch((err) => {
          setError(err.message);
        });
    }
  }

  return (
    <div className="add-form">
      <h2>{isRegister ? "Register" : "Login"}</h2>

      <form onSubmit={handleSubmit}>
        {isRegister && (
          <div>
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>
        )}

        <div>
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div>
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button type="submit" className="btn-primary">
          {isRegister ? "Sign Up" : "Log In"}
        </button>

        {error && <p className="error" style={{ color: "red" }}>{error}</p>}
        {msg && <p className="success" style={{ color: "green" }}>{msg}</p>}
      </form>

      <button
        type="button"
        onClick={() => {
          setIsRegister(!isRegister);
          setError("");
          setMsg("");
        }}
      >
        {isRegister
          ? "Already have an account? Login"
          : "Need an account? Register"}
      </button>
    </div>
  );
}

export default Login;