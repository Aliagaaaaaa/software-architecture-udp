# Usa Node.js liviano
FROM node:20-alpine

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de dependencias
COPY package.json package-lock.json* ./

# Instala dependencias
RUN npm install

# Copia todo el resto del frontend
COPY . .

# Expone el puerto por defecto de Vite
EXPOSE 5173

# Comando por defecto: levantar en modo dev accesible desde fuera
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]