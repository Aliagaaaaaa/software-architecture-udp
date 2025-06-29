import { useEffect, useRef } from "react"

export function useSocket(onMessage: (msg: string) => void) {
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    socketRef.current = new WebSocket("ws://4.228.228.99:3001")

    socketRef.current.onopen = () => {
      console.log("WebSocket conectado.")
    }

    socketRef.current.onmessage = (event) => {
      onMessage(event.data)
    }

    socketRef.current.onerror = (error) => {
      console.error("Error en WebSocket:", error)
    }

    socketRef.current.onclose = () => {
      console.log("WebSocket cerrado.")
    }

    return () => {
      socketRef.current?.close()
    }
  }, [onMessage])

  const sendMessage = (message: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(message)
    } else {
      console.warn("WebSocket no está listo.")
    }
  }

  return { sendMessage }
}