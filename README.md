# HILSIM Server
The Remote Testing Platform of the Future

## Development
### Installing dependencies
`TODO: Remove unused dependencies`

To install all **Python** dependencies, run `pip install -r requirements.txt` in the root of this directory.

To install all **Javascript** dependencies, run `npm i` in the `/Central-Server/hilsim-web` directory.

### Running the server
#### Windows
For windows development, starting up the development server is as easy as running the `dev.ps1` script from any PowerShell environment. If you get the following error: 
```
...\dev.ps1 cannot be loaded because running scripts is disabled on this system. ...
```

You can by pass this warning by opening an administrator terminal, using the command `Set-ExecutionPolicy RemoteSigned`, running the script, then setting the policy back (if you wish.)

To build/deploy the application for production, instead run `prod.ps1`

#### Unix-like systems (And if the script doesn't work)
You can always start up the individual components of the server with the associated script in `/scripts`:

`scripts/run_api.py [dev|prod]` -- Starts the API server on `localhost:443`, with the development server if the environment is `dev`.
`scripts/run_webserver.py [dev|prod]` -- If the environment is `dev`, start the CRA server on `localhost:3000` with hot reloads. If environment is `prod`, build the site as a static page and host on `localhost:8080`
`scripts/run_nginx.py [dev|prod]` -- Points `localhost:80/* --> localhost:8080` and `localhost:80/api/* --> localhost:433/*` on `prod`. Points `localhost/* --> localhost:3000` and `localhost/api/* --> localhost:433/*` on `dev`. 

#### Both systems:
After running the service locally, you can port forward port `80` to the web to act as expected. If you are using `ngrok`, the command is `ngrok http 80`
### Development with hot-reload
If you have run the server in the `dev` environment, all aspects of the running app hot reload. For the webapp portion of the program, this means that any change made to the page will be immediately visible on `http://localhost`. For the API, this means that all of your changes will be applied the next time the API is called.

##### Nginx issues

Sometimes, Nginx will keep running even if the process that started it is killed. Usually, Nginx processes are killed with the `nginx -s stop` command.

To force-kill all nginx process (if `-s stop` stop doesn't work): `taskkill /f /IM nginx.exe`

# test