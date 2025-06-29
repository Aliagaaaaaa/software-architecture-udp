import WebSocket, { WebSocketServer } from "ws";
import net from "net";

const WS_PORT = 3001;
const TCP_HOST = "soa-bus"; // nombre del servicio en Docker
const TCP_PORT = 8000;

const wss = new WebSocketServer({ port: WS_PORT }, () => {
  console.log(`✅ Gateway WebSocket iniciado en ws://4.228.228.99:${WS_PORT}`);
});

wss.on("connection", (ws) => {
  console.log("🔌 Cliente WebSocket conectado");

  ws.on("message", (message) => {
    const raw = message.toString();
    console.log("➡️ Mensaje recibido del cliente:", raw);

    try {
      const mensajeTCP = buildMessage(raw);

      console.log("📨 Enviando al bus:", mensajeTCP);
      enviarAlBus(mensajeTCP, (respuesta) => {
        console.log("⬅️ Respuesta del bus:", respuesta);
        ws.send(respuesta);
      });
    } catch (err) {
      console.error("❌ Error procesando mensaje:", err);
      ws.send("ERROR_FORMATO");
    }
  });

  ws.on("close", () => {
    console.log("🔌 Cliente WebSocket desconectado");
  });

  ws.on("error", (err) => {
    console.error("❌ Error de WebSocket:", err);
  });
});

function buildMessage(raw) {
  const longitud = (raw).length;
  const longitudStr = longitud.toString().padStart(5, "0");
  return longitudStr + raw;
}

function enviarAlBus(mensaje, callback) {
  const client = new net.Socket();

  let respuesta = "";
  client.connect(TCP_PORT, TCP_HOST, () => {
    client.write(mensaje);
  });

  client.on("data", (data) => {
    respuesta += data.toString();
  });

  client.on("end", () => {
    callback(respuesta);
  });

  client.on("error", (err) => {
    console.error("🚨 Error en conexión TCP:", err.message);
    callback("ERROR_TCP");
  });
}