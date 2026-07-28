FROM apify/actor-node-playwright-chrome:20
COPY --chown=myuser package*.json ./
RUN npm install --include=dev --audit=false && npm cache clean --force
COPY --chown=myuser . ./
CMD npm start --silent

