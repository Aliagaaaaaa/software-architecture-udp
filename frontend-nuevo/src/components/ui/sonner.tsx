import { Toaster as Sonner } from "sonner"

const Toaster = () => {
  return (
    <Sonner
      theme="light"
      position="bottom-right"
      expand={true}
      richColors={true}
      closeButton={true}
      style={{
        zIndex: 9999,
        position: "fixed",
      }}
    />
  )
}

export { Toaster }