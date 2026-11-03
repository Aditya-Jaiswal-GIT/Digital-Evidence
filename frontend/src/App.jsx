import { useEffect, useState } from "react";
import api from "./services/api";

function App() {
    const [backendStatus, setBackendStatus] = useState("Checking...");

    useEffect(() => {
        const checkBackend = async () => {
            try {
                const response = await api.get("/health");
                setBackendStatus(response.data.status);
            } catch (error) {
                console.error(error);
                setBackendStatus("Disconnected");
            }
        };

        checkBackend();
    }, []);

    return (
        <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center p-6">

            <div className="max-w-xl w-full bg-slate-900 border border-slate-700 rounded-2xl p-8">

                <h1 className="text-3xl font-bold text-blue-400 mb-4">
                    Digital Evidence Analyzer
                </h1>

                <p className="text-slate-300 mb-6">
                    AI-Based Digital Evidence Authenticity Analyzer
                </p>

                <div className="bg-slate-800 rounded-lg p-4">
                    <h2 className="text-lg font-semibold mb-2">
                        Backend Connection
                    </h2>

                    <p className="text-green-400">
                        {backendStatus}
                    </p>
                </div>

            </div>
        </div>
    );
}

export default App;