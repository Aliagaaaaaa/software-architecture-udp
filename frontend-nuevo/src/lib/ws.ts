// src/lib/ws.ts
import ReconnectingWebSocket from "reconnecting-websocket";

const WS_URL = "ws://4.228.228.99:8000"; // Cambia si usas otro puerto/gateway

export const socket = new ReconnectingWebSocket(WS_URL);

socket.addEventListener("open", () => {
  console.log("🔌 Conectado al WebSocket Gateway");
});

socket.addEventListener("close", () => {
  console.log("❌ Conexión WebSocket cerrada");
});

socket.addEventListener("error", (err) => {
  console.error("⚠️ Error WebSocket:", err);
});

export function sendMessage(msg: string) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(msg);
  } else {
    console.warn("WebSocket no está listo. Intentando luego...");
  }
}