FROM node:18
WORKDIR /src/hilsim-webapp
COPY package*.json ./
RUN npm install
COPY . .
ENV PORT=3000
ENV CHOKIDAR_USEPOLLING=true
EXPOSE 3000
CMD ["npm", "start"]