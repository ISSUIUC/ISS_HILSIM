# HILSIM Server
The Remote Testing Platform of the Future

## Development


### Running the server
The HILSIM Server services are run as seperate Docker containers. For more information on Docker, read here: https://www.docker.com/

In short, Docker containers allow us to spin up platform-independent instances of our services, which means that our code will function regardless of whether you are on Mac or Windows.

To run the server, first, install **Docker**. If you have **Docker Desktop**, you can skip this step.

To **build** the image, we use `docker-compose`. To build the development instance, run the following command:

```docker-compose -f .\compose.yml build```

Then, after it builds, run it with

```docker-compose -f .\compose.yml up```

The equivalent holds for a production container, except the yml file is instead `.\compose.prod.yml`:

```
docker-compose -f .\compose.prod.yml build
docker-compose -f .\compose.prod.yml up
```

### Development with hot-reload
If you have run the server in the `dev` environment, all aspects of the running app hot reload. For the webapp portion of the program, this means that any change made to the page will be visible on `http://localhost` without a re-build. For the API, this means that all of your changes will be applied the next time the API is called.

Keep in mind that in the development container, it takes a couple seconds for the hot reload to take effect, especially on the first reload. If you wish to immediately see results, you can instead run `npm run coldstart` in `Central-Server/hilsim-web`. However, this will not run the API or the reverse proxy, so the server will start at `http://localhost:3000`.

Keep in mind that the dev environment takes some time to spin up, it is usually not stuck but thinking a bit!

##### Nginx issues

Sometimes, Nginx will keep running even if the process that started it is killed. Usually, Nginx processes are killed with the `nginx -s stop` command.

To force-kill all nginx process (if `-s stop` stop doesn't work): `taskkill /f /IM nginx.exe`