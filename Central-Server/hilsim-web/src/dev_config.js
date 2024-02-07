/**
 * Due to the nature of this project, we are interested in performing tests on seperate computers on the same network. Because of this, we
 * spin up an http tunnel through Ngrok. Because the URL of the tunnel is random every time, we need to be able to update the target URL
 * on both the frontend and the datastreamer. The datastreamer handles this through its own `dynamic_url.py` service, this (the frontend)
 * handles dynamic URLs here.
 * 
 * To edit the dynamic url, edit `server_url.txt` on the active_server_url branch (https://github.com/ISSUIUC/ISS_HILSIM/tree/active_server_url)
*/

const server_url_request = await fetch("https://raw.githubusercontent.com/ISSUIUC/ISS_HILSIM/active_server_url/server_url.txt");
const text = await server_url_request.text();

export const api_url = text;