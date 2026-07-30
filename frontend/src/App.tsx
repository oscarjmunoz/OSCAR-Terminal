import { useEffect, useState } from "react";

import { getStatus, getTick } from "./api/market";

export default function App() {

    const [status, setStatus] = useState<any>(null);
    const [tick, setTick] = useState<any>(null);

    useEffect(() => {

        load();

        const timer = setInterval(load, 1000);

        return () => clearInterval(timer);

    }, []);

    async function load() {

        try {

            const s = await getStatus();
            const t = await getTick();

            setStatus(s);
            setTick(t);

        } catch (e) {

            console.error(e);

        }

    }

    return (

        <div
            style={{
                background: "#0f172a",
                color: "white",
                minHeight: "100vh",
                padding: 40,
                fontFamily: "Segoe UI",
            }}
        >

            <h1>OSCAR TERMINAL</h1>

            <hr />

            <h2>MT5</h2>

            <pre>

{JSON.stringify(status, null, 4)}

            </pre>

            <h2>Tick</h2>

            <pre>

{JSON.stringify(tick, null, 4)}

            </pre>

        </div>

    );

}