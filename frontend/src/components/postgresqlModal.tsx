import React, { useState } from "react";

const initialPostgreSQLConfig = {
  host: '',
  port: '5432',
  database: '',
  username: '',
  password: '',
  ssl: true,
};

const PostgreSQLModal = ({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) => {
  const [config, setConfig] = useState(initialPostgreSQLConfig);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setConfig({ 
      ...config, 
      [name]: type === 'checkbox' ? checked : value 
    });
    setSaved(false);
    setError('');
  };

  const handleSave = () => {
    if (!config.host || !config.database || !config.username || !config.password) {
      setError('Please fill in all required fields.');
      return;
    }
    setSaved(true);
    setError('');
  };

  const testConnection = () => {
    // Mock connection test
    if (!config.host || !config.database || !config.username || !config.password) {
      setError('Please fill in all required fields before testing connection.');
      return;
    }
    // Simulate connection test
    setTimeout(() => {
      setSaved(true);
      setError('');
    }, 1000);
  };

  return (
    <div className="h-screen w-screen absolute inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-neutral-800 rounded-3xl p-10 w-full max-w-lg shadow-2xl border border-neutral-700">
        <h2 className="text-2xl font-bold mb-6 text-white text-center tracking-wide">PostgreSQL Configuration</h2>
        <div className="space-y-4">
          <Input 
            label="Host" 
            name="host" 
            value={config.host} 
            onChange={handleChange} 
            required 
            placeholder="localhost or your database host"
          />
          <Input 
            label="Port" 
            name="port" 
            value={config.port} 
            onChange={handleChange} 
            type="number"
            placeholder="5432"
          />
          <Input 
            label="Database Name" 
            name="database" 
            value={config.database} 
            onChange={handleChange} 
            required 
            placeholder="your_database_name"
          />
          <Input 
            label="Username" 
            name="username" 
            value={config.username} 
            onChange={handleChange} 
            required 
            placeholder="your_username"
          />
          <Input 
            label="Password" 
            name="password" 
            value={config.password} 
            onChange={handleChange} 
            required 
            type="password"
            placeholder="your_password"
          />
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="ssl"
              name="ssl"
              checked={config.ssl}
              onChange={handleChange}
              className="rounded border border-gray-500 bg-neutral-900 text-blue-500 focus:ring-2 focus:ring-blue-400"
            />
            <label htmlFor="ssl" className="text-base text-gray-200 font-medium">
              Enable SSL
            </label>
          </div>
        </div>
        {error && <div className="text-red-400 mt-3 text-sm text-center">{error}</div>}
        {saved && <div className="text-green-400 mt-3 text-sm text-center">Configuration saved successfully!</div>}
        <div className="flex justify-between items-center mt-8">
          <button 
            onClick={onClose} 
            className="text-base cursor-pointer text-blue-400 hover:underline"
          >
            Close
          </button>
          <div className="flex gap-3">
            <button 
              onClick={testConnection} 
              className="bg-gray-600 cursor-pointer hover:bg-gray-700 text-white rounded-2xl px-5 py-2 font-semibold transition-colors shadow"
            >
              Test Connection
            </button>
            <button 
              onClick={handleSave} 
              className="bg-blue-500 cursor-pointer hover:bg-blue-600 text-white rounded-2xl px-7 py-2 font-semibold transition-colors shadow"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

function Input({ 
  label, 
  name, 
  value, 
  onChange, 
  required, 
  type = "text", 
  placeholder 
}: {
  label: string;
  name: string;
  value: string | number | boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  type?: string;
  placeholder?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-base text-gray-200 font-medium">
        {label}{required && <span className="text-red-400">*</span>}
      </label>
      <input
        className="rounded-2xl border border-gray-500 bg-neutral-900 text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all"
        name={name}
        value={value as string}
        onChange={onChange}
        required={required}
        type={type}
        placeholder={placeholder}
        autoComplete="off"
      />
    </div>
  );
}

export default PostgreSQLModal;
