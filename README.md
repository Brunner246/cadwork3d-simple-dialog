# CadDialog — PyQt6 QWebEngineView + QWebChannel for cadwork 3d

> [!NOTE]
> Cadwork v2025 uses Qt 5.15.10

A minimal example showing how to embed a webpage in a PyQt6 dialog and
let the page drive cwapi3d. Two demo actions:

- **Get active element IDs** — calls `element_controller.get_active_identifiable_element_ids()`
  and returns the list to the page (awaitable from JS).
- **Zoom active** — calls `visualization_controller.zoom_active_elements()`
  in cadwork 3d (fire-and-forget).

The code is organised around a hexagonal (ports & adapters) architecture so the
seams between Qt, the domain, and cwapi3d are explicit and replaceable.

## Hexagonal layout

```
CadDialog/
  WebDialog.py                              composition root + entry points
  domain/                                   pure Python -- no Qt, no cwapi3d
    cadwork_port.py                           CadworkPort (Protocol) -- driven port
    cadwork_service.py                        CadworkService -- application service (use cases)
  adapters/
    driving/                                primary adapters (drive the domain)
      web_bridge.py                           QObject with @pyqtSlot, holds a CadworkService
      web_dialog.py                           QDialog hosts QWebEngineView + WebBridge + QWebChannel
    driven/                                 secondary adapters (driven by the domain)
      cwapi3d_adapter.py                      production CadworkPort impl (cwapi3d)
      fake_cadwork_adapter.py                 standalone CadworkPort impl (prints + canned data)
  tests/
    test_cadwork_service.py                 exercises the seam with the fake adapter
  assets/
    index.html                              embedded page (replace with anything)
  web/                                      optional React + Vite UI (alternative to assets/)
    src/
      main.tsx                                React 19 entry
      App.tsx                                 element list + click-to-zoom
      cadwork.ts                              typed QWebChannel bridge + useCadwork() hook
      index.css
    index.html                              Vite entry (loads /src/main.tsx)
    vite.config.ts                          base: "./" so file:// loads work
    package.json                            dev/build scripts
```

Dependency rule: `adapters/*` may import from `domain/*`; `domain/*`
imports nothing from this project except other `domain/` modules. The
domain has no Qt and no cwapi3d.

## Running

### Standalone (dev laptop, no cadwork)

```
uv sync
uv run python WebDialog.py
```

The dialog opens on `assets/index.html`. Without cadwork, the bridge is
backed by `FakeCadworkAdapter`.

### Inside cadwork 3d

cadwork owns the Qt event loop, so don't create a `QApplication`:

```python
from WebDialog import run_plugin
dialog = run_plugin()
```

cadwork 2026 embeds its own Python 3.14 with PyQt6 already on the
import path, **but the bundled PyQt6 has no `QtWebEngine*`.


### React UI (Vite + TypeScript)

The static `assets/index.html` is the default. A second, fully-equivalent
UI lives under `web/` as a Vite + React + TypeScript project, talking
to the same `WebBridge` over QWebChannel. `web/src/cadwork.ts` exposes a
typed `getCadworkBridge()` promise and a `useCadwork()` React hook;
`BuildingElement` is mirrored as a TS interface so the page never
hand-rolls JSON shapes.

Which UI `WebDialog` loads is controlled by the `CADWORK_UI` env var,
resolved in `adapters/driving/web_dialog.py:_resolve_ui_url`:

| `CADWORK_UI`               | UI loaded                            |
|----------------------------|--------------------------------------|
| unset / `static` (default) | `assets/index.html`                  |
| `react`                    | `web/dist/index.html` (built bundle) |
| `http://…` or `https://…`  | URL                                  |


#### Install React dependencies:

```
cd web
npm install
```

Requires Node.js ≥ 20.

#### Production-style: build, then load from disk

```powershell
cd web; npm run build; cd ..
$env:CADWORK_UI = "react"
uv run python WebDialog.py
```

#### Dev with HMR (two terminals)

Terminal 1 — Vite dev server:

```
cd web
npm run dev
```

Terminal 2 — point `WebDialog` at the dev server:

```powershell
$env:CADWORK_UI = "http://127.0.0.1:5173"
uv run python WebDialog.py
```

### Tests

```
uv run pytest
```
