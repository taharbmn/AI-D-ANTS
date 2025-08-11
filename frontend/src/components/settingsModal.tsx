import React, { useState } from "react";


const initialEnv = {
  DATABRICKS_TOKEN: '',
  DATABRICKS_BASE_URL: '',
  DATABRICKS_DEFAULT_MODEL: 'databricks-meta-llama-3-3-70b-instruct',
  AWS_REGION: 'us-east-1',
  AWS_ACCESS_KEY_ID: '',
  AWS_SECRET_ACCESS_KEY: '',
  API_TIMEOUT: '30',
  MAX_RETRIES: '3',
};

const SettingsModal = ({
  onClose,
}: {
  onClose: () => void;
}) => {
  const [env, setEnv] = useState(initialEnv);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEnv({ ...env, [e.target.name]: e.target.value });
    setSaved(false);
    setError('');
  };

  const handleSave = () => {
    if (!env.DATABRICKS_TOKEN || !env.DATABRICKS_BASE_URL || !env.AWS_ACCESS_KEY_ID || !env.AWS_SECRET_ACCESS_KEY) {
      setError('Please fill in all required fields.');
      return;
    }
    setSaved(true);
    setError('');
  };

  return (
    <div className="h-screen w-screen absolute inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-neutral-800 rounded-3xl p-10 w-full max-w-lg shadow-2xl border border-neutral-700">
        <h2 className="text-2xl font-bold mb-6 text-white text-center tracking-wide">Settings</h2>
        <div className="space-y-4">
          <Input label="Databricks Token" name="DATABRICKS_TOKEN" value={env.DATABRICKS_TOKEN} onChange={handleChange} required />
          <Input label="Databricks Base URL" name="DATABRICKS_BASE_URL" value={env.DATABRICKS_BASE_URL} onChange={handleChange} required />
          <Input label="Databricks Default Model" name="DATABRICKS_DEFAULT_MODEL" value={env.DATABRICKS_DEFAULT_MODEL} onChange={handleChange} />
          <Input label="AWS Region" name="AWS_REGION" value={env.AWS_REGION} onChange={handleChange} />
          <Input label="AWS Access Key ID" name="AWS_ACCESS_KEY_ID" value={env.AWS_ACCESS_KEY_ID} onChange={handleChange} required />
          <Input label="AWS Secret Access Key" name="AWS_SECRET_ACCESS_KEY" value={env.AWS_SECRET_ACCESS_KEY} onChange={handleChange} required type="password" />
          <Input label="API Timeout" name="API_TIMEOUT" value={env.API_TIMEOUT} onChange={handleChange} type="number" />
          <Input label="Max Retries" name="MAX_RETRIES" value={env.MAX_RETRIES} onChange={handleChange} type="number" />
        </div>
        {error && <div className="text-red-400 mt-3 text-sm text-center">{error}</div>}
        {saved && <div className="text-green-400 mt-3 text-sm text-center">Settings saved!</div>}
        <div className="flex justify-between mt-8">
          <button onClick={onClose} className="text-base cursor-pointer text-blue-400 hover:underline">Close</button>
          <button onClick={handleSave} className="bg-blue-500 cursor-pointer hover:bg-blue-600 text-white rounded-2xl px-7 py-2 font-semibold transition-colors shadow">Save</button>
        </div>
      </div>
    </div>
  );
};

function Input({ label, name, value, onChange, required, type = "text" }: {
  label: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  required?: boolean;
  type?: string;
}) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-base text-gray-200 font-medium">
        {label}{required && <span className="text-red-400">*</span>}
      </label>
      <input
        className="rounded-2xl border border-gray-500 bg-neutral-900 text-white px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-400 transition-all"
        name={name}
        value={value}
        onChange={onChange}
        required={required}
        type={type}
        autoComplete="off"
      />
    </div>
  );
}

export default SettingsModal;
