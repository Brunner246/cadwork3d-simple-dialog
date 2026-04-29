// Typed wrapper around the QWebChannel-exposed `cadwork` QObject.
//
// The Python side (adapters/driving/web_bridge.py) registers a QObject
// named "cadwork" on a QWebChannel and injects qwebchannel.js at
// DocumentCreation, which sets `window.QWebChannel` and
// `window.qt.webChannelTransport`. This module hides the channel setup
// behind a single promise and a React hook, so components can just
// await `getCadworkBridge()` or read `useCadwork()`.

import { useEffect, useState } from "react";

export interface BuildingElement {
  id: number;
  name: string;
}

export interface CadworkBridge {
  getActiveElements(): Promise<BuildingElement[]>;
  activateAndZoom(id: number): void;
}

interface QtWebChannelTransport {
  send(message: string): void;
  onmessage?: (event: { data: string }) => void;
}

interface QWebChannelCtor {
  new (
    transport: QtWebChannelTransport,
    callback: (channel: { objects: Record<string, unknown> }) => void,
  ): unknown;
}

declare global {
  interface Window {
    qt?: { webChannelTransport: QtWebChannelTransport };
    QWebChannel?: QWebChannelCtor;
  }
}

let bridgePromise: Promise<CadworkBridge> | null = null;

export function getCadworkBridge(): Promise<CadworkBridge> {
  if (bridgePromise) return bridgePromise;
  bridgePromise = new Promise((resolve, reject) => {
    const transport = window.qt?.webChannelTransport;
    const Ctor = window.QWebChannel;
    if (!transport || !Ctor) {
      reject(
        new Error(
          "QWebChannel transport is not available. This page must run inside " +
            "QWebEngineView so qwebchannel.js gets injected at document creation.",
        ),
      );
      return;
    }
    new Ctor(transport, (channel) => {
      const cadwork = channel.objects.cadwork as CadworkBridge | undefined;
      if (!cadwork) {
        reject(new Error("`cadwork` object missing from QWebChannel"));
        return;
      }
      resolve(cadwork);
    });
  });
  return bridgePromise;
}

export function useCadwork(): {
  bridge: CadworkBridge | null;
  error: Error | null;
} {
  const [bridge, setBridge] = useState<CadworkBridge | null>(null);
  const [error, setError] = useState<Error | null>(null);
  useEffect(() => {
    let cancelled = false;
    getCadworkBridge()
      .then((b) => {
        if (!cancelled) setBridge(b);
      })
      .catch((e) => {
        if (!cancelled) setError(e instanceof Error ? e : new Error(String(e)));
      });
    return () => {
      cancelled = true;
    };
  }, []);
  return { bridge, error };
}
