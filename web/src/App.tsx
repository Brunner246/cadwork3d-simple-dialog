import { useCallback, useState } from "react";
import { useCadwork, type BuildingElement } from "./cadwork";

export default function App() {
  const { bridge, error } = useCadwork();
  const [elements, setElements] = useState<BuildingElement[] | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLoad = useCallback(async () => {
    if (!bridge) return;
    setLoading(true);
    try {
      setElements(await bridge.getActiveElements());
    } finally {
      setLoading(false);
    }
  }, [bridge]);

  const handleClick = useCallback(
    (id: number) => {
      bridge?.activateAndZoom(id);
    },
    [bridge],
  );

  return (
    <div className="app">
      <h1>
        Cadwork 3d WebView (React){" "}
        <StatusPill bridge={bridge} error={error} />
      </h1>
      <p className="lede">
        Click "Load active elements" to
        fetch the current selection from <code>cadwork 3d</code>; click any row to activate
        that element and zoom to it.
      </p>

      <div className="row">
        <button disabled={!bridge || loading} onClick={handleLoad}>
          {loading ? "Loading…" : "Load active elements"}
        </button>
      </div>

      <ElementList elements={elements} onClick={handleClick} />
    </div>
  );
}

function StatusPill({
  bridge,
  error,
}: {
  bridge: unknown;
  error: Error | null;
}) {
  if (error) {
    return (
      <span className="status error" title={error.message}>
        bridge error
      </span>
    );
  }
  if (!bridge) return <span className="status">connecting…</span>;
  return <span className="status ready">bridge ready</span>;
}

function ElementList({
  elements,
  onClick,
}: {
  elements: BuildingElement[] | null;
  onClick: (id: number) => void;
}) {
  if (elements === null) {
    return (
      <ul className="elements">
        <li className="empty">No elements loaded yet.</li>
      </ul>
    );
  }
  if (elements.length === 0) {
    return (
      <ul className="elements">
        <li className="empty">
          No active elements in the current cadwork selection.
        </li>
      </ul>
    );
  }
  return (
    <ul className="elements">
      {elements.map((el) => (
        <li key={el.id} onClick={() => onClick(el.id)}>
          <span className="id">#{el.id}</span>
          <span className="name">{el.name || "(unnamed)"}</span>
        </li>
      ))}
    </ul>
  );
}
