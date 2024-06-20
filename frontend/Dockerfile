FROM node:22.1.0-alpine

WORKDIR /app

# Копирование package.json и package-lock.json
COPY package*.json ./

# Установка переменной окружения для увеличения памяти
ENV NODE_OPTIONS="--max-old-space-size=4096"

# Silent clean install of npm
RUN npm ci --silent

# Установка глобального пакета react-scripts
RUN npm install -g react-scripts@3.4.1

# Копирование остальных файлов
COPY . .

# Сборка приложения
RUN npm run build

# Экспонирование порта
EXPOSE 8080

# Запуск приложения
CMD ["npm", "run", "serve"]
